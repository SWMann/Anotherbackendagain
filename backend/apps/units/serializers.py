from rest_framework import serializers
from .models import Branch, Rank, Unit, Position, UserPosition
from django.contrib.auth import get_user_model

User = get_user_model()


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class RankSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')

    class Meta:
        model = Rank
        fields = '__all__'


class UnitListSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    parent_unit_name = serializers.ReadOnlyField(source='parent_unit.name', default=None)

    class Meta:
        model = Unit
        fields = ['id', 'name', 'abbreviation', 'branch', 'branch_name', 'parent_unit', 'parent_unit_name', 'unit_type',
                  'emblem_url', 'is_active']


class UnitDetailSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    parent_unit_name = serializers.ReadOnlyField(source='parent_unit.name', default=None)
    commander = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = '__all__'

    def get_commander(self, obj):
        if obj.commander_position:
            user_position = UserPosition.objects.filter(position=obj.commander_position, is_primary=True).first()
            if user_position:
                return {
                    'id': user_position.user.id,
                    'username': user_position.user.username,
                    'avatar_url': user_position.user.avatar_url,
                    'rank': user_position.user.current_rank.abbreviation if user_position.user.current_rank else None
                }
        return None


class PositionSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source='unit.name')

    class Meta:
        model = Position
        fields = '__all__'


class UserPositionSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.ReadOnlyField(source='user.avatar_url')
    position_title = serializers.ReadOnlyField(source='position.title')
    unit_name = serializers.ReadOnlyField(source='unit.name')

    class Meta:
        model = UserPosition
        fields = '__all__'


class UnitMemberSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    avatar_url = serializers.ReadOnlyField(source='user.avatar_url')
    rank = serializers.SerializerMethodField()
    position = serializers.ReadOnlyField(source='position.title')

    class Meta:
        model = UserPosition
        fields = ['id', 'username', 'avatar_url', 'rank', 'position', 'assignment_date', 'is_primary', 'status']

    def get_rank(self, obj):
        if obj.user.current_rank:
            return {
                'abbreviation': obj.user.current_rank.abbreviation,
                'name': obj.user.current_rank.name,
                'insignia_image_url': obj.user.current_rank.insignia_image_url
            }
        return None


class UnitHierarchySerializer(serializers.ModelSerializer):
    subunits = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'name', 'abbreviation', 'unit_type', 'emblem_url', 'subunits']

    def get_subunits(self, obj):
        subunits = Unit.objects.filter(parent_unit=obj)
        if subunits:
            return UnitHierarchySerializer(subunits, many=True).data
        return []


class ChainOfCommandSerializer(serializers.ModelSerializer):
    subordinates = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id', 'title', 'user', 'subordinates']

    def get_subordinates(self, obj):
        subordinates = Position.objects.filter(parent_position=obj)
        if subordinates:
            return ChainOfCommandSerializer(subordinates, many=True).data
        return []

    def get_user(self, obj):
        user_position = UserPosition.objects.filter(position=obj, is_primary=True).first()
        if user_position:
            return {
                'id': user_position.user.id,
                'username': user_position.user.username,
                'avatar_url': user_position.user.avatar_url,
                'rank': user_position.user.current_rank.abbreviation if user_position.user.current_rank else None
            }
        return None


class UnitHierarchyViewSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source='created_by.username', default=None)
    included_units_count = serializers.SerializerMethodField()

    class Meta:
        model = UnitHierarchyView
        fields = '__all__'
        read_only_fields = ['created_by']

    def get_included_units_count(self, obj):
        return obj.included_units.count() if obj.included_units.exists() else 'All Units'


class UnitHierarchyNodeSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source='unit.name')
    unit_abbreviation = serializers.ReadOnlyField(source='unit.abbreviation')
    unit_type = serializers.ReadOnlyField(source='unit.unit_type')

    class Meta:
        model = UnitHierarchyNode
        fields = '__all__'


class UnitNodeSerializer(serializers.ModelSerializer):
    """Serializer for unit nodes in hierarchy view"""
    personnel_count = serializers.SerializerMethodField()
    commander = serializers.SerializerMethodField()
    parent_unit_id = serializers.CharField(source='parent_unit.id', allow_null=True, read_only=True)
    branch_name = serializers.ReadOnlyField(source='branch.name')
    branch_color = serializers.ReadOnlyField(source='branch.color_code')
    subunits = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'abbreviation', 'unit_type', 'description',
            'emblem_url', 'is_active', 'parent_unit_id', 'branch_name',
            'branch_color', 'personnel_count', 'commander', 'subunits',
            'positions', 'motto', 'established_date'
        ]

    def get_personnel_count(self, obj):
        return UserPosition.objects.filter(unit=obj, status='Active').count()

    def get_commander(self, obj):
        if obj.commander_position:
            commander_assignment = UserPosition.objects.filter(
                position=obj.commander_position,
                is_primary=True,
                status='Active'
            ).select_related('user').first()

            if commander_assignment and commander_assignment.user:
                return {
                    'id': commander_assignment.user.id,
                    'username': commander_assignment.user.username,
                    'rank': commander_assignment.user.current_rank.abbreviation if commander_assignment.user.current_rank else None
                }
        return None

    def get_subunits(self, obj):
        # Only return direct children IDs to avoid deep recursion
        return list(obj.subunits.filter(is_active=True).values_list('id', flat=True))

    def get_positions(self, obj):
        positions = obj.positions.all()
        return [{
            'id': pos.id,
            'title': pos.title,
            'is_command_position': pos.is_command_position,
            'is_filled': UserPosition.objects.filter(position=pos, status='Active').exists()
        } for pos in positions]


class HierarchyDataSerializer(serializers.Serializer):
    """Serializer for complete hierarchy data"""
    view = UnitHierarchyViewSerializer()
    nodes = UnitNodeSerializer(many=True)
    edges = serializers.ListField(child=serializers.DictField())
    node_positions = serializers.DictField(required=False)