from rest_framework import serializers
from .models import Ship
from django.utils import timezone


class ShipListSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    assigned_unit_name = serializers.ReadOnlyField(source='assigned_unit.name', default=None)

    class Meta:
        model = Ship
        fields = ['id', 'name', 'designation', 'class_type', 'manufacturer',
                  'owner_username', 'assigned_unit_name', 'primary_role',
                  'approval_status', 'primary_image_url', 'is_flagship']


class ShipDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    owner_avatar = serializers.ReadOnlyField(source='owner.avatar_url')
    assigned_unit_name = serializers.ReadOnlyField(source='assigned_unit.name', default=None)
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username', default=None)

    class Meta:
        model = Ship
        fields = '__all__'


class ShipCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        exclude = ['owner', 'approval_status', 'approval_date', 'approved_by']


class ShipApprovalSerializer(serializers.Serializer):
    approval_status = serializers.ChoiceField(choices=[
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])
    comment = serializers.CharField(required=False, allow_blank=True)