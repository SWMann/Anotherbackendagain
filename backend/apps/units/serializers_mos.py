from rest_framework import serializers
from .models import MOS
from apps.training.serializers import TrainingCertificateSerializer
from apps.units.serializers import UnitListSerializer


class MOSListSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    holders_count = serializers.SerializerMethodField()

    class Meta:
        model = MOS
        fields = [
            'id', 'code', 'title', 'branch', 'branch_name',
            'category', 'is_active', 'is_entry_level',
            'ait_weeks', 'holders_count'
        ]

    def get_holders_count(self, obj):
        return obj.primary_holders.filter(is_active=True).count()


class MOSDetailSerializer(serializers.ModelSerializer):
    branch = serializers.SerializerMethodField()
    required_certifications = TrainingCertificateSerializer(many=True, read_only=True)
    related_mos = MOSListSerializer(many=True, read_only=True)
    authorized_units = serializers.SerializerMethodField()

    class Meta:
        model = MOS
        fields = '__all__'

    def get_branch(self, obj):
        return {
            'id': obj.branch.id,
            'name': obj.branch.name,
            'abbreviation': obj.branch.abbreviation
        }

    def get_authorized_units(self, obj):
        units = obj.authorized_units.filter(is_active=True)
        return UnitListSerializer(units, many=True).data


class MOSCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOS
        fields = '__all__'