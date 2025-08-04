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
import logging

logger = logging.getLogger(__name__)


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
        print("\n=== BRIGADES ENDPOINT DEBUG ===")

        # First, let's see what unit levels exist in the database
        all_unit_levels = Unit.objects.filter(is_active=True).values_list('unit_level', flat=True).distinct()
        print(f"All active unit levels in database: {list(all_unit_levels)}")

        # Count units by level
        for level in all_unit_levels:
            count = Unit.objects.filter(unit_level=level, is_active=True).count()
            print(f"  - {level}: {count} units")

        # Get Squadron level units for Navy/Aviation and Company level for Ground Forces
        units_query = Unit.objects.filter(
            Q(unit_level='navy_squadron') |
            Q(unit_level='aviation_squadron') |
            Q(unit_level='ground_company'),
            is_active=True
        )

        print(f"\nFiltering for: navy_squadron, aviation_squadron, ground_company")
        print(f"Found {units_query.count()} units matching criteria")

        # If no units found with exact match, try partial match
        if units_query.count() == 0:
            print("\nNo exact matches found. Trying partial matches...")

            # Try finding units that might be squadrons or companies
            squadron_units = Unit.objects.filter(
                Q(unit_level__icontains='squadron') | Q(name__icontains='squadron'),
                is_active=True
            )
            company_units = Unit.objects.filter(
                Q(unit_level__icontains='company') | Q(name__icontains='company'),
                is_active=True
            )

            print(f"Units with 'squadron' in level or name: {squadron_units.count()}")
            for unit in squadron_units[:5]:  # Show first 5
                print(
                    f"  - {unit.name} (level: {unit.unit_level}, branch: {unit.branch.name if unit.branch else 'None'})")

            print(f"\nUnits with 'company' in level or name: {company_units.count()}")
            for unit in company_units[:5]:  # Show first 5
                print(
                    f"  - {unit.name} (level: {unit.unit_level}, branch: {unit.branch.name if unit.branch else 'None'})")

            # Use the broader query for now
            units_query = squadron_units | company_units
            print(f"\nUsing broader query, found {units_query.count()} units")

        units = units_query.prefetch_related('authorized_mos', 'mos_training_capability').select_related('branch')

        data = []
        for unit in units:
            print(f"\nProcessing unit: {unit.name}")
            print(f"  - Unit level: {unit.unit_level}")
            print(f"  - Branch: {unit.branch.name if unit.branch else 'None'}")
            print(f"  - Is active: {unit.is_active}")
            print(f"  - Recruitment status: {unit.recruitment_status}")

            # Get all units under this unit (including the unit itself)
            descendant_units = self._get_all_descendant_unit_ids(unit)
            print(f"  - Descendant units: {len(descendant_units)}")

            # Calculate total available slots for all units under this unit
            slots_query = RecruitmentSlot.objects.filter(
                unit__id__in=descendant_units,
                is_active=True
            )
            print(f"  - Active recruitment slots: {slots_query.count()}")

            available_slots = slots_query.aggregate(
                total=Sum(F('total_slots') - F('filled_slots') - F('reserved_slots'))
            )['total'] or 0
            print(f"  - Available slots: {available_slots}")

            authorized_mos = unit.authorized_mos.filter(is_active=True)
            training_mos = unit.mos_training_capability.filter(is_active=True)
            print(f"  - Authorized MOS: {authorized_mos.count()}")
            print(f"  - Training MOS: {training_mos.count()}")

            # Determine branch type based on unit_level prefix
            branch_type = 'unknown'
            if unit.unit_level and unit.unit_level.startswith('navy_'):
                branch_type = 'navy'
            elif unit.unit_level and unit.unit_level.startswith('aviation_'):
                branch_type = 'navy_aviation'
            elif unit.unit_level and unit.unit_level.startswith('ground_'):
                # Further differentiate between Army and Marines based on branch name
                if unit.branch and 'marine' in unit.branch.name.lower():
                    branch_type = 'marines'
                else:
                    branch_type = 'army'
            else:
                # Fallback: try to determine from branch name
                if unit.branch:
                    branch_name = unit.branch.name.lower()
                    if 'navy' in branch_name and 'aviation' in branch_name:
                        branch_type = 'navy_aviation'
                    elif 'navy' in branch_name:
                        branch_type = 'navy'
                    elif 'marine' in branch_name:
                        branch_type = 'marines'
                    elif 'army' in branch_name:
                        branch_type = 'army'

            print(f"  - Determined branch type: {branch_type}")

            data.append({
                'id': str(unit.id),
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'motto': unit.motto,
                'description': unit.description,
                'unit_type': unit.unit_level or 'unknown',
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

        print(f"\n=== TOTAL UNITS RETURNED: {len(data)} ===\n")
        return Response(data)

    @action(detail=True, methods=['get'])
    def platoons(self, request, pk):
        """
        Get subunits for a specific unit (Divisions for Navy, Platoons for Army/Marines)
        Keeping the method name for backwards compatibility
        """
        print(f"\n=== PLATOONS ENDPOINT DEBUG ===")
        print(f"Looking for unit with ID: {pk}")

        unit = get_object_or_404(Unit, pk=pk)
        print(f"Found unit: {unit.name}")
        print(f"  - Unit level: {unit.unit_level}")
        print(f"  - Branch: {unit.branch.name if unit.branch else 'None'}")

        # Determine what type of subunits to look for based on parent unit type
        subunit_type = None
        if unit.unit_level == 'navy_squadron':
            subunit_type = 'navy_division'
        elif unit.unit_level == 'aviation_squadron':
            subunit_type = 'aviation_division'
        elif unit.unit_level == 'ground_company':
            subunit_type = 'ground_platoon'
        elif 'squadron' in str(unit.unit_level).lower():
            # Fallback for non-standard squadron types
            subunit_type = 'division'
            print(f"  - Using fallback: looking for 'division' subunits")
        elif 'company' in str(unit.unit_level).lower():
            # Fallback for non-standard company types
            subunit_type = 'platoon'
            print(f"  - Using fallback: looking for 'platoon' subunits")

        print(f"Looking for subunit type: {subunit_type}")

        if subunit_type:
            # Get specific type of subunits
            subunits = Unit.objects.filter(
                parent_unit=unit,
                unit_level=subunit_type,
                is_active=True
            ).select_related('parent_unit').prefetch_related('recruitment_slots')

            print(f"Found {subunits.count()} subunits with exact level match")

            # If no exact matches, try partial match
            if subunits.count() == 0 and subunit_type in ['division', 'platoon']:
                print(f"No exact matches. Trying partial match for '{subunit_type}'...")
                subunits = Unit.objects.filter(
                    parent_unit=unit,
                    unit_level__icontains=subunit_type,
                    is_active=True
                ).select_related('parent_unit').prefetch_related('recruitment_slots')
                print(f"Found {subunits.count()} subunits with partial match")
        else:
            # Fallback - get any direct children
            print("No specific subunit type determined. Getting all direct children...")
            subunits = Unit.objects.filter(
                parent_unit=unit,
                is_active=True
            ).select_related('parent_unit').prefetch_related('recruitment_slots')
            print(f"Found {subunits.count()} direct child units")

        data = []
        for subunit in subunits:
            print(f"\nProcessing subunit: {subunit.name}")
            print(f"  - Unit level: {subunit.unit_level}")

            # Get slot information
            slots = subunit.recruitment_slots.filter(is_active=True)
            total_available = sum(slot.available_slots for slot in slots)
            print(f"  - Available slots: {total_available}")

            # Get current strength
            current_strength = UserPosition.objects.filter(
                position__unit=subunit,
                status='active'
            ).count()
            print(f"  - Current strength: {current_strength}")

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
            print(f"  - Leader: {leader_name}")

            # Determine the parent hierarchy names based on unit type
            company = None
            battalion = None

            if subunit.unit_level == 'ground_platoon' or 'platoon' in str(subunit.unit_level).lower():
                # For Army/Marines platoons
                company = subunit.parent_unit.name if subunit.parent_unit else None
                battalion = subunit.parent_unit.parent_unit.name if subunit.parent_unit and subunit.parent_unit.parent_unit else None
            elif subunit.unit_level in ['navy_division', 'aviation_division'] or 'division' in str(
                    subunit.unit_level).lower():
                # For Navy/Aviation divisions
                company = subunit.parent_unit.name if subunit.parent_unit else None  # Squadron
                # Find the task force or air group (parent of squadron)
                if subunit.parent_unit and subunit.parent_unit.parent_unit:
                    battalion = subunit.parent_unit.parent_unit.name

            data.append({
                'id': str(subunit.id),
                'designation': subunit.unit_designation or subunit.name,
                'unit_type': subunit.unit_level or 'unknown',
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

        print(f"\n=== TOTAL SUBUNITS RETURNED: {len(data)} ===\n")
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