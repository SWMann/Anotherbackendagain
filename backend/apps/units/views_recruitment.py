from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, F, Q  # Add missing imports
from .models import Position, UserPosition, Unit, RecruitmentSlot
from .serializers import (
    PositionListSerializer, PositionDetailSerializer,
    UserPositionSerializer, UserPositionCreateSerializer
)
from apps.users.views import IsAdminOrReadOnly


class RecruitmentStatusViewSet(viewsets.ViewSet):
    """
    Provide recruitment status for application portal
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def brigades(self, request):
        """Get all brigades with recruitment status"""
        brigades = Unit.objects.filter(
            unit_type='Brigade',
            is_active=True
        ).prefetch_related('authorized_mos', 'mos_training_capability')
        print(brigades)
        data = []
        for brigade in brigades:
            # Get all units under this brigade (including the brigade itself)
            # This includes all descendant units at any level
            descendant_units = Unit.objects.filter(
                Q(id=brigade.id) |  # Include the brigade itself
                Q(parent_unit=brigade) |  # Direct children (battalions)
                Q(parent_unit__parent_unit=brigade) |  # Grandchildren (companies)
                Q(parent_unit__parent_unit__parent_unit=brigade) |  # Great-grandchildren (platoons)
                Q(parent_unit__parent_unit__parent_unit__parent_unit=brigade)  # Great-great-grandchildren (teams/squads)
            ).values_list('id', flat=True)
            print(descendant_units)

            # Calculate total available slots for all units under this brigade
            available_slots = RecruitmentSlot.objects.filter(
                unit__id__in=descendant_units,
                is_active=True
            ).aggregate(
                total=Sum(F('total_slots') - F('filled_slots') - F('reserved_slots'))
            )['total'] or 0
            print(available_slots)
            authorized_mos = brigade.authorized_mos.filter(is_active=True)
            training_mos = brigade.mos_training_capability.filter(is_active=True)

            data.append({
                'id': str(brigade.id),  # Ensure UUID is serialized as string
                'name': brigade.name,
                'abbreviation': brigade.abbreviation,
                'motto': brigade.motto,
                'description': brigade.description,
                'unit_type': brigade.unit_type,
                'recruitment_status': brigade.recruitment_status,
                'available_slots': available_slots,
                'is_aviation_only': brigade.is_aviation_only,
                'emblem_url': brigade.emblem_url,
                'recruitment_notes': brigade.recruitment_notes
                'authorized_mos': [
                    {'id': mos.id, 'code': mos.code, 'title': mos.title}
                    for mos in authorized_mos
                ],
                'training_mos': [
                    {'id': mos.id, 'code': mos.code, 'title': mos.title}
                    for mos in training_mos
                ],
                'mos_categories': list(authorized_mos.values_list('category', flat=True).distinct())
            })

        return Response(data)

    @action(detail=True, methods=['get'])
    def platoons(self, request, pk):
        """Get platoons for a specific brigade"""
        print(pk)
        brigade = get_object_or_404(Unit, pk=pk)
        print(brigade)
        # Get all platoons under this brigade
        platoons = Unit.objects.filter(
            unit_type='Platoon',
            is_active=True
        ).filter(
            # Complex query to get all platoons under brigade
            Q(parent_unit__parent_unit__parent_unit=brigade) |  # Brigade->Battalion->Company->Platoon
            Q(parent_unit__parent_unit=brigade)  # Brigade->Battalion->Platoon (for special units)
        ).select_related(
            'parent_unit',  # Company
            'parent_unit__parent_unit'  # Battalion
        ).prefetch_related('recruitment_slots')

        data = []
        for platoon in platoons:
            # Get slot information
            slots = platoon.recruitment_slots.filter(is_active=True)
            total_available = sum(slot.available_slots for slot in slots)

            # Get current strength
            current_strength = UserPosition.objects.filter(
                position__unit=platoon,
                status='active'
            ).count()

            # Get platoon leader
            leader_position = platoon.positions.filter(
                role__is_command_role=True,
                is_active=True
            ).first()

            leader_name = "Vacant"
            if leader_position and not leader_position.is_vacant:
                leader_assignment = leader_position.assignments.filter(
                    status='active',
                    assignment_type='primary'
                ).first()
                if leader_assignment and leader_assignment.user.current_rank:
                    leader_name = f"{leader_assignment.user.current_rank.abbreviation} {leader_assignment.user.username}"

            data.append({
                'id': str(platoon.id),  # Ensure UUID is serialized as string
                'designation': platoon.unit_designation,
                'unit_type': platoon.unit_type,
                'company': platoon.parent_unit.name if platoon.parent_unit else None,
                'battalion': platoon.parent_unit.parent_unit.name if platoon.parent_unit and platoon.parent_unit.parent_unit else None,
                'current_strength': current_strength,
                'max_strength': platoon.max_personnel,
                'available_slots': total_available,
                'leader': leader_name,
                'recruitment_status': platoon.recruitment_status,
                'is_accepting_applications': platoon.is_accepting_applications(),
                'career_tracks_available': list(slots.values_list('career_track', flat=True).distinct())
            })

        return Response(data)