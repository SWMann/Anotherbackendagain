from rest_framework import serializers
from .models import OperationOrder


class OperationOrderListSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator.username')
    event_title = serializers.ReadOnlyField(source='event.title', default=None)

    class Meta:
        model = OperationOrder
        fields = ['id', 'operation_name', 'event', 'event_title', 'creator_username',
                  'approval_status', 'classification', 'version', 'created_at']


class OperationOrderDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator.username')
    creator_avatar = serializers.ReadOnlyField(source='creator.avatar_url')
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username', default=None)
    event_title = serializers.ReadOnlyField(source='event.title', default=None)
    event_start_time = serializers.ReadOnlyField(source='event.start_time', default=None)

    class Meta:
        model = OperationOrder
        fields = '__all__'


class OperationOrderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationOrder
        fields = [
            'operation_name', 'event', 'situation', 'mission', 'execution',
            'service_support', 'command_signal', 'attachments',
            'approval_status', 'classification', 'version'
        ]


class OperationOrderApprovalSerializer(serializers.Serializer):
    approval_status = serializers.ChoiceField(choices=[
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])
    comment = serializers.CharField(required=False, allow_blank=True)