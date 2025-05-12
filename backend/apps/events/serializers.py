from rest_framework import serializers
from .models import Event, EventAttendance
from django.contrib.auth import get_user_model

User = get_user_model()


class EventListSerializer(serializers.ModelSerializer):
    host_unit_name = serializers.ReadOnlyField(source='host_unit.name')
    creator_username = serializers.ReadOnlyField(source='creator.username')
    attendees_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'event_type', 'start_time', 'end_time',
                  'location', 'host_unit', 'host_unit_name', 'creator_username',
                  'image_url', 'is_mandatory', 'status', 'attendees_count']

    def get_attendees_count(self, obj):
        return obj.attendances.filter(status='Attending').count()


class EventDetailSerializer(serializers.ModelSerializer):
    host_unit_name = serializers.ReadOnlyField(source='host_unit.name')
    creator_username = serializers.ReadOnlyField(source='creator.username')
    creator_avatar = serializers.ReadOnlyField(source='creator.avatar_url')
    operation_order_name = serializers.ReadOnlyField(source='operation_order.operation_name', default=None)
    attending_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_attending_count(self, obj):
        return obj.attendances.filter(status='Attending').count()


class EventAttendanceSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')
    event_start = serializers.ReadOnlyField(source='event.start_time')
    event_end = serializers.ReadOnlyField(source='event.end_time')
    user_username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.ReadOnlyField(source='user.avatar_url')

    class Meta:
        model = EventAttendance
        fields = '__all__'


class EventAttendanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendance
        fields = ['status', 'feedback']


class EventCalendarSerializer(serializers.ModelSerializer):
    host_unit_name = serializers.ReadOnlyField(source='host_unit.name')
    host_unit_color = serializers.ReadOnlyField(source='host_unit.branch.color_code')

    class Meta:
        model = Event
        fields = ['id', 'title', 'start_time', 'end_time', 'event_type',
                  'host_unit_name', 'host_unit_color', 'is_mandatory', 'status']


class EventRSVPSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('Attending', 'Attending'),
        ('Declined', 'Declined'),
        ('Maybe', 'Maybe'),
        ('Excused', 'Excused')
    ])
    feedback = serializers.CharField(required=False, allow_blank=True)