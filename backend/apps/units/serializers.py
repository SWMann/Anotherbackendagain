# backend/apps/units/serializers.py
from rest_framework import serializers
from .models import (
    Branch, Rank, Unit, Role, Position, UserPosition,
    UnitHierarchyView, UnitHierarchyNode, RecruitmentSlot, PositionTemplate, TemplatePosition)
from django.db.models import Sum, F

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# Basic Serializers
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class RankSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')

    class Meta:
        model = Rank
        fields = '__all__'


# Role Serializers
class RoleListSerializer(serializers.ModelSerializer):
    """Simple serializer for role lists"""
    positions_count = serializers.SerializerMethodField()
    filled_positions_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'abbreviation', 'category', 'description',
            'is_command_role', 'is_staff_role', 'is_nco_role',
            'is_specialist_role', 'icon_url', 'positions_count',
            'filled_positions_count', 'sort_order'
        ]

    def get_positions_count(self, obj):
        return obj.positions.filter(is_active=True).count()

    def get_filled_positions_count(self, obj):
        return obj.positions.filter(is_active=True, is_vacant=False).count()


class RoleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for role with all relationships"""
    allowed_branches = serializers.SerializerMethodField()
    min_rank_details = RankSerializer(source='min_rank', read_only=True)
    max_rank_details = RankSerializer(source='max_rank', read_only=True)
    typical_rank_details = RankSerializer(source='typical_rank', read_only=True)
    parent_role_details = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_allowed_branches(self, obj):
        return BranchSerializer(obj.allowed_branches.all(), many=True).data

    def get_parent_role_details(self, obj):
        if obj.parent_role:
            return {
                'id': obj.parent_role.id,
                'name': obj.parent_role.name,
                'category': obj.parent_role.category
            }
        return None

    def get_positions(self, obj):
        positions = obj.positions.filter(is_active=True).select_related('unit')
        return [{
            'id': pos.id,
            'unit': pos.unit.name,
            'unit_id': pos.unit.id,
            'display_title': pos.display_title,
            'is_vacant': pos.is_vacant
        } for pos in positions]


# Add this to backend/apps/units/serializers.py after RoleDetailSerializer

# Add to backend/apps/units/serializers.py after the existing serializers

class RecruitmentSlotSerializer(serializers.ModelSerializer):
    """Serializer for recruitment slots"""
    unit_name = serializers.ReadOnlyField(source='unit.name')
    role_name = serializers.ReadOnlyField(source='role.name')
    role_category = serializers.ReadOnlyField(source='role.category')
    available_slots = serializers.ReadOnlyField()

    class Meta:
        model = RecruitmentSlot
        fields = [
            'id', 'unit', 'unit_name', 'role', 'role_name', 'role_category',
            'career_track', 'total_slots', 'filled_slots', 'reserved_slots',
            'available_slots', 'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'available_slots']

    def validate(self, data):
        # Ensure filled + reserved doesn't exceed total
        total = data.get('total_slots', self.instance.total_slots if self.instance else 0)
        filled = data.get('filled_slots', self.instance.filled_slots if self.instance else 0)
        reserved = data.get('reserved_slots', self.instance.reserved_slots if self.instance else 0)

        if filled + reserved > total:
            raise serializers.ValidationError(
                "Filled slots + reserved slots cannot exceed total slots"
            )
        return data


class RecruitmentSlotCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating recruitment slots"""

    class Meta:
        model = RecruitmentSlot
        fields = [
            'unit', 'role', 'career_track', 'total_slots',
            'filled_slots', 'reserved_slots', 'is_active', 'notes'
        ]

    def validate(self, data):
        # Check for duplicate slots
        unit = data.get('unit', self.instance.unit if self.instance else None)
        role = data.get('role', self.instance.role if self.instance else None)
        career_track = data.get('career_track', self.instance.career_track if self.instance else None)

        existing = RecruitmentSlot.objects.filter(
            unit=unit,
            role=role,
            career_track=career_track
        ).exclude(pk=self.instance.pk if self.instance else None)

        if existing.exists():
            raise serializers.ValidationError(
                "A recruitment slot for this unit, role, and career track already exists"
            )

        return super().validate(data)


class UnitRecruitmentStatusSerializer(serializers.ModelSerializer):
    """Serializer for unit recruitment status"""
    recruitment_slots = RecruitmentSlotSerializer(many=True, read_only=True)
    total_slots = serializers.SerializerMethodField()
    total_filled = serializers.SerializerMethodField()
    total_available = serializers.SerializerMethodField()
    fill_rate = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'abbreviation', 'recruitment_status',
            'max_personnel', 'target_personnel', 'recruitment_notes',
            'recruitment_slots', 'total_slots', 'total_filled',
            'total_available', 'fill_rate'
        ]

    def get_total_slots(self, obj):
        return obj.recruitment_slots.filter(is_active=True).aggregate(
            total=Sum('total_slots')
        )['total'] or 0

    def get_total_filled(self, obj):
        return obj.recruitment_slots.filter(is_active=True).aggregate(
            total=Sum('filled_slots')
        )['total'] or 0

    def get_total_available(self, obj):
        slots = obj.recruitment_slots.filter(is_active=True)
        total = 0
        for slot in slots:
            total += slot.available_slots
        return total

    def get_fill_rate(self, obj):
        total = self.get_total_slots(obj)
        filled = self.get_total_filled(obj)
        if total > 0:
            return round((filled / total) * 100, 1)
        return 0


# Add this import at the top of the file

class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating roles with proper M2M handling"""
    allowed_branches = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Branch.objects.all(),
        required=False
    )

    class Meta:
        model = Role
        fields = '__all__'

    def create(self, validated_data):
        # Extract many-to-many data
        allowed_branches = validated_data.pop('allowed_branches', [])

        # Create the role
        role = Role.objects.create(**validated_data)

        # Set many-to-many relationships
        if allowed_branches:
            role.allowed_branches.set(allowed_branches)

        return role

    def update(self, instance, validated_data):
        # Extract many-to-many data
        allowed_branches = validated_data.pop('allowed_branches', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update many-to-many relationships
        if allowed_branches is not None:
            instance.allowed_branches.set(allowed_branches)

        return instance
# Unit Serializers
class UnitListSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    parent_unit_name = serializers.ReadOnlyField(source='parent_unit.name', default=None)
    commander = serializers.SerializerMethodField()
    personnel_count = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'abbreviation', 'branch', 'branch_name',
            'parent_unit', 'parent_unit_name', 'unit_type', 'emblem_url',
            'is_active', 'commander', 'personnel_count'
        ]

    def get_commander(self, obj):
        # Find command position for this unit
        command_position = obj.positions.filter(
            role__is_command_role=True,
            is_active=True
        ).first()

        if command_position:
            active_assignment = command_position.assignments.filter(
                status='active',
                assignment_type='primary'
            ).select_related('user', 'user__current_rank').first()

            if active_assignment:
                return {
                    'id': active_assignment.user.id,
                    'username': active_assignment.user.username,
                    'rank': active_assignment.user.current_rank.abbreviation if active_assignment.user.current_rank else None
                }
        return None

    def get_personnel_count(self, obj):
        return UserPosition.objects.filter(
            position__unit=obj,
            status='active'
        ).count()


# Position List Serializer (needed before UnitDetailSerializer)
class PositionListSerializer(serializers.ModelSerializer):
    """Simple serializer for position lists"""
    role_name = serializers.ReadOnlyField(source='role.name')
    role_category = serializers.ReadOnlyField(source='role.category')
    unit_name = serializers.ReadOnlyField(source='unit.name')
    unit_abbreviation = serializers.ReadOnlyField(source='unit.abbreviation')
    current_holder = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = [
            'id', 'role', 'role_name', 'role_category', 'unit',
            'unit_name', 'unit_abbreviation', 'display_title',
            'is_active', 'is_vacant', 'current_holder'
        ]

    def get_current_holder(self, obj):
        active = obj.assignments.filter(
            status='active',
            assignment_type='primary'
        ).select_related('user', 'user__current_rank').first()

        if active:
            return {
                'id': active.user.id,
                'username': active.user.username,
                'rank': active.user.current_rank.abbreviation if active.user.current_rank else None
            }
        return None


class UnitDetailSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    parent_unit_details = serializers.SerializerMethodField()
    subunits = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()
    personnel = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = '__all__'

    def get_parent_unit_details(self, obj):
        if obj.parent_unit:
            return {
                'id': obj.parent_unit.id,
                'name': obj.parent_unit.name,
                'abbreviation': obj.parent_unit.abbreviation,
                'unit_type': obj.parent_unit.unit_type
            }
        return None

    def get_subunits(self, obj):
        subunits = obj.subunits.filter(is_active=True)
        return UnitListSerializer(subunits, many=True).data

    def get_positions(self, obj):
        positions = obj.positions.filter(is_active=True).select_related('role')
        return PositionListSerializer(positions, many=True).data

    def get_personnel(self, obj):
        assignments = UserPosition.objects.filter(
            position__unit=obj,
            status='active'
        ).select_related('user', 'position', 'user__current_rank')

        return [{
            'id': assignment.user.id,
            'username': assignment.user.username,
            'rank': assignment.user.current_rank.abbreviation if assignment.user.current_rank else None,
            'position': assignment.position.display_title,
            'assignment_date': assignment.assignment_date,
            'assignment_type': assignment.assignment_type
        } for assignment in assignments]

    def get_statistics(self, obj):
        total_positions = obj.positions.filter(is_active=True).count()
        filled_positions = obj.positions.filter(is_active=True, is_vacant=False).count()

        return {
            'total_positions': total_positions,
            'filled_positions': filled_positions,
            'vacant_positions': total_positions - filled_positions,
            'fill_rate': round((filled_positions / total_positions * 100) if total_positions > 0 else 0, 1),
            'personnel_count': UserPosition.objects.filter(
                position__unit=obj,
                status='active'
            ).count()
        }


# UserPosition Serializers
class UserPositionSerializer(serializers.ModelSerializer):
    """Serializer for user position assignments"""
    user_details = serializers.SerializerMethodField()
    position_details = serializers.SerializerMethodField()
    unit_details = serializers.SerializerMethodField()
    assigned_by_details = serializers.SerializerMethodField()

    class Meta:
        model = UserPosition
        fields = '__all__'

    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'avatar_url': obj.user.avatar_url,
            'rank': RankSerializer(obj.user.current_rank).data if obj.user.current_rank else None,
            'service_number': obj.user.service_number
        }

    def get_position_details(self, obj):
        return {
            'id': obj.position.id,
            'display_title': obj.position.display_title,
            'role': {
                'id': obj.position.role.id,
                'name': obj.position.role.name,
                'category': obj.position.role.category,
                'is_command_role': obj.position.role.is_command_role
            }
        }

    def get_unit_details(self, obj):
        unit = obj.position.unit
        return {
            'id': unit.id,
            'name': unit.name,
            'abbreviation': unit.abbreviation,
            'unit_type': unit.unit_type,
            'emblem_url': unit.emblem_url
        }

    def get_assigned_by_details(self, obj):
        if obj.assigned_by:
            return {
                'id': obj.assigned_by.id,
                'username': obj.assigned_by.username
            }
        return None


# Add this to backend/apps/units/serializers.py in the UserPositionCreateSerializer class

class UserPositionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating position assignments"""

    class Meta:
        model = UserPosition
        fields = [
            'user', 'position', 'status', 'assignment_type',
            'effective_date', 'end_date', 'order_number', 'notes'
        ]

    def validate(self, data):
        # Skip validation if force flag is set in context
        if self.context.get('force', False):
            return data

        # Check if user meets requirements
        position = data['position']
        user = data['user']

        # Check rank requirements
        if position.min_rank and user.current_rank:
            if user.current_rank.tier < position.min_rank.tier:
                raise serializers.ValidationError(
                    f"User's rank ({user.current_rank.abbreviation}) is below minimum required rank ({position.min_rank.abbreviation})"
                )

        if position.max_rank and user.current_rank:
            if user.current_rank.tier > position.max_rank.tier:
                raise serializers.ValidationError(
                    f"User's rank ({user.current_rank.abbreviation}) is above maximum allowed rank ({position.max_rank.abbreviation})"
                )

        # Check time in service
        if position.role and position.role.min_time_in_service > 0:
            days_in_service = (timezone.now() - user.join_date).days
            if days_in_service < position.role.min_time_in_service:
                raise serializers.ValidationError(
                    f"User needs {position.role.min_time_in_service - days_in_service} more days in service"
                )

        # Check for existing active primary assignment
        if data.get('status') == 'active' and data.get('assignment_type') == 'primary':
            existing = UserPosition.objects.filter(
                position=position,
                status='active',
                assignment_type='primary'
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing.exists():
                raise serializers.ValidationError(
                    "This position already has an active primary assignment"
                )

        return data

    def create(self, validated_data):
        # Set assigned_by to current user
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


# Position Detail Serializer (needs UserPositionSerializer)
class PositionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for position with all information"""
    role = RoleDetailSerializer(read_only=True)
    unit = UnitDetailSerializer(read_only=True)
    parent_position_details = serializers.SerializerMethodField()
    subordinate_positions = serializers.SerializerMethodField()
    current_assignments = serializers.SerializerMethodField()
    assignment_history = serializers.SerializerMethodField()
    effective_requirements = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = '__all__'

    def get_parent_position_details(self, obj):
        if obj.parent_position:
            return {
                'id': obj.parent_position.id,
                'display_title': obj.parent_position.display_title,
                'unit': obj.parent_position.unit.name
            }
        return None

    def get_subordinate_positions(self, obj):
        subordinates = obj.subordinate_positions.filter(is_active=True)
        return PositionListSerializer(subordinates, many=True).data

    def get_current_assignments(self, obj):
        active = obj.assignments.filter(
            status='active'
        ).select_related('user', 'user__current_rank')
        return UserPositionSerializer(active, many=True).data

    def get_assignment_history(self, obj):
        history = obj.assignments.select_related(
            'user', 'user__current_rank', 'assigned_by'
        ).order_by('-assignment_date')[:10]
        return UserPositionSerializer(history, many=True).data

    def get_effective_requirements(self, obj):
        return {
            'min_rank': RankSerializer(obj.min_rank).data if obj.min_rank else None,
            'max_rank': RankSerializer(obj.max_rank).data if obj.max_rank else None,
            'min_time_in_service': obj.role.min_time_in_service if obj.role else 0,
            'min_time_in_grade': obj.role.min_time_in_grade if obj.role else 0,
            'min_operations_count': obj.role.min_operations_count if obj.role else 0,
            'additional_requirements': obj.additional_requirements
        }

# Backwards Compatibility Serializers
class UnitMemberSerializer(serializers.ModelSerializer):
    """Updated to work with new UserPosition model"""
    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    avatar_url = serializers.ReadOnlyField(source='user.avatar_url')
    rank = serializers.SerializerMethodField()
    position = serializers.ReadOnlyField(source='position.display_title')
    role = serializers.ReadOnlyField(source='position.role.name')

    class Meta:
        model = UserPosition
        fields = [
            'id', 'username', 'avatar_url', 'rank', 'position',
            'role', 'assignment_date', 'assignment_type', 'status'
        ]

    def get_rank(self, obj):
        if obj.user.current_rank:
            return {
                'abbreviation': obj.user.current_rank.abbreviation,
                'name': obj.user.current_rank.name,
                'insignia_image_url': obj.user.current_rank.insignia_image_url
            }
        return None


class PositionSerializer(serializers.ModelSerializer):
    """Backwards compatibility - redirects to PositionDetailSerializer"""
    unit_name = serializers.ReadOnlyField(source='unit.name')
    role_name = serializers.ReadOnlyField(source='role.name')

    class Meta:
        model = Position
        fields = '__all__'


# Add this to backend/apps/units/serializers.py after PositionDetailSerializer

class PositionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating positions"""

    class Meta:
        model = Position
        fields = [
            'id', 'role', 'unit', 'title', 'identifier', 'parent_position',
            'is_active', 'is_vacant', 'override_min_rank', 'override_max_rank',
            'additional_requirements', 'notes', 'display_order', 'show_in_orbat',
            'orbat_display_level', 'reports_to_external',
            'is_available_for_recruitment', 'recruitment_priority',
            'requires_flight_qualification'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        # Validate that role and unit are provided for new positions
        if self.instance is None:  # Creating new position
            if not data.get('role'):
                raise serializers.ValidationError("Role is required when creating a position")
            if not data.get('unit'):
                raise serializers.ValidationError("Unit is required when creating a position")

        # Check for unique constraint
        role = data.get('role', self.instance.role if self.instance else None)
        unit = data.get('unit', self.instance.unit if self.instance else None)
        identifier = data.get('identifier', self.instance.identifier if self.instance else None)

        if role and unit:
            # Check if this combination already exists
            existing = Position.objects.filter(
                unit=unit,
                role=role,
                identifier=identifier
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing.exists():
                raise serializers.ValidationError(
                    "A position with this role and identifier already exists in this unit"
                )

        return data

    def create(self, validated_data):
        # Set default values
        if 'is_vacant' not in validated_data:
            validated_data['is_vacant'] = True
        if 'is_active' not in validated_data:
            validated_data['is_active'] = True

        return super().create(validated_data)

    def to_representation(self, instance):
        # Return the detailed representation after create/update
        return PositionDetailSerializer(instance, context=self.context).data


# Hierarchy Serializers
class UnitHierarchySerializer(serializers.ModelSerializer):
    subunits = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'name', 'abbreviation', 'unit_type', 'emblem_url', 'subunits']

    def get_subunits(self, obj):
        subunits = Unit.objects.filter(parent_unit=obj, is_active=True)
        if subunits:
            return UnitHierarchySerializer(subunits, many=True).data
        return []


class ChainOfCommandSerializer(serializers.ModelSerializer):
    subordinates = serializers.SerializerMethodField()
    holder = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id', 'display_title', 'holder', 'subordinates']

    def get_subordinates(self, obj):
        subordinates = Position.objects.filter(
            parent_position=obj,
            is_active=True
        )
        if subordinates:
            return ChainOfCommandSerializer(subordinates, many=True).data
        return []

    def get_holder(self, obj):
        assignment = obj.assignments.filter(
            status='active',
            assignment_type='primary'
        ).select_related('user', 'user__current_rank').first()

        if assignment:
            return {
                'id': assignment.user.id,
                'username': assignment.user.username,
                'avatar_url': assignment.user.avatar_url,
                'rank': assignment.user.current_rank.abbreviation if assignment.user.current_rank else None
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
        return UserPosition.objects.filter(
            position__unit=obj,
            status='active'
        ).count()

    def get_commander(self, obj):
        command_position = obj.positions.filter(
            role__is_command_role=True,
            is_active=True
        ).first()

        if command_position:
            assignment = command_position.assignments.filter(
                status='active',
                assignment_type='primary'
            ).select_related('user', 'user__current_rank').first()

            if assignment:
                return {
                    'id': assignment.user.id,
                    'username': assignment.user.username,
                    'rank': assignment.user.current_rank.abbreviation if assignment.user.current_rank else None
                }
        return None

    def get_subunits(self, obj):
        return list(obj.subunits.filter(is_active=True).values_list('id', flat=True))

    def get_positions(self, obj):
        positions = obj.positions.filter(is_active=True).select_related('role')
        return [{
            'id': pos.id,
            'display_title': pos.display_title,
            'role_category': pos.role.category,
            'is_command_position': pos.role.is_command_role,
            'is_vacant': pos.is_vacant
        } for pos in positions]


class HierarchyDataSerializer(serializers.Serializer):
    """Serializer for complete hierarchy data"""
    view = UnitHierarchyViewSerializer()
    nodes = UnitNodeSerializer(many=True)
    edges = serializers.ListField(child=serializers.DictField())
    node_positions = serializers.DictField(required=False)


# Add this to backend/apps/units/serializers.py after the existing serializers

class TemplatePositionSerializer(serializers.ModelSerializer):
    """Serializer for template positions"""
    role_details = RoleDetailSerializer(source='role', read_only=True)

    class Meta:
        model = TemplatePosition
        fields = [
            'id', 'role', 'role_details', 'naming_pattern',
            'identifier_pattern', 'quantity', 'parent_template_position',
            'display_order', 'override_min_rank', 'override_max_rank',
            'additional_config'
        ]


class PositionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for position templates"""
    template_positions = TemplatePositionSerializer(many=True, read_only=True)
    allowed_branches = BranchSerializer(many=True, read_only=True)
    position_count = serializers.SerializerMethodField()

    class Meta:
        model = PositionTemplate
        fields = [
            'id', 'name', 'description', 'template_type',
            'applicable_unit_types', 'allowed_branches',
            'is_active', 'created_by', 'template_positions',
            'position_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_position_count(self, obj):
        return sum(tp.quantity for tp in obj.template_positions.all())


# Fixed PositionTemplateCreateSerializer for backend/apps/units/serializers.py
# This version properly handles foreign keys and filters out unexpected fields

class PositionTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating position templates with proper foreign key handling"""
    template_positions = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = PositionTemplate
        fields = [
            'name', 'description', 'template_type',
            'applicable_unit_types', 'allowed_branches',
            'is_active', 'template_positions'
        ]

    def create(self, validated_data):
        template_positions_data = validated_data.pop('template_positions', [])
        allowed_branches = validated_data.pop('allowed_branches', [])

        # Create the main template
        template = PositionTemplate.objects.create(**validated_data)

        # Set many-to-many relationships
        if allowed_branches:
            template.allowed_branches.set(allowed_branches)

        # Create template positions
        for tp_data in template_positions_data:
            try:
                # Convert role ID to Role instance
                role_id = tp_data.pop('role')
                role = Role.objects.get(id=role_id)

                # Handle optional rank foreign keys
                override_min_rank_id = tp_data.pop('override_min_rank', None)
                override_max_rank_id = tp_data.pop('override_max_rank', None)

                override_min_rank = None
                override_max_rank = None

                if override_min_rank_id:
                    try:
                        override_min_rank = Rank.objects.get(id=override_min_rank_id)
                    except Rank.DoesNotExist:
                        pass

                if override_max_rank_id:
                    try:
                        override_max_rank = Rank.objects.get(id=override_max_rank_id)
                    except Rank.DoesNotExist:
                        pass

                # Handle parent template position if provided
                parent_template_position_id = tp_data.pop('parent_template_position', None)
                parent_template_position = None
                if parent_template_position_id:
                    try:
                        parent_template_position = TemplatePosition.objects.get(id=parent_template_position_id)
                    except TemplatePosition.DoesNotExist:
                        pass

                # Remove any unexpected fields to prevent errors
                allowed_fields = {
                    'naming_pattern', 'identifier_pattern', 'quantity',
                    'display_order', 'additional_config'
                }
                filtered_data = {k: v for k, v in tp_data.items() if k in allowed_fields}

                TemplatePosition.objects.create(
                    template=template,
                    role=role,
                    override_min_rank=override_min_rank,
                    override_max_rank=override_max_rank,
                    parent_template_position=parent_template_position,
                    **filtered_data
                )
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"Role with id '{role_id}' does not exist")

        return template

    def update(self, instance, validated_data):
        template_positions_data = validated_data.pop('template_positions', None)
        allowed_branches = validated_data.pop('allowed_branches', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update allowed branches if provided
        if allowed_branches is not None:
            instance.allowed_branches.set(allowed_branches)

        # Update template positions if provided
        if template_positions_data is not None:
            # Delete existing template positions
            instance.template_positions.all().delete()

            # Create new template positions
            for tp_data in template_positions_data:
                try:
                    # Convert role ID to Role instance
                    role_id = tp_data.pop('role')
                    role = Role.objects.get(id=role_id)

                    # Handle optional rank foreign keys
                    override_min_rank_id = tp_data.pop('override_min_rank', None)
                    override_max_rank_id = tp_data.pop('override_max_rank', None)

                    override_min_rank = None
                    override_max_rank = None

                    if override_min_rank_id:
                        try:
                            override_min_rank = Rank.objects.get(id=override_min_rank_id)
                        except Rank.DoesNotExist:
                            pass

                    if override_max_rank_id:
                        try:
                            override_max_rank = Rank.objects.get(id=override_max_rank_id)
                        except Rank.DoesNotExist:
                            pass

                    # Handle parent template position if provided
                    parent_template_position_id = tp_data.pop('parent_template_position', None)
                    parent_template_position = None
                    if parent_template_position_id:
                        try:
                            parent_template_position = TemplatePosition.objects.get(id=parent_template_position_id)
                        except TemplatePosition.DoesNotExist:
                            pass

                    # Remove any unexpected fields to prevent errors
                    allowed_fields = {
                        'naming_pattern', 'identifier_pattern', 'quantity',
                        'display_order', 'additional_config'
                    }
                    filtered_data = {k: v for k, v in tp_data.items() if k in allowed_fields}

                    TemplatePosition.objects.create(
                        template=instance,
                        role=role,
                        override_min_rank=override_min_rank,
                        override_max_rank=override_max_rank,
                        parent_template_position=parent_template_position,
                        **filtered_data
                    )
                except Role.DoesNotExist:
                    raise serializers.ValidationError(f"Role with id '{role_id}' does not exist")

        return instance

class ApplyTemplateSerializer(serializers.Serializer):
    """Serializer for applying a template to a unit"""
    template_id = serializers.UUIDField()
    unit_id = serializers.UUIDField()
    preview_only = serializers.BooleanField(default=False)
    position_overrides = serializers.DictField(
        child=serializers.DictField(),
        required=False,
        help_text="Override specific positions in the template"
    )

    def validate(self, data):
        # Validate template exists
        try:
            template = PositionTemplate.objects.get(id=data['template_id'])
        except PositionTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found")

        # Validate unit exists
        try:
            unit = Unit.objects.get(id=data['unit_id'])
        except Unit.DoesNotExist:
            raise serializers.ValidationError("Unit not found")

        # Check if template is applicable to unit type
        if template.applicable_unit_types and unit.unit_type not in template.applicable_unit_types:
            raise serializers.ValidationError(
                f"Template is not applicable to unit type '{unit.unit_type}'"
            )

        # Check branch restrictions
        if template.allowed_branches.exists() and unit.branch not in template.allowed_branches.all():
            raise serializers.ValidationError(
                "Template is not allowed for this unit's branch"
            )

        data['template'] = template
        data['unit'] = unit
        return data


class TemplatePreviewSerializer(serializers.Serializer):
    """Serializer for template preview results"""
    positions = serializers.ListField(
        child=serializers.DictField()
    )
    hierarchy = serializers.DictField()
    summary = serializers.DictField()