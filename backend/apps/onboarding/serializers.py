# backend/apps/onboarding/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Application, ApplicationWaiverType, ApplicationWaiver,
    ApplicationProgress, ApplicationComment, ApplicationInterview,
    UserOnboardingProgress, MentorAssignment, ApplicationStatus
)
from apps.units.models import Branch, Unit, RecruitmentSlot, Role
from apps.units.serializers import BranchSerializer, UnitListSerializer, RoleDetailSerializer

User = get_user_model()


class ApplicationWaiverTypeSerializer(serializers.ModelSerializer):
    """Serializer for waiver/acknowledgment types"""

    class Meta:
        model = ApplicationWaiverType
        fields = [
            'id', 'code', 'title', 'description', 'content',
            'is_required', 'order', 'waiver_type'
        ]


class ApplicationWaiverSerializer(serializers.ModelSerializer):
    """Serializer for tracking waiver acceptance"""
    waiver_type_details = ApplicationWaiverTypeSerializer(source='waiver_type', read_only=True)

    class Meta:
        model = ApplicationWaiver
        fields = [
            'id', 'application', 'waiver_type', 'waiver_type_details',
            'accepted', 'accepted_at', 'ip_address', 'user_agent'
        ]
        read_only_fields = ['accepted_at']


class ApplicationProgressSerializer(serializers.ModelSerializer):
    """Serializer for application progress tracking"""
    next_step = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationProgress
        fields = [
            'id', 'application', 'basic_info_completed', 'branch_selected',
            'primary_unit_selected', 'secondary_unit_selected', 'track_selected',
            'position_selected', 'experience_completed', 'role_specific_completed',
            'waivers_completed', 'current_step', 'last_saved_at',
            'completion_percentage', 'next_step'
        ]
        read_only_fields = ['completion_percentage', 'last_saved_at']

    def get_next_step(self, obj):
        """Determine the next incomplete step"""
        steps = [
            (2, 'basic_info', obj.basic_info_completed),
            (3, 'branch', obj.branch_selected),
            (4, 'primary_unit', obj.primary_unit_selected),
            (5, 'secondary_unit', obj.secondary_unit_selected),
            (6, 'track', obj.track_selected),
            (7, 'position', obj.position_selected),
            (8, 'experience', obj.experience_completed),
            (9, 'role_specific', obj.role_specific_completed),
            (10, 'waivers', obj.waivers_completed),
        ]

        for step_num, step_name, completed in steps:
            if not completed:
                return {
                    'step': step_num,
                    'name': step_name,
                    'completed': False
                }

        return {
            'step': 11,
            'name': 'submit',
            'completed': True
        }


class ApplicationCommentSerializer(serializers.ModelSerializer):
    """Serializer for application comments"""
    author_name = serializers.ReadOnlyField(source='author.username')
    author_rank = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationComment
        fields = [
            'id', 'application', 'author', 'author_name', 'author_rank',
            'comment', 'is_visible_to_applicant', 'created_at'
        ]
        read_only_fields = ['author', 'created_at']

    def get_author_rank(self, obj):
        if obj.author.current_rank:
            return obj.author.current_rank.abbreviation
        return None


class ApplicationInterviewSerializer(serializers.ModelSerializer):
    """Serializer for interview scheduling"""
    interviewer_name = serializers.ReadOnlyField(source='interviewer.username', default=None)
    scheduled_by_name = serializers.ReadOnlyField(source='scheduled_by.username', default=None)

    class Meta:
        model = ApplicationInterview
        fields = [
            'id', 'application', 'scheduled_at', 'scheduled_by', 'scheduled_by_name',
            'interviewer', 'interviewer_name', 'interview_type', 'status',
            'completed_at', 'interview_notes', 'recommendation'
        ]


class RecruitmentSlotSerializer(serializers.ModelSerializer):
    """Serializer for recruitment slots"""
    role_details = RoleDetailSerializer(source='role', read_only=True)
    unit_name = serializers.ReadOnlyField(source='unit.name')
    unit_abbreviation = serializers.ReadOnlyField(source='unit.abbreviation')

    class Meta:
        model = RecruitmentSlot
        fields = [
            'id', 'unit', 'unit_name', 'unit_abbreviation', 'role', 'role_details',
            'career_track', 'total_slots', 'filled_slots', 'reserved_slots',
            'available_slots', 'is_active', 'notes'
        ]


class ApplicationListSerializer(serializers.ModelSerializer):
    """List view serializer for applications"""
    branch_name = serializers.ReadOnlyField(source='branch.name', default=None)
    primary_unit_name = serializers.ReadOnlyField(source='primary_unit.name', default=None)
    selected_role_name = serializers.ReadOnlyField(source='selected_role.name', default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'application_number', 'discord_username', 'first_name',
            'last_name', 'branch', 'branch_name', 'primary_unit',
            'primary_unit_name', 'career_track', 'selected_role_name',
            'status', 'status_display', 'submitted_at', 'created_at'
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for full application data"""
    branch_details = BranchSerializer(source='branch', read_only=True)
    primary_unit_details = serializers.SerializerMethodField()
    secondary_unit_details = serializers.SerializerMethodField()
    selected_recruitment_slot_details = RecruitmentSlotSerializer(source='selected_recruitment_slot', read_only=True)
    waivers = ApplicationWaiverSerializer(many=True, read_only=True)
    progress = ApplicationProgressSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    interviews = ApplicationInterviewSerializer(many=True, read_only=True)
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username', default=None)
    referrer_name = serializers.ReadOnlyField(source='referrer.username', default=None)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = [
            'application_number', 'user', 'discord_id', 'started_at',
            'submitted_at', 'reviewed_at', 'decision_at',
            'discord_notification_sent', 'discord_notification_sent_at'
        ]

    def get_primary_unit_details(self, obj):
        if obj.primary_unit:
            return {
                'id': obj.primary_unit.id,
                'name': obj.primary_unit.name,
                'abbreviation': obj.primary_unit.abbreviation,
                'unit_type': obj.primary_unit.unit_type,
                'emblem_url': obj.primary_unit.emblem_url
            }
        return None

    def get_secondary_unit_details(self, obj):
        if obj.secondary_unit:
            return {
                'id': obj.secondary_unit.id,
                'name': obj.secondary_unit.name,
                'abbreviation': obj.secondary_unit.abbreviation,
                'unit_type': obj.secondary_unit.unit_type,
                'emblem_url': obj.secondary_unit.emblem_url
            }
        return None

    def get_comments(self, obj):
        # Filter comments based on user permissions
        request = self.context.get('request')
        if request and request.user.is_admin:
            comments = obj.comments.all()
        else:
            comments = obj.comments.filter(is_visible_to_applicant=True)
        return ApplicationCommentSerializer(comments, many=True).data


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating application during the flow"""

    class Meta:
        model = Application
        fields = [
            'discord_username', 'discord_discriminator', 'email',
            'first_name', 'last_name', 'date_of_birth', 'timezone', 'country',
            'branch', 'primary_unit', 'secondary_unit', 'career_track',
            'selected_recruitment_slot', 'alternate_recruitment_slot_1',
            'alternate_recruitment_slot_2', 'previous_experience',
            'reason_for_joining', 'role_specific_answers',
            'has_flight_experience', 'flight_hours', 'preferred_aircraft',
            'weekly_availability_hours', 'can_attend_mandatory_events',
            'availability_notes', 'leadership_experience', 'technical_experience',
            'referrer', 'referral_source', 'current_step'
        ]

    def create(self, validated_data):
        # Set discord_id from the authenticated user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['discord_id'] = request.user.discord_id
            validated_data['user'] = request.user

        application = super().create(validated_data)

        # Create progress tracker
        ApplicationProgress.objects.create(application=application)

        return application

    def update(self, instance, validated_data):
        # Update current_step if provided
        if 'current_step' in validated_data:
            current_step = validated_data.pop('current_step')
            if hasattr(instance, 'progress'):
                instance.progress.current_step = current_step
                instance.progress.save()

        # Update the application
        application = super().update(instance, validated_data)

        # Update progress based on what fields are filled
        if hasattr(application, 'progress'):
            progress = application.progress

            # Check each step completion
            if all([application.first_name, application.last_name, application.email,
                    application.timezone, application.country]):
                progress.basic_info_completed = True

            if application.branch:
                progress.branch_selected = True

            if application.primary_unit:
                progress.primary_unit_selected = True

            if application.secondary_unit:
                progress.secondary_unit_selected = True

            if application.career_track:
                progress.track_selected = True

            if application.selected_recruitment_slot:
                progress.position_selected = True

            if application.previous_experience and application.reason_for_joining:
                progress.experience_completed = True

            # Check if role-specific questions are answered based on track
            if application.career_track == 'warrant' and application.has_flight_experience is not None:
                progress.role_specific_completed = True
            elif application.career_track == 'officer' and application.leadership_experience:
                progress.role_specific_completed = True
            elif application.career_track == 'enlisted':
                progress.role_specific_completed = True

            progress.save()

        return application


class ApplicationSubmitSerializer(serializers.Serializer):
    """Serializer for final application submission"""
    confirm_submission = serializers.BooleanField()
    accept_all_waivers = serializers.BooleanField()

    def validate(self, data):
        if not data.get('confirm_submission'):
            raise serializers.ValidationError("You must confirm submission")
        if not data.get('accept_all_waivers'):
            raise serializers.ValidationError("You must accept all waivers and acknowledgments")
        return data


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Public serializer for checking application status"""
    progress = ApplicationProgressSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'application_number', 'status', 'status_display',
            'submitted_at', 'progress', 'interview_scheduled_at'
        ]


class UserOnboardingProgressSerializer(serializers.ModelSerializer):
    """Serializer for post-approval onboarding"""
    user_username = serializers.ReadOnlyField(source='user.username')
    application_number = serializers.ReadOnlyField(source='application.application_number', default=None)

    class Meta:
        model = UserOnboardingProgress
        fields = '__all__'


class MentorAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for mentor assignments"""
    recruit_username = serializers.ReadOnlyField(source='recruit.username')
    recruit_avatar = serializers.ReadOnlyField(source='recruit.avatar_url')
    mentor_username = serializers.ReadOnlyField(source='mentor.username')
    mentor_avatar = serializers.ReadOnlyField(source='mentor.avatar_url')
    assigned_by_username = serializers.ReadOnlyField(source='assigned_by.username')
    application_number = serializers.ReadOnlyField(source='application.application_number', default=None)

    class Meta:
        model = MentorAssignment
        fields = '__all__'


class ApplicationRecruitmentDataSerializer(serializers.Serializer):
    """Serializer for initial recruitment data shown to applicants"""
    branches = serializers.SerializerMethodField()
    career_tracks = serializers.SerializerMethodField()
    waivers = serializers.SerializerMethodField()

    def get_branches(self, obj):
        branches = Branch.objects.all()
        return BranchSerializer(branches, many=True).data

    def get_career_tracks(self, obj):
        return [
            {
                'value': 'enlisted',
                'label': 'Enlisted',
                'description': 'Start as an enlisted member and work your way up through the ranks',
                'requirements': []
            },
            {
                'value': 'warrant',
                'label': 'Warrant Officer',
                'description': 'Technical specialist track, ideal for pilots and technical experts',
                'requirements': ['Flight experience recommended for aviation units']
            },
            {
                'value': 'officer',
                'label': 'Commissioned Officer',
                'description': 'Leadership track for those ready to take command responsibilities',
                'requirements': ['Leadership experience recommended']
            }
        ]

    def get_waivers(self, obj):
        waivers = ApplicationWaiverType.objects.filter(is_required=True).order_by('order')
        return ApplicationWaiverTypeSerializer(waivers, many=True).data