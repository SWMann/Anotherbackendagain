# backend/apps/units/views_promotion.py
"""
Views for rank promotion requirements system
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models_promotion import (
    PromotionRequirementType, RankPromotionRequirement,
    UserPromotionProgress, UserRankHistory, PromotionWaiver
)
from .serializers_promotion import (
    PromotionRequirementTypeSerializer, RankPromotionRequirementSerializer,
    PromotionProgressSerializer, PromotionChecklistSerializer,
    UserRankHistorySerializer, PromotionWaiverSerializer,
    CreatePromotionWaiverSerializer, PromoteUserSerializer
)
from .models import Rank
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


class PromotionRequirementTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for promotion requirement types"""
    queryset = PromotionRequirementType.objects.all()
    serializer_class = PromotionRequirementTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['category', 'evaluation_type']
    ordering = ['category', 'name']


class RankPromotionRequirementViewSet(viewsets.ModelViewSet):
    """ViewSet for rank-specific promotion requirements"""
    queryset = RankPromotionRequirement.objects.all()
    serializer_class = RankPromotionRequirementSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['rank', 'requirement_type', 'is_mandatory']
    ordering = ['rank__tier', 'display_order']

    @action(detail=False, methods=['get'])
    def by_rank(self, request):
        """Get all requirements for a specific rank"""
        rank_id = request.query_params.get('rank_id')
        if not rank_id:
            return Response(
                {'error': 'rank_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        requirements = self.queryset.filter(rank_id=rank_id)
        serializer = self.get_serializer(requirements, many=True)
        return Response(serializer.data)


class UserPromotionProgressView(APIView):
    """View for user's promotion progress"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id=None):
        """Get promotion progress for user"""
        # If no user_id provided, use current user
        if user_id:
            if not request.user.is_admin and str(request.user.id) != user_id:
                return Response(
                    {'error': 'You can only view your own promotion progress'},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user

        # Get or create promotion progress
        progress, created = UserPromotionProgress.objects.get_or_create(
            user=user,
            defaults={'next_rank': self._get_next_rank(user)}
        )

        # Update next rank if needed
        if not progress.next_rank or created:
            progress.next_rank = self._get_next_rank(user)
            progress.save()

        # Evaluate requirements
        progress.evaluate_requirements()

        # Serialize and return
        serializer = PromotionProgressSerializer(progress)
        return Response(serializer.data)

    def _get_next_rank(self, user):
        """Determine next eligible rank for user"""
        if not user.current_rank:
            # Get entry-level rank for user's branch
            if user.branch:
                return Rank.objects.filter(
                    branch=user.branch,
                    is_enlisted=True
                ).order_by('tier').first()
            return None

        # Get next rank in progression
        current_tier = user.current_rank.tier

        # Determine career track
        if user.current_rank.is_enlisted:
            # Check if eligible for warrant or officer
            if user.warrant_officer_candidate:
                next_rank = Rank.objects.filter(
                    branch=user.branch,
                    is_warrant=True,
                    tier__gt=current_tier
                ).order_by('tier').first()
            elif user.officer_candidate:
                next_rank = Rank.objects.filter(
                    branch=user.branch,
                    is_officer=True,
                    tier__gt=current_tier
                ).order_by('tier').first()
            else:
                # Continue enlisted progression
                next_rank = Rank.objects.filter(
                    branch=user.branch,
                    is_enlisted=True,
                    tier__gt=current_tier
                ).order_by('tier').first()
        else:
            # Continue in current track
            filters = {
                'branch': user.branch,
                'tier__gt': current_tier
            }
            if user.current_rank.is_warrant:
                filters['is_warrant'] = True
            else:
                filters['is_officer'] = True

            next_rank = Rank.objects.filter(**filters).order_by('tier').first()

        return next_rank


class PromotionChecklistView(APIView):
    """Simplified checklist view for career progression page"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get promotion checklist for current user"""
        user = request.user

        # Get promotion progress
        progress, created = UserPromotionProgress.objects.get_or_create(
            user=user,
            defaults={'next_rank': self._get_next_rank(user)}
        )

        if not progress.next_rank:
            return Response({
                'message': 'You have reached the highest rank available'
            })

        # Evaluate requirements
        progress.evaluate_requirements()

        # Build checklist
        checklist = []
        action_items = []

        requirements = progress.next_rank.promotion_requirements.all().select_related(
            'requirement_type', 'position_role', 'required_certification'
        ).order_by('display_order')

        for req in requirements:
            req_id = str(req.id)
            is_met = False
            current_value = 0
            progress_text = ""

            if req_id in progress.requirements_met:
                is_met, current_value = progress.requirements_met[req_id]

            # Build progress text based on requirement type
            eval_type = req.requirement_type.evaluation_type

            if eval_type in ['time_in_service', 'time_in_grade', 'time_in_unit']:
                if isinstance(current_value, (int, float)):
                    days_remaining = max(0, req.value_required - current_value)
                    progress_text = f"{current_value}/{req.value_required} days"
                    if not is_met:
                        action_items.append(
                            f"Wait {days_remaining} more days to meet {req.display_text}"
                        )

            elif eval_type == 'certification_required':
                progress_text = "✓ Earned" if is_met else "✗ Not Earned"
                if not is_met and req.required_certification:
                    action_items.append(
                        f"Earn {req.required_certification.name} certification"
                    )

            elif eval_type == 'deployments_count':
                progress_text = f"{current_value}/{req.value_required} deployments"
                if not is_met:
                    action_items.append(
                        f"Complete {req.value_required - current_value} more combat deployments"
                    )

            elif eval_type == 'leadership_time':
                if isinstance(current_value, (int, float)):
                    progress_text = f"{current_value}/{req.value_required} days"
                    if not is_met:
                        action_items.append(
                            f"Serve {req.value_required - current_value} more days in a leadership position"
                        )

            # Check if waived
            is_waived = req_id in progress.active_waivers

            checklist_item = {
                'requirement': req.display_text,
                'category': req.requirement_type.category,
                'is_met': is_met or is_waived,
                'is_waived': is_waived,
                'progress': progress_text,
                'is_mandatory': req.is_mandatory,
                'group': req.requirement_group
            }

            checklist.append(checklist_item)

        # Build response
        response_data = {
            'current_rank': {
                'name': user.current_rank.name if user.current_rank else None,
                'abbreviation': user.current_rank.abbreviation if user.current_rank else None,
                'tier': user.current_rank.tier if user.current_rank else None
            },
            'next_rank': {
                'name': progress.next_rank.name,
                'abbreviation': progress.next_rank.abbreviation,
                'tier': progress.next_rank.tier
            },
            'overall_eligible': progress.overall_eligible,
            'eligibility_percentage': progress.eligibility_percentage,
            'checklist': checklist,
            'action_items': action_items[:5],  # Top 5 action items
            'time_estimate': self._calculate_time_estimate(progress)
        }

        return Response(PromotionChecklistSerializer(response_data).data)

    def _get_next_rank(self, user):
        """Get next rank (same as in UserPromotionProgressView)"""
        # Implementation same as above
        view = UserPromotionProgressView()
        return view._get_next_rank(user)

    def _calculate_time_estimate(self, progress):
        """Calculate estimated time to promotion eligibility"""
        if progress.overall_eligible:
            return {
                'eligible_now': True,
                'message': "You meet all requirements for promotion!"
            }

        # Find longest time-based requirement
        max_days = 0
        blocking_requirement = None

        for req in progress.next_rank.promotion_requirements.filter(
                requirement_type__evaluation_type__in=[
                    'time_in_service', 'time_in_grade', 'time_in_unit'
                ]
        ):
            req_id = str(req.id)
            if req_id in progress.requirements_met:
                is_met, current_value = progress.requirements_met[req_id]
                if not is_met and isinstance(current_value, (int, float)):
                    days_needed = req.value_required - current_value
                    if days_needed > max_days:
                        max_days = days_needed
                        blocking_requirement = req.display_text

        if max_days > 0:
            return {
                'eligible_now': False,
                'days_until_eligible': max_days,
                'estimated_date': (timezone.now() + timezone.timedelta(days=max_days)).date(),
                'blocking_requirement': blocking_requirement
            }

        return {
            'eligible_now': False,
            'message': "Complete all non-time based requirements"
        }


class PromoteUserView(APIView):
    """View for promoting users"""
    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def post(self, request):
        """Promote a user to a new rank"""
        serializer = PromoteUserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        new_rank = serializer.validated_data['new_rank']
        force = serializer.validated_data.get('force', False)

        # Check promotion eligibility unless forced
        if not force:
            progress, _ = UserPromotionProgress.objects.get_or_create(
                user=user,
                defaults={'next_rank': new_rank}
            )
            progress.evaluate_requirements()

            if not progress.overall_eligible:
                return Response({
                    'error': 'User does not meet all promotion requirements',
                    'eligible': False,
                    'eligibility_percentage': progress.eligibility_percentage,
                    'missing_requirements': [
                        req for req, (met, _) in progress.requirements_met.items()
                        if not met
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)

        # End current rank in history
        if user.current_rank:
            current_history = UserRankHistory.objects.filter(
                user=user,
                rank=user.current_rank,
                date_ended__isnull=True
            ).first()

            if current_history:
                current_history.date_ended = timezone.now()
                current_history.save()

        # Create new rank history entry
        UserRankHistory.objects.create(
            user=user,
            rank=new_rank,
            date_assigned=timezone.now(),
            promoted_by=request.user,
            promotion_order=serializer.validated_data.get('promotion_order', ''),
            notes=serializer.validated_data.get('notes', '')
        )

        # Update user's current rank
        user.current_rank = new_rank
        user.save()

        # Reset promotion progress
        UserPromotionProgress.objects.filter(user=user).delete()

        return Response({
            'message': f'Successfully promoted {user.username} to {new_rank.name}',
            'user_id': user.id,
            'new_rank': {
                'id': new_rank.id,
                'name': new_rank.name,
                'abbreviation': new_rank.abbreviation,
                'tier': new_rank.tier
            }
        })


class RankHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing rank history"""
    queryset = UserRankHistory.objects.all()
    serializer_class = UserRankHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'rank']
    ordering = ['-date_assigned']

    def get_queryset(self):
        """Filter based on user permissions"""
        if self.request.user.is_admin:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class PromotionWaiverViewSet(viewsets.ModelViewSet):
    """ViewSet for promotion waivers"""
    queryset = PromotionWaiver.objects.all()
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['user', 'requirement', 'is_active']
    ordering = ['-waiver_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePromotionWaiverSerializer
        return PromotionWaiverSerializer

    def perform_create(self, serializer):
        waiver = serializer.save(waived_by=self.request.user)

        # Update user's promotion progress
        progress, _ = UserPromotionProgress.objects.get_or_create(
            user=waiver.user
        )
        if str(waiver.requirement.id) not in progress.active_waivers:
            progress.active_waivers.append(str(waiver.requirement.id))
            progress.save()

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a waiver"""
        waiver = self.get_object()
        waiver.is_active = False
        waiver.save()

        # Update user's promotion progress
        progress = UserPromotionProgress.objects.filter(user=waiver.user).first()
        if progress and str(waiver.requirement.id) in progress.active_waivers:
            progress.active_waivers.remove(str(waiver.requirement.id))
            progress.save()

        return Response({'message': 'Waiver revoked successfully'})