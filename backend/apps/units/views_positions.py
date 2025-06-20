# backend/apps/units/views_positions.py
"""
Updated Position views with force assignment capability
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Position, UserPosition
from .serializers import (
    PositionListSerializer, PositionDetailSerializer,
    UserPositionSerializer, UserPositionCreateSerializer,
    PositionCreateUpdateSerializer
)
from apps.users.views import IsAdminOrReadOnly
from datetime import datetime

from ..users.models import User


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for Position management"""
    queryset = Position.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = [
        'role', 'unit', 'is_active', 'is_vacant',
        'role__category', 'role__is_command_role'
    ]
    search_fields = ['title', 'role__name', 'unit__name']
    ordering = ['unit__name', 'role__sort_order']

    def get_serializer_class(self):
        if self.action == 'list':
            return PositionListSerializer
        elif self.action in ['assign', 'vacate']:
            return UserPositionCreateSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PositionCreateUpdateSerializer
        return PositionDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign(self, request, pk=None):
        """Assign a user to this position"""
        position = self.get_object()

        # Get user
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)

        # Check if force assignment is requested
        force_assign = request.data.get('force', False)

        # Validate requirements
        requirement_failures = []

        # Check rank requirements
        if not force_assign:
            if position.min_rank and user.current_rank:
                if user.current_rank.tier < position.min_rank.tier:
                    requirement_failures.append({
                        'type': 'rank_below_minimum',
                        'message': f"User's rank ({user.current_rank.abbreviation}) is below minimum required rank ({position.min_rank.abbreviation})",
                        'user_value': user.current_rank.abbreviation,
                        'required_value': position.min_rank.abbreviation
                    })

            if position.max_rank and user.current_rank:
                if user.current_rank.tier > position.max_rank.tier:
                    requirement_failures.append({
                        'type': 'rank_above_maximum',
                        'message': f"User's rank ({user.current_rank.abbreviation}) is above maximum allowed rank ({position.max_rank.abbreviation})",
                        'user_value': user.current_rank.abbreviation,
                        'required_value': position.max_rank.abbreviation
                    })

            # Check if user has a rank at all
            if not user.current_rank and (position.min_rank or position.max_rank):
                requirement_failures.append({
                    'type': 'no_rank',
                    'message': "User has no assigned rank",
                    'user_value': 'None',
                    'required_value': 'Any rank'
                })

            # Check time in service
            if position.role and position.role.min_time_in_service > 0:
                days_in_service = (timezone.now() - user.join_date).days if user.join_date else 0
                if days_in_service < position.role.min_time_in_service:
                    requirement_failures.append({
                        'type': 'insufficient_time_in_service',
                        'message': f"User needs {position.role.min_time_in_service - days_in_service} more days in service",
                        'user_value': f"{days_in_service} days",
                        'required_value': f"{position.role.min_time_in_service} days"
                    })

            # Check time in grade
            if position.role and position.role.min_time_in_grade > 0 and user.current_rank:
                # This would require tracking when rank was assigned
                # For now, we'll skip this check
                pass

            # Check branch restrictions
            if position.role and position.role.allowed_branches.exists():
                if not user.branch or user.branch not in position.role.allowed_branches.all():
                    allowed_branches = ", ".join([b.name for b in position.role.allowed_branches.all()])
                    requirement_failures.append({
                        'type': 'branch_restriction',
                        'message': f"User's branch is not allowed for this role",
                        'user_value': user.branch.name if user.branch else 'None',
                        'required_value': allowed_branches
                    })

            # Check for flight qualification if required
            if position.requires_flight_qualification:
                # This would check for aviation certificates
                # For now, we'll add a placeholder
                requirement_failures.append({
                    'type': 'flight_qualification_required',
                    'message': "Position requires aviation qualifications",
                    'user_value': 'Not qualified',
                    'required_value': 'Aviation qualified'
                })

            # If there are requirement failures and not forcing, return error
            if requirement_failures:
                return Response({
                    'error': 'User does not meet position requirements',
                    'requirement_failures': requirement_failures,
                    'can_force': True
                }, status=status.HTTP_400_BAD_REQUEST)

        # Create assignment data
        assignment_data = {
            'user': user.id,
            'position': position.id,
            'status': request.data.get('status', 'active'),
            'assignment_type': request.data.get('assignment_type', 'primary'),
            'effective_date': request.data.get('effective_date'),
            'order_number': request.data.get('order_number'),
            'notes': request.data.get('notes', '')
        }

        # Add force assignment note if applicable
        if force_assign and requirement_failures:
            force_note = f"\n\nFORCE ASSIGNED by {request.user.username} on {datetime.now().strftime('%Y-%m-%d %H:%M')}. Requirements bypassed:\n"
            for failure in requirement_failures:
                force_note += f"- {failure['message']}\n"
            assignment_data['notes'] = assignment_data['notes'] + force_note

        serializer = UserPositionCreateSerializer(
            data=assignment_data,
            context={'request': request}
        )

        # Override validation if force is true
        if force_assign:
            serializer.is_valid(raise_exception=False)
            # Manually create the assignment
            assignment = UserPosition.objects.create(
                user_id=user.id,
                position_id=position.id,
                status=assignment_data['status'],
                assignment_type=assignment_data['assignment_type'],
                effective_date=assignment_data.get('effective_date'),
                order_number=assignment_data.get('order_number'),
                notes=assignment_data['notes'],
                assigned_by=request.user
            )

            # Update position vacancy status
            if assignment.status == 'active' and assignment.assignment_type == 'primary':
                position.is_vacant = False
                position.save()

            return Response(
                UserPositionSerializer(assignment).data,
                status=status.HTTP_201_CREATED
            )
        else:
            if serializer.is_valid():
                assignment = serializer.save()

                # Update position vacancy status
                if assignment.status == 'active' and assignment.assignment_type == 'primary':
                    position.is_vacant = False
                    position.save()

                return Response(
                    UserPositionSerializer(assignment).data,
                    status=status.HTTP_201_CREATED
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def requirement_check(self, request, pk=None):
        """Check if a user meets requirements for this position"""
        position = self.get_object()
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)
        requirement_checks = []
        meets_all_requirements = True

        # Check rank requirements
        if position.min_rank:
            if user.current_rank and user.current_rank.tier >= position.min_rank.tier:
                requirement_checks.append({
                    'requirement': 'Minimum Rank',
                    'required': position.min_rank.abbreviation,
                    'user_has': user.current_rank.abbreviation,
                    'meets': True
                })
            else:
                requirement_checks.append({
                    'requirement': 'Minimum Rank',
                    'required': position.min_rank.abbreviation,
                    'user_has': user.current_rank.abbreviation if user.current_rank else 'No rank',
                    'meets': False
                })
                meets_all_requirements = False

        if position.max_rank:
            if user.current_rank and user.current_rank.tier <= position.max_rank.tier:
                requirement_checks.append({
                    'requirement': 'Maximum Rank',
                    'required': position.max_rank.abbreviation,
                    'user_has': user.current_rank.abbreviation,
                    'meets': True
                })
            else:
                requirement_checks.append({
                    'requirement': 'Maximum Rank',
                    'required': position.max_rank.abbreviation,
                    'user_has': user.current_rank.abbreviation if user.current_rank else 'No rank',
                    'meets': False
                })
                meets_all_requirements = False

        # Check time in service
        if position.role and position.role.min_time_in_service > 0:
            days_in_service = (timezone.now() - user.join_date).days if user.join_date else 0
            requirement_checks.append({
                'requirement': 'Time in Service',
                'required': f"{position.role.min_time_in_service} days",
                'user_has': f"{days_in_service} days",
                'meets': days_in_service >= position.role.min_time_in_service
            })
            if days_in_service < position.role.min_time_in_service:
                meets_all_requirements = False

        # Check branch
        if position.role and position.role.allowed_branches.exists():
            allowed_branches = [b.name for b in position.role.allowed_branches.all()]
            user_branch = user.branch.name if user.branch else 'None'
            requirement_checks.append({
                'requirement': 'Branch',
                'required': ', '.join(allowed_branches),
                'user_has': user_branch,
                'meets': user.branch in position.role.allowed_branches.all() if user.branch else False
            })
            if not user.branch or user.branch not in position.role.allowed_branches.all():
                meets_all_requirements = False

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'rank': user.current_rank.abbreviation if user.current_rank else None
            },
            'position': {
                'id': position.id,
                'title': position.display_title,
                'role': position.role.name if position.role else None
            },
            'meets_all_requirements': meets_all_requirements,
            'requirement_checks': requirement_checks
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def vacate(self, request, pk=None):
        """Vacate this position"""
        position = self.get_object()

        # End all active assignments
        active_assignments = position.assignments.filter(status='active')

        end_date = request.data.get('end_date', timezone.now())
        notes = request.data.get('notes', 'Position vacated')

        for assignment in active_assignments:
            assignment.status = 'ended'
            assignment.end_date = end_date
            assignment.notes = f"{assignment.notes}\n{notes}" if assignment.notes else notes
            assignment.save()

        # Update position status
        position.is_vacant = True
        position.save()

        return Response({
            'message': f'Position vacated. {active_assignments.count()} assignments ended.',
            'position_id': position.id,
            'is_vacant': position.is_vacant
        })

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get assignment history for this position"""
        position = self.get_object()

        assignments = position.assignments.select_related(
            'user', 'user__current_rank', 'assigned_by'
        ).order_by('-assignment_date')

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            assignments = assignments.filter(status=status_filter)

        limit = request.query_params.get('limit', 20)
        assignments = assignments[:int(limit)]

        serializer = UserPositionSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def chain_of_command(self, request, pk=None):
        """Get chain of command for this position"""
        position = self.get_object()

        # Get upward chain
        chain_up = []
        current = position.parent_position
        while current and len(chain_up) < 10:  # Limit depth
            chain_up.append(current)
            current = current.parent_position

        # Get downward chain
        chain_down = list(position.subordinate_positions.filter(is_active=True))

        return Response({
            'position': PositionListSerializer(position).data,
            'reports_to': PositionListSerializer(chain_up, many=True).data,
            'subordinates': PositionListSerializer(chain_down, many=True).data
        })