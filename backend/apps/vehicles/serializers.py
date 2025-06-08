# backend/apps/vehicles/serializers.py
from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    assigned_unit_name = serializers.ReadOnlyField(source='assigned_unit.name', default=None)

    class Meta:
        model = Vehicle
        fields = '__all__'