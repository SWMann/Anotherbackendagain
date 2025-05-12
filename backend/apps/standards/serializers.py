from rest_framework import serializers
from .models import StandardGroup, StandardSubGroup, Standard


class StandardGroupListSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name', default=None)
    subgroups_count = serializers.SerializerMethodField()

    class Meta:
        model = StandardGroup
        fields = ['id', 'name', 'description', 'icon_url', 'branch', 'branch_name',
                  'order_index', 'is_active', 'subgroups_count']

    def get_subgroups_count(self, obj):
        return obj.subgroups.count()


class StandardGroupDetailSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name', default=None)
    created_by_username = serializers.ReadOnlyField(source='created_by.username', default=None)

    class Meta:
        model = StandardGroup
        fields = '__all__'


class StandardSubGroupSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source='standard_group.name')
    standards_count = serializers.SerializerMethodField()

    class Meta:
        model = StandardSubGroup
        fields = '__all__'

    def get_standards_count(self, obj):
        return obj.standards.count()


class StandardListSerializer(serializers.ModelSerializer):
    subgroup_name = serializers.ReadOnlyField(source='standard_sub_group.name')
    group_name = serializers.ReadOnlyField(source='standard_sub_group.standard_group.name')
    author_username = serializers.ReadOnlyField(source='author.username', default=None)

    class Meta:
        model = Standard
        fields = ['id', 'title', 'document_number', 'standard_sub_group', 'subgroup_name',
                  'group_name', 'summary', 'version', 'status', 'author_username',
                  'effective_date', 'difficulty_level', 'is_required']


class StandardDetailSerializer(serializers.ModelSerializer):
    subgroup_name = serializers.ReadOnlyField(source='standard_sub_group.name')
    group_name = serializers.ReadOnlyField(source='standard_sub_group.standard_group.name')
    author_username = serializers.ReadOnlyField(source='author.username', default=None)
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username', default=None)

    class Meta:
        model = Standard
        fields = '__all__'


class StandardApproveSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('Active', 'Active'),
        ('Draft', 'Draft'),
        ('Archived', 'Archived')
    ])
    effective_date = serializers.DateTimeField(required=False, allow_null=True)
    review_date = serializers.DateTimeField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)