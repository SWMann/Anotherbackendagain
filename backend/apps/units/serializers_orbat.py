# backend/apps/units/serializers_orbat.py
from rest_framework import serializers
from .models import Position, UserPosition
from apps.users.serializers import UserSerializer


class ORBATUserSerializer(serializers.Serializer):
    """Lightweight user serializer for ORBAT nodes"""
    id = serializers.UUIDField()
    username = serializers.CharField()
    service_number = serializers.CharField()
    avatar_url = serializers.URLField()
    rank = serializers.SerializerMethodField()

    def get_rank(self, obj):
        if obj.current_rank:
            return {
                'abbreviation': obj.current_rank.abbreviation,
                'name': obj.current_rank.name,
                'insignia_url': obj.current_rank.insignia_image_url
            }
        return None


class ORBATNodeSerializer(serializers.ModelSerializer):
    """Serializer for ORBAT position nodes"""
    id = serializers.CharField()  # Convert to string for React Flow
    current_holder = serializers.SerializerMethodField()
    unit_info = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    position_type = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = [
            'id', 'display_title', 'current_holder', 'unit_info',
            'role_info', 'position_type', 'is_vacant', 'display_order',
            'manual_x', 'manual_y', 'orbat_display_level'
        ]

    def get_current_holder(self, obj):
        active_assignment = obj.assignments.filter(
            status='active',
            assignment_type='primary'
        ).first()

        if active_assignment:
            return ORBATUserSerializer(active_assignment.user).data
        return None

    def get_unit_info(self, obj):
        return {
            'id': obj.unit.id,
            'name': obj.unit.name,
            'abbreviation': obj.unit.abbreviation,
            'unit_type': obj.unit.unit_type,
            'emblem_url': obj.unit.emblem_url
        }

    def get_role_info(self, obj):
        return {
            'id': obj.role.id,
            'name': obj.role.name,
            'category': obj.role.category,
            'is_command_role': obj.role.is_command_role,
            'is_staff_role': obj.role.is_staff_role,
            'icon_url': obj.role.icon_url,
            'color_code': obj.role.color_code
        }

    def get_position_type(self, obj):
        if obj.role.is_command_role:
            return 'command'
        elif obj.role.is_staff_role:
            return 'staff'
        elif obj.role.is_nco_role:
            return 'nco'
        elif obj.role.is_specialist_role:
            return 'specialist'
        else:
            return 'standard'


class ORBATEdgeSerializer(serializers.Serializer):
    """Serializer for ORBAT edges (relationships between positions)"""
    id = serializers.CharField()
    source = serializers.CharField()
    target = serializers.CharField()
    type = serializers.CharField(default='smoothstep')
    animated = serializers.BooleanField(default=False)
    style = serializers.DictField(required=False)
    data = serializers.DictField(required=False)


class ORBATDataSerializer(serializers.Serializer):
    """Complete ORBAT data serializer"""
    nodes = ORBATNodeSerializer(many=True)
    edges = ORBATEdgeSerializer(many=True)
    unit = serializers.DictField()
    statistics = serializers.DictField()