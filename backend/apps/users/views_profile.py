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

# Try to import UserRankHistory, but don't fail if it doesn't exist yet
try:
    from apps.units.models_promotion import UserRankHistory
    from apps.units.serializers_promotion import UserRankHistorySerializer

    RANK_HISTORY_AVAILABLE = True
except ImportError:
    RANK_HISTORY_AVAILABLE = False

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

        # Ensure we prefetch the related rank data
        user = User.objects.select_related(
            'current_rank',
            'primary_unit',
            'branch',
        ).get(pk=user.pk)

        # Get user data with expanded relations - pass request context
        user_data = UserProfileDetailSerializer(user, context={'request': request}).data

        # Get user's rank history if available
        rank_history_data = []
        if RANK_HISTORY_AVAILABLE:
            rank_history = UserRankHistory.objects.filter(user=user).select_related(
                'rank', 'rank__branch', 'promoted_by'
            ).order_by('-date_assigned')

            # Serialize rank history with request context for proper URL generation
            for history_entry in rank_history:
                rank_data = {
                    'id': history_entry.id,
                    'rank': {
                        'id': history_entry.rank.id,
                        'name': history_entry.rank.name,
                        'abbreviation': history_entry.rank.abbreviation,
                        'tier': history_entry.rank.tier,
                        'insignia_image_url': history_entry.rank.insignia_display_url if hasattr(history_entry.rank,
                                                                                                 'insignia_display_url') else history_entry.rank.insignia_image_url,
                        'is_officer': history_entry.rank.is_officer,
                        'is_enlisted': history_entry.rank.is_enlisted,
                        'is_warrant': history_entry.rank.is_warrant,
                        'branch': {
                            'id': history_entry.rank.branch.id,
                            'name': history_entry.rank.branch.name,
                            'abbreviation': history_entry.rank.branch.abbreviation
                        } if history_entry.rank.branch else None
                    },
                    'date_assigned': history_entry.date_assigned,
                    'date_ended': history_entry.date_ended,
                    'promoted_by': {
                        'id': history_entry.promoted_by.id,
                        'username': history_entry.promoted_by.username
                    } if history_entry.promoted_by else None,
                    'promotion_order': history_entry.promotion_order,
                    'notes': history_entry.notes,
                    'duration_days': ((
                                          history_entry.date_ended if history_entry.date_ended else timezone.now()) - history_entry.date_assigned).days if history_entry.date_assigned else 0,
                    'is_current': history_entry.date_ended is None
                }
                rank_history_data.append(rank_data)

        # If no rank history exists but user has a current rank, create a synthetic entry
        if not rank_history_data and user.current_rank:
            rank_history_data.append({
                'id': None,
                'rank': {
                    'id': user.current_rank.id,
                    'name': user.current_rank.name,
                    'abbreviation': user.current_rank.abbreviation,
                    'tier': user.current_rank.tier,
                    'insignia_image_url': user.current_rank.insignia_display_url if hasattr(user.current_rank,
                                                                                            'insignia_display_url') else user.current_rank.insignia_image_url,
                    'is_officer': user.current_rank.is_officer,
                    'is_enlisted': user.current_rank.is_enlisted,
                    'is_warrant': user.current_rank.is_warrant,
                    'branch': {
                        'id': user.current_rank.branch.id,
                        'name': user.current_rank.branch.name,
                        'abbreviation': user.current_rank.branch.abbreviation
                    } if user.current_rank.branch else None
                },
                'date_assigned': user.join_date,
                'date_ended': None,
                'promoted_by': None,
                'promotion_order': None,
                'notes': 'Initial rank assignment',
                'duration_days': (timezone.now() - user.join_date).days if user.join_date else 0,
                'is_current': True
            })

        # Get user positions with full details
        positions = UserPosition.objects.filter(user=user).select_related(
            'position', 'position__role', 'position__unit', 'position__unit__branch'
        ).order_by('-assignment_date')
        positions_data = UserPositionSerializer(positions, many=True, context={'request': request}).data

        # Get user certificates with full details
        certificates = UserCertificate.objects.filter(
            user=user
        ).select_related(
            'certificate', 'issuer', 'training_event'
        ).order_by('-issue_date')
        certificates_data = UserCertificateSerializer(certificates, many=True, context={'request': request}).data

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
        ships_data = ShipListSerializer(ships, many=True, context={'request': request}).data

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
            'rank_history': rank_history_data,
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
                'approved_ships': len([s for s in ships_data if s['approval_status'] == 'Approved']),
                'total_ranks_held': len(rank_history_data),
                'days_at_current_rank': rank_history_data[0]['duration_days'] if rank_history_data and
                                                                                 rank_history_data[0][
                                                                                     'is_current'] else 0
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

        progression = []

        if RANK_HISTORY_AVAILABLE:
            # Get actual rank history
            rank_history = UserRankHistory.objects.filter(user=user).select_related(
                'rank', 'rank__branch', 'promoted_by'
            ).order_by('date_assigned')  # Chronological order for progression

            for history in rank_history:
                # Get the proper insignia URL
                insignia_url = None
                if hasattr(history.rank, 'insignia_display_url'):
                    insignia_url = history.rank.insignia_display_url
                elif history.rank.insignia_image:
                    try:
                        insignia_url = history.rank.insignia_image.url
                    except:
                        insignia_url = history.rank.insignia_image_url
                else:
                    insignia_url = history.rank.insignia_image_url

                progression.append({
                    'rank': {
                        'id': history.rank.id,
                        'name': history.rank.name,
                        'abbreviation': history.rank.abbreviation,
                        'tier': history.rank.tier,
                        'insignia_image_url': insignia_url,
                        'is_officer': history.rank.is_officer,
                        'is_enlisted': history.rank.is_enlisted,
                        'is_warrant': history.rank.is_warrant
                    },
                    'date_achieved': history.date_assigned,
                    'date_ended': history.date_ended,
                    'promoted_by': {
                        'id': history.promoted_by.id,
                        'username': history.promoted_by.username
                    } if history.promoted_by else None,
                    'duration_days': ((
                                          history.date_ended if history.date_ended else timezone.now()) - history.date_assigned).days if history.date_assigned else 0,
                    'is_current': history.date_ended is None,
                    'notes': history.notes,
                    'promotion_order': history.promotion_order
                })

        # If no history but user has current rank, create synthetic entry
        if not progression and user.current_rank:
            insignia_url = None
            if hasattr(user.current_rank, 'insignia_display_url'):
                insignia_url = user.current_rank.insignia_display_url
            elif user.current_rank.insignia_image:
                try:
                    insignia_url = user.current_rank.insignia_image.url
                except:
                    insignia_url = user.current_rank.insignia_image_url
            else:
                insignia_url = user.current_rank.insignia_image_url

            progression.append({
                'rank': {
                    'id': user.current_rank.id,
                    'name': user.current_rank.name,
                    'abbreviation': user.current_rank.abbreviation,
                    'tier': user.current_rank.tier,
                    'insignia_image_url': insignia_url,
                    'is_officer': user.current_rank.is_officer,
                    'is_enlisted': user.current_rank.is_enlisted,
                    'is_warrant': user.current_rank.is_warrant
                },
                'date_achieved': user.join_date,
                'date_ended': None,
                'promoted_by': None,
                'duration_days': (timezone.now() - user.join_date).days if user.join_date else 0,
                'is_current': True,
                'notes': 'Initial rank assignment',
                'promotion_order': None
            })

        return Response({
            'user_id': user.id,
            'current_rank': UserProfileSerializer(user, context={'request': request}).data.get('rank'),
            'progression': progression,
            'total_promotions': len(progression) - 1 if len(progression) > 0 else 0
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
            'position', 'position__role', 'position__unit', 'position__unit__branch'
        ).order_by('-assignment_date')

        history = []
        for pos in positions:
            history.append({
                'id': pos.id,
                'unit': {
                    'id': pos.position.unit.id,
                    'name': pos.position.unit.name,
                    'abbreviation': pos.position.unit.abbreviation,
                    'unit_type': pos.position.unit.unit_type,
                    'emblem_url': pos.position.unit.emblem_url,
                    'description': pos.position.unit.description
                } if pos.position.unit else None,
                'position': {
                    'id': pos.position.id,
                    'title': pos.position.display_title,
                    'role_name': pos.position.role.name if pos.position.role else None,
                    'is_command_role': pos.position.role.is_command_role if pos.position.role else False,
                    'is_staff_role': pos.position.role.is_staff_role if pos.position.role else False
                },
                'assignment_date': pos.assignment_date,
                'status': pos.status,
                'assignment_type': pos.assignment_type,
                'order_number': pos.order_number
            })

        return Response({
            'user_id': user.id,
            'history': history
        })