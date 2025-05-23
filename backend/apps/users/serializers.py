from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'discord_id', 'username', 'email', 'avatar_url', 'bio',
            'join_date', 'is_active', 'is_staff', 'is_admin', 'service_number',
            'current_rank', 'primary_unit', 'branch', 'background_image_url',
            'timezone', 'discord_notifications', 'email_notifications',
            'commission_stage', 'onboarding_status', 'recruit_status',
            'training_completion_date', 'application_date',
            'bit_completion_date', 'branch_application_date',
            'branch_induction_date', 'unit_assignment_date',
            'officer_candidate', 'warrant_officer_candidate'
        ]
        read_only_fields = ['id', 'discord_id', 'join_date', 'is_active', 'is_staff', 'is_admin']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'avatar_url', 'bio', 'service_number',
            'current_rank', 'primary_unit', 'branch', 'background_image_url',
            'timezone', 'commission_stage', 'recruit_status',
            'officer_candidate', 'warrant_officer_candidate'
        ]
        read_only_fields = ['id', 'service_number', 'current_rank', 'primary_unit', 'branch', 'commission_stage',
                            'recruit_status']


class UserSensitiveFieldsSerializer(serializers.ModelSerializer):
    """
    Serializer for updating sensitive user fields that require admin permissions
    """

    class Meta:
        model = User
        fields = [
            'current_rank',
            'primary_unit',
            'branch',
            'commission_stage',
            'recruit_status',
            'officer_candidate',
            'warrant_officer_candidate'
        ]


class DiscordTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['discord_id'] = user.discord_id
        token['username'] = user.username
        token['is_admin'] = user.is_admin
        token['is_staff'] = user.is_staff

        return token


class UserProfileSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'avatar_url', 'bio', 'join_date',
            'service_number', 'rank', 'unit', 'branch',
            'background_image_url', 'commission_stage', 'recruit_status',
        ]

    def get_rank(self, obj):
        if obj.current_rank:
            return {
                'id': obj.current_rank.id,
                'name': obj.current_rank.name,
                'abbreviation': obj.current_rank.abbreviation,
                'insignia_image_url': obj.current_rank.insignia_image_url
            }
        return None

    def get_unit(self, obj):
        if obj.primary_unit:
            return {
                'id': obj.primary_unit.id,
                'name': obj.primary_unit.name,
                'abbreviation': obj.primary_unit.abbreviation,
                'emblem_url': obj.primary_unit.emblem_url
            }
        return None

    def get_branch(self, obj):
        if obj.branch:
            return {
                'id': obj.branch.id,
                'name': obj.branch.name,
                'abbreviation': obj.branch.abbreviation,
                'logo_url': obj.branch.logo_url
            }
        return None


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive user profile serializer with all related data expanded
    """
    current_rank = serializers.SerializerMethodField()
    primary_unit = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    commission_stage = serializers.SerializerMethodField()
    mentor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'discord_id', 'username', 'email', 'avatar_url', 'bio',
            'join_date', 'last_login', 'is_active', 'is_staff', 'is_admin',
            'service_number', 'current_rank', 'primary_unit', 'branch',
            'background_image_url', 'timezone', 'discord_notifications',
            'email_notifications', 'commission_stage', 'onboarding_status',
            'recruit_status', 'training_completion_date', 'application_date',
            'bit_completion_date', 'branch_application_date',
            'branch_induction_date', 'unit_assignment_date',
            'officer_candidate', 'warrant_officer_candidate', 'mentor'
        ]

    def get_current_rank(self, obj):
        if obj.current_rank:
            return {
                'id': obj.current_rank.id,
                'name': obj.current_rank.name,
                'abbreviation': obj.current_rank.abbreviation,
                'tier': obj.current_rank.tier,
                'insignia_image_url': obj.current_rank.insignia_image_url,
                'description': obj.current_rank.description,
                'color_code': obj.current_rank.color_code,
                'is_officer': obj.current_rank.is_officer,
                'is_enlisted': obj.current_rank.is_enlisted,
                'is_warrant': obj.current_rank.is_warrant
            }
        return None

    def get_primary_unit(self, obj):
        if obj.primary_unit:
            return {
                'id': obj.primary_unit.id,
                'name': obj.primary_unit.name,
                'abbreviation': obj.primary_unit.abbreviation,
                'unit_type': obj.primary_unit.unit_type,
                'emblem_url': obj.primary_unit.emblem_url,
                'banner_image_url': obj.primary_unit.banner_image_url,
                'motto': obj.primary_unit.motto,
                'description': obj.primary_unit.description
            }
        return None

    def get_branch(self, obj):
        if obj.branch:
            return {
                'id': obj.branch.id,
                'name': obj.branch.name,
                'abbreviation': obj.branch.abbreviation,
                'logo_url': obj.branch.logo_url,
                'color_code': obj.branch.color_code,
                'description': obj.branch.description
            }
        return None

    def get_commission_stage(self, obj):
        if obj.commission_stage:
            return {
                'id': obj.commission_stage.id,
                'name': obj.commission_stage.name,
                'description': obj.commission_stage.description,
                'badge_image_url': obj.commission_stage.badge_image_url,
                'requirements': obj.commission_stage.requirements,
                'benefits': obj.commission_stage.benefits,
                'order_index': obj.commission_stage.order_index
            }
        return None

    def get_mentor(self, obj):
        # Get active mentor assignment
        from apps.onboarding.models import MentorAssignment
        mentor_assignment = MentorAssignment.objects.filter(
            recruit=obj,
            status='Active'
        ).select_related('mentor').first()

        if mentor_assignment and mentor_assignment.mentor:
            mentor = mentor_assignment.mentor
            return {
                'id': mentor.id,
                'username': mentor.username,
                'avatar_url': mentor.avatar_url,
                'rank': {
                    'abbreviation': mentor.current_rank.abbreviation,
                    'name': mentor.current_rank.name
                } if mentor.current_rank else None
            }
        return None