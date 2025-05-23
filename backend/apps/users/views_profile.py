from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserProfileDetailSerializer
from apps.units.models import UserPosition
from apps.training.models import UserCertificate
from apps.events.models import EventAttendance, Event
from apps.ships.models import Ship
from apps.units.serializers import UserPositionSerializer
from apps.training.serializers import UserCertificateSerializer
from apps.events.serializers import EventAttendanceSerializer
from apps.ships.serializers import ShipListSerializer
from django.utils import timezone
from django.db.models import Q

from .serializers import UserProfileSerializer

User = get_user_model()


class UserProfileDetailView(APIView):
    """
    Get comprehensive user profile data with all related objects expanded
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        # If no pk provided, use current user
        if pk is None or pk == 'me':
            user = request.user
        else:
            user = get_object_or_404(User, pk=pk)

        # Get user data with expanded relations
        user_data = UserProfileDetailSerializer(user).data

        # Get user positions with full details
        positions = UserPosition.objects.filter(user=user).select_related(
            'position', 'unit', 'position__unit__branch'
        ).order_by('-assignment_date')
        positions_data = UserPositionSerializer(positions, many=True).data

        # Get user certificates with full details
        certificates = UserCertificate.objects.filter(
            user=user
        ).select_related(
            'certificate', 'issuer', 'training_event'
        ).order_by('-issue_date')
        certificates_data = UserCertificateSerializer(certificates, many=True).data

        # Get user event attendance with event details
        event_attendances = EventAttendance.objects.filter(
            user=user
        ).select_related(
            'event', 'event__host_unit'
        ).order_by('-event__start_time')
        events_data = []

        for attendance in event_attendances:
            event_dict = {
                'id': attendance.event.id,
                'title': attendance.event.title,
                'description': attendance.event.description,
                'event_type': attendance.event.event_type,
                'start_time': attendance.event.start_time,
                'end_time': attendance.event.end_time,
                'location': attendance.event.location,
                'host_unit': {
                    'id': attendance.event.host_unit.id,
                    'name': attendance.event.host_unit.name,
                    'abbreviation': attendance.event.host_unit.abbreviation
                } if attendance.event.host_unit else None,
                'status': attendance.event.status,
                'is_mandatory': attendance.event.is_mandatory,
                'attendance_status': attendance.status,
                'response_time': attendance.response_time,
                'check_in_time': attendance.check_in_time,
                'check_out_time': attendance.check_out_time,
                'performance_rating': attendance.performance_rating
            }
            events_data.append(event_dict)

        # Get user ships
        ships = Ship.objects.filter(owner=user).select_related('assigned_unit')
        ships_data = ShipListSerializer(ships, many=True).data

        # Calculate statistics
        days_in_service = (timezone.now() - user.join_date).days if user.join_date else 0
        completed_ops = EventAttendance.objects.filter(
            user=user,
            event__status='Completed'
        ).count()
        upcoming_ops = EventAttendance.objects.filter(
            user=user,
            event__start_time__gt=timezone.now()
        ).count()

        response_data = {
            'user': user_data,
            'positions': positions_data,
            'certificates': certificates_data,
            'events': events_data,
            'ships': ships_data,
            'statistics': {
                'days_in_service': days_in_service,
                'completed_operations': completed_ops,
                'upcoming_operations': upcoming_ops,
                'total_certificates': len(certificates_data),
                'active_certificates': len([c for c in certificates_data if c['is_active']]),
                'total_ships': len(ships_data),
                'approved_ships': len([s for s in ships_data if s['approval_status'] == 'Approved'])
            }
        }

        return Response(response_data)


class UserRankProgressionView(APIView):
    """
    Get user's rank progression history
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # For now, return current rank only
        # In a full implementation, you'd track rank history
        progression = []
        if user.current_rank:
            progression.append({
                'rank': {
                    'id': user.current_rank.id,
                    'name': user.current_rank.name,
                    'abbreviation': user.current_rank.abbreviation,
                    'tier': user.current_rank.tier,
                    'insignia_image_url': user.current_rank.insignia_image_url
                },
                'date_achieved': user.join_date,  # Placeholder
                'is_current': True
            })

        return Response({
            'user_id': user.id,
            'current_rank': UserProfileSerializer(user).data.get('rank'),
            'progression': progression
        })


class UserUnitHistoryView(APIView):
    """
    Get user's unit assignment history
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # Get all positions ordered by assignment date
        positions = UserPosition.objects.filter(user=user).select_related(
            'position', 'unit', 'unit__branch'
        ).order_by('-assignment_date')

        history = []
        for pos in positions:
            history.append({
                'id': pos.id,
                'unit': {
                    'id': pos.unit.id,
                    'name': pos.unit.name,
                    'abbreviation': pos.unit.abbreviation,
                    'unit_type': pos.unit.unit_type,
                    'emblem_url': pos.unit.emblem_url,
                    'description': pos.unit.description
                },
                'position': {
                    'id': pos.position.id,
                    'title': pos.position.title,
                    'abbreviation': pos.position.abbreviation,
                    'is_command_position': pos.position.is_command_position,
                    'is_staff_position': pos.position.is_staff_position
                },
                'assignment_date': pos.assignment_date,
                'status': pos.status,
                'is_primary': pos.is_primary,
                'order_number': pos.order_number
            })

        return Response({
            'user_id': user.id,
            'history': history
        })