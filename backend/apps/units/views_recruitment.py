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
        # Get Squadron level units for Navy/Aviation and Company level for Ground Forces
        units = Unit.objects.filter(
            Q(unit_level='navy_squadron') |
            Q(unit_level='aviation_squadron') |
            Q(unit_level='ground_company'),
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

            # Determine branch type based on unit_level prefix
            branch_type = 'unknown'
            if unit.unit_level.startswith('navy_'):
                branch_type = 'navy'
            elif unit.unit_level.startswith('aviation_'):
                branch_type = 'navy_aviation'
            elif unit.unit_level.startswith('ground_'):
                # Further differentiate between Army and Marines based on branch name
                if unit.branch and 'marine' in unit.branch.name.lower():
                    branch_type = 'marines'
                else:
                    branch_type = 'army'

            data.append({
                'id': str(unit.id),
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'motto': unit.motto,
                'description': unit.description,
                'unit_type': unit.unit_level,
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
        subunit_type = None
        if unit.unit_level == 'navy_squadron':
            subunit_type = 'navy_division'
        elif unit.unit_level == 'aviation_squadron':
            subunit_type = 'aviation_division'
        elif unit.unit_level == 'ground_company':
            subunit_type = 'ground_platoon'

        if subunit_type:
            # Get specific type of subunits
            subunits = Unit.objects.filter(
                parent_unit=unit,
                unit_level=subunit_type,
                is_active=True
            ).select_related('parent_unit').prefetch_related('recruitment_slots')
        else:
            # Fallback - get any direct children
            subunits = Unit.objects.filter(
                parent_unit=unit,
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

            # Determine the parent hierarchy names based on unit type
            company = None
            battalion = None

            if subunit.unit_level == 'ground_platoon':
                # For Army/Marines platoons
                company = subunit.parent_unit.name if subunit.parent_unit else None
                battalion = subunit.parent_unit.parent_unit.name if subunit.parent_unit and subunit.parent_unit.parent_unit else None
            elif subunit.unit_level in ['navy_division', 'aviation_division']:
                # For Navy/Aviation divisions
                company = subunit.parent_unit.name if subunit.parent_unit else None  # Squadron
                # Find the task force or air group (parent of squadron)
                if subunit.parent_unit and subunit.parent_unit.parent_unit:
                    battalion = subunit.parent_unit.parent_unit.name

            data.append({
                'id': str(subunit.id),
                'designation': subunit.unit_designation or subunit.name,
                'unit_type': subunit.unit_level,
                'company': company,  # Company for Army/Marines, Squadron for Navy
                'battalion': battalion,  # Battalion for Army/Marines, Task Force for Navy
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

    @action(detail=False, methods=['get'])
    def branch_structure(self, request):
        """
        Get the structure information for each branch with proper value codes
        """
        return Response({
            'navy': {
                'name': 'Navy',
                'recruitment_level': 'navy_squadron',
                'subunit_level': 'navy_division',
                'structure': [
                    {'value': 'navy_expeditionary_force', 'label': 'Expeditionary Force'},
                    {'value': 'navy_fleet', 'label': 'Fleet'},
                    {'value': 'navy_battle_group', 'label': 'Battle Group'},
                    {'value': 'navy_task_force', 'label': 'Task Force'},
                    {'value': 'navy_squadron', 'label': 'Squadron'},
                    {'value': 'navy_division', 'label': 'Division'},
                    {'value': 'navy_flight', 'label': 'Flight'},
                    {'value': 'navy_vessel', 'label': 'Individual Vessel'}
                ]
            },
            'navy_aviation': {
                'name': 'Naval Aviation',
                'recruitment_level': 'aviation_squadron',
                'subunit_level': 'aviation_division',
                'structure': [
                    {'value': 'aviation_air_wing', 'label': 'Air Wing'},
                    {'value': 'aviation_air_group', 'label': 'Air Group'},
                    {'value': 'aviation_squadron', 'label': 'Squadron'},
                    {'value': 'aviation_division', 'label': 'Division'},
                    {'value': 'aviation_flight', 'label': 'Flight'},
                    {'value': 'aviation_element', 'label': 'Element/Section'}
                ]
            },
            'army': {
                'name': 'Army',
                'recruitment_level': 'ground_company',
                'subunit_level': 'ground_platoon',
                'structure': [
                    {'value': 'ground_corps', 'label': 'Corps'},
                    {'value': 'ground_division', 'label': 'Division'},
                    {'value': 'ground_brigade', 'label': 'Brigade/Regiment'},
                    {'value': 'ground_battalion', 'label': 'Battalion'},
                    {'value': 'ground_company', 'label': 'Company'},
                    {'value': 'ground_platoon', 'label': 'Platoon'},
                    {'value': 'ground_squad', 'label': 'Squad'},
                    {'value': 'ground_fire_team', 'label': 'Fire Team'}
                ]
            },
            'marines': {
                'name': 'Marines',
                'recruitment_level': 'ground_company',
                'subunit_level': 'ground_platoon',
                'structure': [
                    {'value': 'ground_corps', 'label': 'Corps'},
                    {'value': 'ground_division', 'label': 'Division'},
                    {'value': 'ground_brigade', 'label': 'Brigade/Regiment'},
                    {'value': 'ground_battalion', 'label': 'Battalion'},
                    {'value': 'ground_company', 'label': 'Company'},
                    {'value': 'ground_platoon', 'label': 'Platoon'},
                    {'value': 'ground_squad', 'label': 'Squad'},
                    {'value': 'ground_fire_team', 'label': 'Fire Team'}
                ]
            }
        })