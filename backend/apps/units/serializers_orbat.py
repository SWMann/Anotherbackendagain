# backend/apps/units/serializers_orbat.py
from rest_framework import serializers
from .models import Position, Unit, UserPosition


class ORBATUnitSerializer(serializers.ModelSerializer):
    """Lightweight unit serializer for ORBAT views"""
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Unit
        fields = ['id', 'name', 'abbreviation', 'unit_type', 'branch_name', 'emblem_url']


class ORBATUserSerializer(serializers.Serializer):
    """Serializer for user info in ORBAT nodes"""
    id = serializers.UUIDField()
    username = serializers.CharField()
    service_number = serializers.CharField(allow_null=True)
    avatar_url = serializers.URLField(allow_null=True)
    rank = serializers.SerializerMethodField()

    def get_rank(self, obj):
        if hasattr(obj, 'current_rank') and obj.current_rank:
            return {
                'abbreviation': obj.current_rank.abbreviation,
                'name': obj.current_rank.name,
                'insignia_url': obj.current_rank.insignia_image_url
            }
        return None


class ORBATNodeSerializer(serializers.ModelSerializer):
    """Serializer for ORBAT position nodes"""
    id = serializers.CharField()  # Convert UUID to string for React Flow
    display_title = serializers.CharField()
    unit_info = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    current_holder = serializers.SerializerMethodField()
    position_type = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = [
            'id', 'display_title', 'is_vacant', 'display_order',
            'unit_info', 'role_info', 'current_holder', 'position_type'
        ]

    def get_unit_info(self, obj):
        if obj.unit:
            return {
                'id': str(obj.unit.id),
                'name': obj.unit.name,
                'abbreviation': obj.unit.abbreviation,
                'unit_type': obj.unit.unit_type
            }
        return None

    def get_role_info(self, obj):
        if obj.role:
            return {
                'id': str(obj.role.id),
                'name': obj.role.name,
                'category': obj.role.category,
                'is_command_role': obj.role.is_command_role,
                'is_staff_role': obj.role.is_staff_role
            }
        return None

    def get_current_holder(self, obj):
        # Get the active primary assignment
        active_assignment = obj.assignments.filter(
            status='active',
            assignment_type='primary'
        ).select_related('user', 'user__current_rank').first()

        if active_assignment and active_assignment.user:
            return ORBATUserSerializer(active_assignment.user).data
        return None

    def get_position_type(self, obj):
        if obj.role:
            if obj.role.is_command_role:
                return 'command'
            elif obj.role.is_staff_role:
                return 'staff'
            elif obj.role.category == 'nco':
                return 'nco'
            elif obj.role.category == 'specialist':
                return 'specialist'
        return 'standard'