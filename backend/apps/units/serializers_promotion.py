# backend/apps/units/serializers_promotion.py
"""
Serializers for rank promotion requirements system
"""
from rest_framework import serializers
from .models_promotion import (
    PromotionRequirementType, RankPromotionRequirement,
    UserPromotionProgress, UserRankHistory, PromotionWaiver
)
from .models import Rank, Role
from .serializers import RankSerializer, RoleDetailSerializer
from apps.training.serializers import TrainingCertificateSerializer
from django.utils import timezone


class PromotionRequirementTypeSerializer(serializers.ModelSerializer):
    """Serializer for promotion requirement types"""

    class Meta:
        model = PromotionRequirementType
        fields = '__all__'


class RankPromotionRequirementSerializer(serializers.ModelSerializer):
    """Detailed serializer for rank promotion requirements"""

    requirement_type_details = PromotionRequirementTypeSerializer(
        source='requirement_type',
        read_only=True
    )
    position_role_details = RoleDetailSerializer(source='position_role', read_only=True)
    required_certification_details = TrainingCertificateSerializer(
        source='required_certification',
        read_only=True
    )

    class Meta:
        model = RankPromotionRequirement
        fields = '__all__'


class RequirementProgressSerializer(serializers.Serializer):
    """Serializer for individual requirement progress"""

    requirement_id = serializers.UUIDField()
    requirement_type = serializers.CharField()
    display_text = serializers.CharField()
    category = serializers.CharField()
    is_mandatory = serializers.BooleanField()
    requirement_group = serializers.CharField(allow_null=True)

    # Progress fields
    is_met = serializers.BooleanField()
    current_value = serializers.CharField()
    required_value = serializers.CharField()
    progress_percentage = serializers.FloatField()

    # Waiver fields
    is_waived = serializers.BooleanField(default=False)
    waiverable = serializers.BooleanField()
    waiver_details = serializers.DictField(required=False)

    # Additional context
    details = serializers.DictField(required=False)


class PromotionProgressSerializer(serializers.ModelSerializer):
    """Comprehensive promotion progress serializer"""

    next_rank_details = RankSerializer(source='next_rank', read_only=True)
    requirements_summary = serializers.SerializerMethodField()
    detailed_requirements = serializers.SerializerMethodField()
    time_estimates = serializers.SerializerMethodField()

    class Meta:
        model = UserPromotionProgress
        fields = [
            'id', 'user', 'next_rank', 'next_rank_details',
            'last_evaluation_date', 'overall_eligible', 'eligibility_percentage',
            'board_eligible', 'board_scheduled_date', 'board_completed_date',
            'board_result', 'requirements_summary', 'detailed_requirements',
            'time_estimates', 'notes'
        ]

    def get_requirements_summary(self, obj):
        """Get summary of requirements status"""
        if not obj.requirements_met:
            return {
                'total': 0,
                'met': 0,
                'pending': 0,
                'waived': 0
            }

        total = len(obj.requirements_met)
        met = sum(1 for met, _ in obj.requirements_met.values() if met)
        waived = len(obj.active_waivers)

        return {
            'total': total,
            'met': met,
            'pending': total - met,
            'waived': waived
        }

    def get_detailed_requirements(self, obj):
        """Get detailed requirement progress"""
        if not obj.next_rank:
            return []

        requirements = obj.next_rank.promotion_requirements.all().select_related(
            'requirement_type', 'position_role', 'required_certification'
        )

        detailed = []

        # Group requirements by category
        for req in requirements:
            req_id = str(req.id)

            # Get progress from cached results
            if req_id in obj.requirements_met:
                is_met, current_value = obj.requirements_met[req_id]
            else:
                is_met, current_value = False, 0

            # Check if waived
            is_waived = req_id in obj.active_waivers

            # Calculate progress percentage
            if isinstance(current_value, (int, float)) and req.value_required > 0:
                progress_percentage = min(100, (current_value / req.value_required) * 100)
            else:
                progress_percentage = 100.0 if is_met else 0.0

            # Build requirement details
            req_data = {
                'requirement_id': req.id,
                'requirement_type': req.requirement_type.evaluation_type,
                'display_text': req.display_text,
                'category': req.requirement_type.category,
                'is_mandatory': req.is_mandatory,
                'requirement_group': req.requirement_group,
                'is_met': is_met or is_waived,
                'current_value': str(current_value),
                'required_value': str(req.value_required),
                'progress_percentage': progress_percentage,
                'is_waived': is_waived,
                'waiverable': req.waiverable,
                'details': {}
            }

            # Add specific details based on requirement type
            if req.requirement_type.evaluation_type == 'certification_required':
                req_data['details']['certification'] = {
                    'name': req.required_certification.name if req.required_certification else None,
                    'abbreviation': req.required_certification.abbreviation if req.required_certification else None
                }
            elif req.requirement_type.evaluation_type in ['time_in_position', 'time_in_position_type']:
                req_data['details']['position'] = {
                    'role': req.position_role.name if req.position_role else req.position_category,
                    'days_required': req.value_required
                }

            detailed.append(req_data)

        # Sort by category and mandatory status
        detailed.sort(key=lambda x: (
            not x['is_mandatory'],
            x['category'],
            x['display_text']
        ))

        return detailed

    def get_time_estimates(self, obj):
        """Calculate estimated time to meet all requirements"""
        if not obj.next_rank or obj.overall_eligible:
            return None

        estimates = {
            'days_until_eligible': None,
            'estimated_eligibility_date': None,
            'blocking_requirements': []
        }

        # Find time-based requirements that aren't met
        requirements = obj.next_rank.promotion_requirements.filter(
            requirement_type__evaluation_type__in=[
                'time_in_service', 'time_in_grade', 'time_in_unit',
                'time_in_position', 'time_in_position_type'
            ]
        )

        max_days_needed = 0

        for req in requirements:
            req_id = str(req.id)
            if req_id in obj.requirements_met:
                is_met, current_value = obj.requirements_met[req_id]
                if not is_met and isinstance(current_value, (int, float)):
                    days_needed = req.value_required - current_value
                    if days_needed > max_days_needed:
                        max_days_needed = days_needed
                        estimates['blocking_requirements'].append({
                            'requirement': req.display_text,
                            'days_needed': days_needed
                        })

        if max_days_needed > 0:
            estimates['days_until_eligible'] = max_days_needed
            estimates['estimated_eligibility_date'] = (
                    timezone.now() + timezone.timedelta(days=max_days_needed)
            ).date()

        return estimates


class PromotionChecklistSerializer(serializers.Serializer):
    """Serializer for promotion checklist display"""

    current_rank = RankSerializer()
    next_rank = RankSerializer()
    overall_eligible = serializers.BooleanField()
    eligibility_percentage = serializers.FloatField()

    checklist = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of requirements in checklist format"
    )

    action_items = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of specific actions user needs to take"
    )

    time_estimate = serializers.DictField(
        help_text="Estimated timeline to eligibility"
    )


class UserRankHistorySerializer(serializers.ModelSerializer):
    """Serializer for rank history"""

    rank_details = RankSerializer(source='rank', read_only=True)
    promoted_by_username = serializers.ReadOnlyField(source='promoted_by.username')
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = UserRankHistory
        fields = '__all__'

    def get_duration_days(self, obj):
        """Calculate how long user held this rank"""
        end_date = obj.date_ended or timezone.now()
        return (end_date - obj.date_assigned).days


class PromotionWaiverSerializer(serializers.ModelSerializer):
    """Serializer for promotion waivers"""

    requirement_details = RankPromotionRequirementSerializer(
        source='requirement',
        read_only=True
    )
    waived_by_username = serializers.ReadOnlyField(source='waived_by.username')

    class Meta:
        model = PromotionWaiver
        fields = '__all__'


class CreatePromotionWaiverSerializer(serializers.ModelSerializer):
    """Serializer for creating promotion waivers"""

    class Meta:
        model = PromotionWaiver
        fields = ['user', 'requirement', 'reason', 'expiry_date']


class PromoteUserSerializer(serializers.Serializer):
    """Serializer for promoting a user"""

    user_id = serializers.UUIDField()
    new_rank_id = serializers.UUIDField()
    promotion_order = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    force = serializers.BooleanField(
        default=False,
        help_text="Force promotion even if requirements not met"
    )

    def validate(self, data):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Validate user
        try:
            user = User.objects.get(id=data['user_id'])
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        # Validate rank
        try:
            rank = Rank.objects.get(id=data['new_rank_id'])
            data['new_rank'] = rank
        except Rank.DoesNotExist:
            raise serializers.ValidationError("Rank not found")

        # Check if promotion is valid (going up in tiers)
        if user.current_rank and rank.tier <= user.current_rank.tier:
            if not data.get('force'):
                raise serializers.ValidationError(
                    "Cannot promote to same or lower rank without force flag"
                )

        # Check branch compatibility
        if user.branch and rank.branch != user.branch:
            raise serializers.ValidationError(
                "Cannot promote to rank from different branch"
            )

        return data