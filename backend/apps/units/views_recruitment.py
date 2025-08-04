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
    def recruitment_units(self, request):
        """
        Get recruitment units based on branch type
        Returns Squadrons for Navy/Navy Aviation, Companies for Army/Marines
        """
        branch_type = request.query_params.get('branch_type', 'all')

        if branch_type in ['navy', 'navy_aviation']:
            # Get Squadrons for Navy branches
            units = Unit.objects.filter(
                unit_level='squadron',
                is_active=True,
                branch__name__icontains='Navy' if branch_type == 'navy' else 'Aviation'
            ).prefetch_related('authorized_mos', 'mos_training_capability')

        elif branch_type in ['army', 'marines']:
            # Get Companies for Army/Marines
            units = Unit.objects.filter(
                unit_level='company',
                is_active=True,
                branch__name__icontains=branch_type.title()
            ).prefetch_related('authorized_mos', 'mos_training_capability')

        else:
            # Get all recruitment level units
            units = Unit.objects.filter(
                Q(unit_level='squadron') | Q(unit_level='company'),
                is_active=True
            ).prefetch_related('authorized_mos', 'mos_training_capability')

        data = []
        for unit in units:
            # Get all sub-units recursively
            descendant_units = self._get_all_descendant_units(unit)

            # Calculate total available slots
            available_slots = RecruitmentSlot.objects.filter(
                unit__id__in=[u.id for u in descendant_units],
                is_active=True
            ).aggregate(
                total=Sum(F('total_slots') - F('filled_slots') - F('reserved_slots'))
            )['total'] or 0

            authorized_mos = unit.authorized_mos.filter(is_active=True)
            training_mos = unit.mos_training_capability.filter(is_active=True)

            # Get parent unit info (Battalion for Company, Taskforce/Division for Squadron)
            parent_info = None
            if unit.parent_unit:
                parent_info = {
                    'id': str(unit.parent_unit.id),
                    'name': unit.parent_unit.name,
                    'type': unit.parent_unit.unit_level
                }

            data.append({
                'id': str(unit.id),
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'motto': unit.motto,
                'description': unit.description,
                'unit_type': unit.unit_level,
                'branch': unit.branch.name if unit.branch else None,
                'recruitment_status': unit.recruitment_status,
                'available_slots': available_slots,
                'is_aviation_only': unit.is_aviation_only,
                'emblem_url': unit.emblem_url,
                'recruitment_notes': unit.recruitment_notes,
                'parent_unit': parent_info,
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
    def subunits(self, request, pk):
        """
        Get subunits for a specific unit
        Returns Divisions for Navy Squadrons, Platoons for Army/Marine Companies
        """
        unit = get_object_or_404(Unit, pk=pk)

        # Determine what type of subunits to look for
        if unit.unit_level == 'squadron':
            # Navy Squadron -> get Divisions
            subunit_type = 'division'
        elif unit.unit_level == 'company':
            # Army/Marine Company -> get Platoons
            subunit_type = 'platoon'
        else:
            return Response({
                'error': f'Unit type {unit.unit_level} does not have standard subunits for recruitment'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get direct subunits
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

            data.append({
                'id': str(subunit.id),
                'name': subunit.name,
                'designation': subunit.unit_designation,
                'unit_type': subunit.unit_level,
                'parent_unit': unit.name,
                'current_strength': current_strength,
                'max_strength': subunit.max_personnel,
                'available_slots': total_available,
                'leader': leader_name,
                'recruitment_status': subunit.recruitment_status,
                'is_accepting_applications': subunit.is_accepting_applications(),
                'career_tracks_available': list(slots.values_list('career_track', flat=True).distinct()),
                'emblem_url': subunit.emblem_url,
                'motto': subunit.motto
            })

        return Response({
            'parent_unit': {
                'id': str(unit.id),
                'name': unit.name,
                'type': unit.unit_level,
                'branch': unit.branch.name if unit.branch else None
            },
            'subunits': data,
            'total_subunits': len(data)
        })

    def _get_all_descendant_units(self, unit):
        """
        Recursively get all descendant units
        """
        descendants = [unit]
        children = Unit.objects.filter(parent_unit=unit, is_active=True)

        for child in children:
            descendants.extend(self._get_all_descendant_units(child))

        return descendants

    @action(detail=False, methods=['get'])
    def branch_structure(self, request):
        """
        Get the structure information for each branch
        """
        return Response({
            'navy': {
                'name': 'Navy',
                'recruitment_level': 'Squadron',
                'subunit_level': 'Division',
                'structure': [
                    'Expeditionary Force',
                    'Fleet',
                    'Battlegroup',
                    'Taskforce',
                    'Squadron',
                    'Division',
                    'Flight',
                    'Individual Vessel'
                ]
            },
            'navy_aviation': {
                'name': 'Navy Aviation',
                'recruitment_level': 'Squadron',
                'subunit_level': 'Division',
                'structure': [
                    'Air Wing',
                    'Air Group',
                    'Squadron',
                    'Division',
                    'Flight',
                    'Element/Section'
                ]
            },
            'army': {
                'name': 'Army',
                'recruitment_level': 'Company',
                'subunit_level': 'Platoon',
                'structure': [
                    'Corps',
                    'Division',
                    'Brigade',
                    'Battalion',
                    'Company',
                    'Platoon',
                    'Squad',
                    'Fireteam'
                ]
            },
            'marines': {
                'name': 'Marines',
                'recruitment_level': 'Company',
                'subunit_level': 'Platoon',
                'structure': [
                    'Corps',
                    'Division',
                    'Brigade',
                    'Battalion',
                    'Company',
                    'Platoon',
                    'Squad',
                    'Fireteam'
                ]
            }
        })