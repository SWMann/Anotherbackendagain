from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, EventAttendance
from .serializers import (
    EventListSerializer, EventDetailSerializer, EventAttendanceSerializer,
    EventAttendanceUpdateSerializer, EventCalendarSerializer, EventRSVPSerializer
)
from apps.users.views import IsAdminOrReadOnly


class IsCreatorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an event or admins to edit it
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user or request.user.is_admin


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['host_unit', 'event_type', 'status', 'is_mandatory', 'is_public']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['start_time']
    permission_classes = [IsCreatorOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def attendance(self, request, pk=None):
        event = self.get_object()
        attendances = event.attendances.all()
        serializer = EventAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def attend(self, request, pk=None):
        event = self.get_object()
        user = request.user

        serializer = EventRSVPSerializer(data=request.data)
        if serializer.is_valid():
            status_value = serializer.validated_data['status']
            feedback = serializer.validated_data.get('feedback', '')

            # Get or create attendance record
            attendance, created = EventAttendance.objects.get_or_create(
                event=event,
                user=user,
                defaults={
                    'status': status_value,
                    'feedback': feedback
                }
            )

            # Update if it already existed
            if not created:
                attendance.status = status_value
                attendance.feedback = feedback
                attendance.response_time = timezone.now()
                attendance.save()

            return Response({
                'id': attendance.id,
                'status': attendance.status,
                'response_time': attendance.response_time
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def upcoming(self, request):
        """Get upcoming events."""
        now = timezone.now()
        upcoming_events = Event.objects.filter(
            start_time__gte=now
        ).order_by('start_time')[:10]

        serializer = EventListSerializer(upcoming_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def calendar(self, request):
        """Get events formatted for calendar view."""
        # Get date range from query params
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        events = Event.objects.all()

        if start_date:
            events = events.filter(end_time__gte=start_date)
        if end_date:
            events = events.filter(start_time__lte=end_date)

        serializer = EventCalendarSerializer(events, many=True)
        return Response(serializer.data)