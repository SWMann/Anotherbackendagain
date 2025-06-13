# backend/apps/units/views_positions.py
"""
Updated Position views to work with new structure
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Position, UserPosition
from .serializers import (
    PositionListSerializer, PositionDetailSerializer,
    UserPositionSerializer, UserPositionCreateSerializer
)
from apps.users.views import IsAdminOrReadOnly

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

        # Create assignment data
        assignment_data = {
            'user': user.id,
            'position': position.id,
            'status': request.data.get('status', 'active'),
            'assignment_type': request.data.get('assignment_type', 'primary'),
            'effective_date': request.data.get('effective_date'),
            'order_number': request.data.get('order_number'),
            'notes': request.data.get('notes')
        }

        serializer = UserPositionCreateSerializer(
            data=assignment_data,
            context={'request': request}
        )

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
