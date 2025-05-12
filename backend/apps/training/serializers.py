from rest_framework import serializers
from .models import TrainingCertificate, UserCertificate
from django.utils import timezone
from datetime import timedelta


class TrainingCertificateSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    min_rank_name = serializers.ReadOnlyField(source='min_rank_requirement.name', default=None)

    class Meta:
        model = TrainingCertificate
        fields = '__all__'


class UserCertificateSerializer(serializers.ModelSerializer):
    certificate_name = serializers.ReadOnlyField(source='certificate.name')
    certificate_abbreviation = serializers.ReadOnlyField(source='certificate.abbreviation')
    certificate_badge = serializers.ReadOnlyField(source='certificate.badge_image_url')
    issuer_username = serializers.ReadOnlyField(source='issuer.username')
    user_username = serializers.ReadOnlyField(source='user.username')
    revoked_by_username = serializers.ReadOnlyField(source='revoked_by.username', default=None)
    training_event_title = serializers.ReadOnlyField(source='training_event.title', default=None)

    class Meta:
        model = UserCertificate
        fields = '__all__'


class IssueCertificateSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    certificate_id = serializers.UUIDField()
    training_event_id = serializers.UUIDField(required=False, allow_null=True)
    certificate_file_url = serializers.URLField(required=False, allow_blank=True)
    expiry_days = serializers.IntegerField(required=False, allow_null=True,
                                           help_text="Days until expiration, null for certificate default")

    def validate(self, data):
        # Check if user already has an active certificate of this type
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        try:
            certificate = TrainingCertificate.objects.get(id=data['certificate_id'])
        except TrainingCertificate.DoesNotExist:
            raise serializers.ValidationError("Certificate not found")

        existing = UserCertificate.objects.filter(
            user_id=data['user_id'],
            certificate_id=data['certificate_id'],
            is_active=True
        ).exists()

        if existing:
            raise serializers.ValidationError("User already has an active certificate of this type")

        # Check if user meets minimum rank requirement
        if certificate.min_rank_requirement and user.current_rank:
            if user.current_rank.tier < certificate.min_rank_requirement.tier:
                raise serializers.ValidationError(
                    f"User does not meet the minimum rank requirement of {certificate.min_rank_requirement.name}"
                )

        return data


class RevokeCertificateSerializer(serializers.Serializer):
    revocation_reason = serializers.CharField()