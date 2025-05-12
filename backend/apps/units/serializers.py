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