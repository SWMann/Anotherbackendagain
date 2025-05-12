from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'avatar_url', 'discord_id',
            'bio', 'join_date', 'is_active', 'is_staff', 'is_admin',
            'service_number', 'background_image_url', 'timezone',
            'discord_notifications', 'email_notifications',
            'onboarding_status', 'recruit_status',
            'officer_candidate', 'warrant_officer_candidate'
        ]
        read_only_fields = [
            'id', 'join_date', 'is_active', 'is_staff', 'is_admin', 'discord_id'
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that includes the user data in the response
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        user = self.user
        data['user'] = UserSerializer(user).data

        return data


class TokenRefreshResponseSerializer(serializers.Serializer):
    """
    Serializer for token refresh response
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class TokenVerifyResponseSerializer(serializers.Serializer):
    """
    Serializer for token verify response
    """
    user = UserSerializer()