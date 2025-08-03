# backend/apps/commendations/serializers.py
from rest_framework import serializers
from .models import CommendationType, Commendation, CommendationDevice, CommendationDeviceAwarded
from django.utils import timezone
from apps.core.serializers import MediaURLMixin
from apps.units.models import Branch


class CommendationTypeSerializer(MediaURLMixin, serializers.ModelSerializer):
    allowed_branches = serializers.SerializerMethodField()
    min_rank_name = serializers.ReadOnlyField(source='min_rank_requirement.name', default=None)
    ribbon_display_url = serializers.SerializerMethodField()
    medal_display_url = serializers.SerializerMethodField()
    awards_count = serializers.SerializerMethodField()

    class Meta:
        model = CommendationType
        fields = '__all__'

    def get_allowed_branches(self, obj):
        return [
            {
                'id': branch.id,
                'name': branch.name,
                'abbreviation': branch.abbreviation
            }
            for branch in obj.allowed_branches.all()
        ]

    def get_ribbon_display_url(self, obj):
        if obj.ribbon_image:
            return self.get_media_url(obj, 'ribbon_image')
        return obj.ribbon_image_url

    def get_medal_display_url(self, obj):
        if obj.medal_image:
            return self.get_media_url(obj, 'medal_image')
        return obj.medal_image_url

    def get_awards_count(self, obj):
        return obj.commendation_set.count()


class CommendationDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommendationDevice
        fields = '__all__'


class CommendationDeviceAwardedSerializer(serializers.ModelSerializer):
    device_details = CommendationDeviceSerializer(source='device', read_only=True)

    class Meta:
        model = CommendationDeviceAwarded
        fields = '__all__'


class CommendationSerializer(serializers.ModelSerializer):
    commendation_type_details = CommendationTypeSerializer(source='commendation_type', read_only=True)
    user_username = serializers.ReadOnlyField(source='user.username')
    user_rank = serializers.SerializerMethodField()
    user_avatar = serializers.ReadOnlyField(source='user.avatar_url')
    awarded_by_username = serializers.ReadOnlyField(source='awarded_by.username', default=None)
    verified_by_username = serializers.ReadOnlyField(source='verified_by.username', default=None)
    related_event_title = serializers.ReadOnlyField(source='related_event.title', default=None)
    related_unit_name = serializers.ReadOnlyField(source='related_unit.name', default=None)
    devices = CommendationDeviceAwardedSerializer(many=True, read_only=True)

    class Meta:
        model = Commendation
        fields = '__all__'

    def get_user_rank(self, obj):
        if obj.user.current_rank:
            return {
                'abbreviation': obj.user.current_rank.abbreviation,
                'name': obj.user.current_rank.name,
                'insignia_url': obj.user.current_rank.insignia_display_url
            }
        return None


class AwardCommendationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    commendation_type_id = serializers.UUIDField()
    citation = serializers.CharField()
    short_citation = serializers.CharField(max_length=500)
    awarded_date = serializers.DateTimeField(required=False)
    related_event_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    related_unit_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    order_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True, default='')
    is_public = serializers.BooleanField(default=True)
    supporting_documents = serializers.JSONField(required=False, default=list)
    devices = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )

    def validate(self, data):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Validate user exists
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        # Validate commendation type exists
        try:
            comm_type = CommendationType.objects.get(id=data['commendation_type_id'])
        except CommendationType.DoesNotExist:
            raise serializers.ValidationError("Commendation type not found")

        # Check if user meets minimum rank requirement
        if comm_type.min_rank_requirement and user.current_rank:
            if user.current_rank.tier < comm_type.min_rank_requirement.tier:
                raise serializers.ValidationError(
                    f"User does not meet the minimum rank requirement of {comm_type.min_rank_requirement.name}"
                )

        # Check branch restrictions
        if comm_type.allowed_branches.exists() and user.branch:
            if user.branch not in comm_type.allowed_branches.all():
                raise serializers.ValidationError(
                    "This commendation is not available for the user's branch"
                )

        # Check max awards
        if comm_type.max_awards_per_user > 0:
            existing_count = Commendation.objects.filter(
                user_id=data['user_id'],
                commendation_type_id=data['commendation_type_id']
            ).count()
            if existing_count >= comm_type.max_awards_per_user:
                raise serializers.ValidationError(
                    f"User has already received the maximum number ({comm_type.max_awards_per_user}) of this commendation"
                )

        # Set default awarded date if not provided
        if 'awarded_date' not in data:
            data['awarded_date'] = timezone.now()

        # Clean up None values for optional fields
        if 'related_event_id' in data and data['related_event_id'] == '':
            data['related_event_id'] = None
        if 'related_unit_id' in data and data['related_unit_id'] == '':
            data['related_unit_id'] = None
        if 'order_number' in data and data['order_number'] == '':
            data['order_number'] = ''

        return data


class CreateCommendationTypeSerializer(serializers.ModelSerializer):
    allowed_branches = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Branch.objects.all(),
        required=False
    )

    class Meta:
        model = CommendationType
        fields = [
            'name', 'abbreviation', 'description', 'category', 'precedence',
            'ribbon_image', 'medal_image', 'ribbon_image_url', 'medal_image_url',
            'eligibility_criteria', 'min_rank_requirement', 'requires_nomination',
            'auto_award_criteria', 'is_active', 'multiple_awards_allowed',
            'max_awards_per_user', 'allowed_branches'
        ]

    def create(self, validated_data):
        allowed_branches = validated_data.pop('allowed_branches', [])
        instance = super().create(validated_data)
        if allowed_branches:
            instance.allowed_branches.set(allowed_branches)
        return instance

    def update(self, instance, validated_data):
        allowed_branches = validated_data.pop('allowed_branches', None)
        instance = super().update(instance, validated_data)
        if allowed_branches is not None:
            instance.allowed_branches.set(allowed_branches)
        return instance