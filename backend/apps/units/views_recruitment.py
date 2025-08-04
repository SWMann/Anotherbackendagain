# backend/apps/units/views_recruitment.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, F, Q
from .models import Position, UserPosition, Unit, RecruitmentSlot
from .serializers import (
    PositionListSerializer, PositionDetailSerializer,
    UserPositionSerializer, UserPositionCreateSerializer
)
from apps.users.views import IsAdminOrReadOnly


class RecruitmentStatusViewSet(viewsets.ViewSet):
    """
    Provide recruitment status for application portal
    Updated for new Navy/Marines/Army structure
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def brigades(self, request):
        """
        Get all recruitment units (Squadrons for Navy, Companies for Army/Marines)
        Keeping the method name for backwards compatibility
        """
        # Get all Squadron and Company level units
        units = Unit.objects.filter(
            Q(unit_level='squadron') | Q(unit_level='company'),
            is_active=True
        ).prefetch_related('authorized_mos', 'mos_training_capability').select_related('branch')

        data = []
        for unit in units:
            # Get all units under this unit (including the unit itself)
            descendant_units = self._get_all_descendant_unit_ids(unit)

            # Calculate total available slots for all units under this unit
            available_slots = RecruitmentSlot.objects.filter(
                unit__id__in=descendant_units,
                is_active=True
            ).aggregate(
                total=Sum(F('total_slots') - F('filled_slots') - F('reserved_slots'))
            )['total'] or 0

            authorized_mos = unit.authorized_mos.filter(is_active=True)
            training_mos = unit.mos_training_capability.filter(is_active=True)

            # Determine branch type for UI
            branch_type = 'unknown'
            if unit.branch:
                if 'navy' in unit.branch.name.lower():
                    if 'aviation' in unit.branch.name.lower():
                        branch_type = 'navy_aviation'
                    else:
                        branch_type = 'navy'
                elif 'army' in unit.branch.name.lower():
                    branch_type = 'army'
                elif 'marine' in unit.branch.name.lower():
                    branch_type = 'marines'

            data.append({
                'id': str(unit.id),
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'motto': unit.motto,
                'description': unit.description,
                'unit_type': unit.unit_level,  # Will be 'squadron' or 'company'
                'branch_type': branch_type,
                'branch_name': unit.branch.name if unit.branch else None,
                'recruitment_status': unit.recruitment_status,
                'available_slots': available_slots,
                'is_aviation_only': unit.is_aviation_only,
                'emblem_url': unit.emblem_url,
                'recruitment_notes': unit.recruitment_notes,
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
        """
        Get subunits for a specific unit (Divisions for Navy, Platoons for Army/Marines)
        Keeping the method name for backwards compatibility
        """
        unit = get_object_or_404(Unit, pk=pk)

        # Determine what type of subunits to look for based on parent unit type
        if unit.unit_level == 'squadron':
            # Navy Squadron -> get Divisions
            subunit_type = 'division'
        elif unit.unit_level == 'company':
            # Army/Marine Company -> get Platoons
            subunit_type = 'platoon'
        else:
            # Fallback - try to get any direct children
            subunits = Unit.objects.filter(
                parent_unit=unit,
                is_active=True
            ).select_related('parent_unit').prefetch_related('recruitment_slots')

        if unit.unit_level in ['squadron', 'company']:
            # Get specific type of subunits
            subunits = Unit.objects.filter(
                parent_unit=unit,
                unit_level=subunit_type,
                is_active=True
            ).select_related('parent_unit').prefetch_related('recruitment_slots')

        data = []
        for subunit in subunits:
            # Get slot information
            slots = subunit.recruitment_slots.filter(is_active=True)
            total_available = sum(slot.available_slots for slot in slots)

            # Get current strength
            current_strength = UserPosition.objects.filter(
                position__unit=subunit,
                status='active'
            ).count()

            # Get unit leader
            leader_position = subunit.positions.filter(
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

            # Determine the parent hierarchy names
            company = None
            battalion = None

            if subunit.unit_level == 'platoon':
                # For Army/Marines platoons
                company = subunit.parent_unit.name if subunit.parent_unit else None
                battalion = subunit.parent_unit.parent_unit.name if subunit.parent_unit and subunit.parent_unit.parent_unit else None
            elif subunit.unit_level == 'division':
                # For Navy divisions - adapt the structure
                company = subunit.parent_unit.name if subunit.parent_unit else None  # Squadron
                battalion = subunit.parent_unit.parent_unit.name if subunit.parent_unit and subunit.parent_unit.parent_unit else None  # Taskforce

            data.append({
                'id': str(subunit.id),
                'designation': subunit.unit_designation or subunit.name,
                'unit_type': subunit.unit_level,
                'company': company,  # Company for Army/Marines, Squadron for Navy
                'battalion': battalion,  # Battalion for Army/Marines, Taskforce for Navy
                'current_strength': current_strength,
                'max_strength': subunit.max_personnel,
                'available_slots': total_available,
                'leader': leader_name,
                'recruitment_status': subunit.recruitment_status,
                'is_accepting_applications': subunit.is_accepting_applications(),
                'career_tracks_available': list(slots.values_list('career_track', flat=True).distinct())
            })

        return Response(data)

    def _get_all_descendant_unit_ids(self, unit):
        """
        Recursively get all descendant unit IDs
        More efficient than the previous implementation
        """
        descendant_ids = [unit.id]

        # Get all descendants in a more efficient way
        children = Unit.objects.filter(parent_unit=unit, is_active=True).values_list('id', flat=True)
        descendant_ids.extend(children)

        # Get grandchildren and beyond
        current_level = list(children)
        while current_level:
            next_level = Unit.objects.filter(
                parent_unit__id__in=current_level,
                is_active=True
            ).values_list('id', flat=True)
            descendant_ids.extend(next_level)
            current_level = list(next_level)

        return descendant_ids