from rest_framework import serializers
from .models import CommissionStage, Application, UserOnboardingProgress, BranchApplication, MentorAssignment
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class CommissionStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionStage
        fields = '__all__'


class ApplicationListSerializer(serializers.ModelSerializer):
    preferred_branch_name = serializers.ReadOnlyField(source='preferred_branch.name', default=None)
    preferred_unit_name = serializers.ReadOnlyField(source='preferred_unit.name', default=None)

    class Meta:
        model = Application
        fields = ['id', 'discord_id', 'username', 'email', 'preferred_branch',
                  'preferred_branch_name', 'preferred_unit', 'preferred_unit_name',
                  'status', 'submission_date', 'interview_date']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    preferred_branch_name = serializers.ReadOnlyField(source='preferred_branch.name', default=None)
    preferred_unit_name = serializers.ReadOnlyField(source='preferred_unit.name', default=None)
    referrer_username = serializers.ReadOnlyField(source='referrer.username', default=None)
    reviewer_username = serializers.ReadOnlyField(source='reviewer.username', default=None)
    mos_priority_1_details = serializers.SerializerMethodField()
    mos_priority_2_details = serializers.SerializerMethodField()
    mos_priority_3_details = serializers.SerializerMethodField()


    def get_mos_priority_1_details(self, obj):
        if obj.mos_priority_1:
            return {
                'id': obj.mos_priority_1.id,
                'code': obj.mos_priority_1.code,
                'title': obj.mos_priority_1.title
            }
        return None

    def get_mos_priority_2_details(self, obj):
        if obj.mos_priority_2:
            return {
                'id': obj.mos_priority_2.id,
                'code': obj.mos_priority_2.code,
                'title': obj.mos_priority_2.title
            }
        return None

    def get_mos_priority_3_details(self, obj):
        if obj.mos_priority_3:
            return {
                'id': obj.mos_priority_3.id,
                'code': obj.mos_priority_3.code,
                'title': obj.mos_priority_3.title
            }
        return None
    class Meta:
        model = Application
        fields = '__all__'


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'discord_id', 'username', 'email', 'preferred_branch',
            'preferred_unit', 'motivation', 'experience', 'referrer',
            'mos_priority_1', 'mos_priority_2', 'mos_priority_3',
            'mos_waiver_requested', 'mos_waiver_reason'
        ]


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status', 'reviewer_notes', 'interview_date']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['discord_id', 'username', 'status', 'submission_date', 'review_date', 'interview_date']


class UserOnboardingProgressSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    application_status = serializers.ReadOnlyField(source='application.status', default=None)
    bit_event_title = serializers.ReadOnlyField(source='bit_event.title', default=None)
    branch_application_status = serializers.ReadOnlyField(source='branch_application.status', default=None)
    branch_induction_event_title = serializers.ReadOnlyField(source='branch_induction_event.title', default=None)

    class Meta:
        model = UserOnboardingProgress
        fields = '__all__'


class BranchApplicationSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    branch_name = serializers.ReadOnlyField(source='branch.name')
    reviewer_username = serializers.ReadOnlyField(source='reviewer.username', default=None)

    class Meta:
        model = BranchApplication
        fields = '__all__'


class BranchApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchApplication
        fields = ['branch', 'application_type', 'motivation', 'experience', 'preferred_role']


class BranchApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchApplication
        fields = ['status', 'reviewer_notes']


class MentorAssignmentSerializer(serializers.ModelSerializer):
    recruit_username = serializers.ReadOnlyField(source='recruit.username')
    recruit_avatar = serializers.ReadOnlyField(source='recruit.avatar_url')
    mentor_username = serializers.ReadOnlyField(source='mentor.username')
    mentor_avatar = serializers.ReadOnlyField(source='mentor.avatar_url')
    assigned_by_username = serializers.ReadOnlyField(source='assigned_by.username')

    class Meta:
        model = MentorAssignment
        fields = '__all__'


class MentorAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorAssignment
        fields = ['recruit', 'mentor', 'assignment_notes']


class NextRequirementsSerializer(serializers.Serializer):
    current_stage = serializers.SerializerMethodField()
    next_stage = serializers.SerializerMethodField()
    missing_requirements = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    def get_current_stage(self, obj):
        if obj.user.commission_stage:
            return {
                'id': obj.user.commission_stage.id,
                'name': obj.user.commission_stage.name,
                'description': obj.user.commission_stage.description,
                'badge_image_url': obj.user.commission_stage.badge_image_url
            }
        return None

    def get_next_stage(self, obj):
        if obj.user.commission_stage:
            next_stage = CommissionStage.objects.filter(
                order_index__gt=obj.user.commission_stage.order_index
            ).order_by('order_index').first()

            if next_stage:
                return {
                    'id': next_stage.id,
                    'name': next_stage.name,
                    'description': next_stage.description,
                    'requirements': next_stage.requirements,
                    'badge_image_url': next_stage.badge_image_url
                }
        return None

    def get_missing_requirements(self, obj):
        if not obj.user.commission_stage:
            return ["No commission stage assigned"]

        next_stage = CommissionStage.objects.filter(
            order_index__gt=obj.user.commission_stage.order_index
        ).order_by('order_index').first()

        if not next_stage:
            return ["Highest commission stage reached"]

        missing = []

        # Check time requirement
        if next_stage.time_requirement:
            if not obj.user.commission_stage or not obj.user.join_date:
                missing.append(f"Time in service: {next_stage.time_requirement} days required")
            else:
                days_in_service = (timezone.now() - obj.user.join_date).days
                if days_in_service < next_stage.time_requirement:
                    missing.append(f"Time in service: {days_in_service}/{next_stage.time_requirement} days")

        # Check training requirements
        if next_stage.training_requirements:
            user_certs = set(
                obj.user.usercertificate_set.filter(is_active=True).values_list('certificate_id', flat=True))
            for cert_id in next_stage.training_requirements:
                if cert_id not in user_certs:
                    from apps.training.models import TrainingCertificate
                    try:
                        cert = TrainingCertificate.objects.get(id=cert_id)
                        missing.append(f"Missing certificate: {cert.name}")
                    except TrainingCertificate.DoesNotExist:
                        missing.append(f"Missing certificate (ID: {cert_id})")

        return missing if missing else ["All requirements met for next stage"]

    def get_progress_percentage(self, obj):
        if not obj.user.commission_stage:
            return 0

        next_stage = CommissionStage.objects.filter(
            order_index__gt=obj.user.commission_stage.order_index
        ).order_by('order_index').first()

        if not next_stage:
            return 100

        requirements_count = 0
        fulfilled_count = 0

        # Time requirement
        if next_stage.time_requirement:
            requirements_count += 1
            if obj.user.join_date:
                days_in_service = (timezone.now() - obj.user.join_date).days
                if days_in_service >= next_stage.time_requirement:
                    fulfilled_count += 1
                else:
                    fulfilled_count += days_in_service / next_stage.time_requirement

        # Training requirements
        if next_stage.training_requirements:
            user_certs = set(
                obj.user.usercertificate_set.filter(is_active=True).values_list('certificate_id', flat=True))
            cert_count = len(next_stage.training_requirements)
            requirements_count += cert_count
            fulfilled_count += len([c for c in next_stage.training_requirements if c in user_certs])

        return int((fulfilled_count / max(requirements_count, 1)) * 100)