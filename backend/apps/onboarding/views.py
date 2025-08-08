# backend/apps/onboarding/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction, models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import requests
import os

from .models import (
    Application, ApplicationWaiverType, ApplicationWaiver,
    ApplicationProgress, ApplicationComment, ApplicationInterview,
    UserOnboardingProgress, MentorAssignment, ApplicationStatus
)
from .serializers import (
    ApplicationListSerializer, ApplicationDetailSerializer,
    ApplicationCreateSerializer, ApplicationSubmitSerializer,
    ApplicationStatusSerializer, ApplicationWaiverTypeSerializer,
    ApplicationWaiverSerializer, ApplicationProgressSerializer,
    ApplicationCommentSerializer, ApplicationInterviewSerializer,
    ApplicationRecruitmentDataSerializer, UserOnboardingProgressSerializer,
    MentorAssignmentSerializer
)
from apps.units.models import Unit, MOS, Branch, RecruitmentSlot, Role
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model

from ..units.models import RecruitmentSlot

User = get_user_model()


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the new application flow
    """


    queryset = Application.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'branch', 'career_track', 'primary_unit', 'secondary_unit']
    search_fields = ['application_number', 'discord_username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'submitted_at', 'status']
    ordering = ['-created_at']

    def _get_all_subordinate_units(self, unit):
        """
        Recursively get all subordinate units including the unit itself.
        Returns a list of unit IDs.

        This is used to aggregate recruitment slots from an entire unit hierarchy,
        so when a user selects a Squadron, they see positions from the Squadron,
        its Divisions, Flights, etc.

        Args:
            unit: The parent Unit object

        Returns:
            list: List of UUID strings representing all unit IDs in the hierarchy
        """
        unit_ids = [unit.id]

        # Get all direct children
        children = Unit.objects.filter(
            parent_unit=unit,
            is_active=True
        ).values_list('id', flat=True)

        unit_ids.extend(children)

        # Recursively get all descendants
        current_level = list(children)
        max_depth = 10  # Prevent infinite loops
        depth = 0

        while current_level and depth < max_depth:
            next_level = Unit.objects.filter(
                parent_unit_id__in=current_level,
                is_active=True
            ).values_list('id', flat=True)

            if next_level:
                unit_ids.extend(next_level)
                current_level = list(next_level)
            else:
                break

            depth += 1

        return unit_ids

    def get_permissions(self):
        """
        - Anyone can create an application
        - Authenticated users can view/update their own
        - Admins can view/update all
        """
        if self.action in ['create', 'recruitment_data']:
            return [permissions.AllowAny()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'submit', 'check_status',
                             'current', 'get_units', 'get_mos_options', 'save_progress',
                             'accept_waiver']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        elif self.action in ['create', 'update', 'partial_update', 'save_progress']:
            return ApplicationCreateSerializer
        elif self.action == 'submit':
            return ApplicationSubmitSerializer
        elif self.action == 'check_status':
            return ApplicationStatusSerializer
        return ApplicationDetailSerializer

    def get_queryset(self):
        """Filter applications based on user permissions"""
        queryset = super().get_queryset()

        if not self.request.user.is_authenticated:
            return queryset.none()

        if not self.request.user.is_admin:
            # Non-admins can only see their own applications
            queryset = queryset.filter(user=self.request.user)

        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def recruitment_data(self, request):
        """
        Get initial recruitment data for the application form
        Step 6: Initial Breakdown
        """
        serializer = ApplicationRecruitmentDataSerializer({})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_recruitment_slots(self, request):
        """
        Get available recruitment slots based on unit and track
        Step 7: Position Selection - Shows open recruitment slots
        Now directly returns RecruitmentSlot objects
        """
        branch_id = request.query_params.get('branch_id')
        career_track = request.query_params.get('career_track')
        unit_id = request.query_params.get('unit_id')

        if not unit_id:
            return Response(
                {'error': 'unit_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the selected unit
        try:
            unit = Unit.objects.get(id=unit_id, is_active=True)
        except Unit.DoesNotExist:
            return Response(
                {'error': 'Unit not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all subordinate units including the selected unit
        all_unit_ids = self._get_all_subordinate_units(unit)

        print(f"Getting recruitment slots for unit {unit.name} and {len(all_unit_ids) - 1} subordinate units")

        # Get open recruitment slots for all units in hierarchy and career track
        slots = RecruitmentSlot.objects.filter(
            unit_id__in=all_unit_ids,
            career_track=career_track,
            is_active=True
        ).select_related('role', 'unit').filter(
            # Only show slots with available positions
            models.Q(total_slots__gt=models.F('filled_slots') + models.F('reserved_slots'))
        )

        data = []

        for slot in slots:
            # Build the slot data
            slot_data = {
                'id': slot.id,
                'unit': {
                    'id': str(slot.unit.id),
                    'name': slot.unit.name,
                    'abbreviation': slot.unit.abbreviation,
                    'level': slot.unit.unit_level,
                    'type': slot.unit.unit_type
                },
                'role': {
                    'id': str(slot.role.id),
                    'name': slot.role.name,
                    'abbreviation': slot.role.abbreviation or slot.role.name[:4],
                    'category': slot.role.category,
                    'description': slot.role.description or '',
                    'is_command_role': slot.role.is_command_role,
                    'is_staff_role': slot.role.is_staff_role,
                    'is_nco_role': slot.role.is_nco_role,
                    'is_specialist_role': slot.role.is_specialist_role,
                    'responsibilities': slot.role.responsibilities,
                    'min_rank': slot.role.min_rank.abbreviation if slot.role.min_rank else None,
                    'typical_rank': slot.role.typical_rank.abbreviation if slot.role.typical_rank else None,
                },
                'career_track': slot.career_track,
                'available_slots': slot.available_slots,
                'total_slots': slot.total_slots,
                'filled_slots': slot.filled_slots,
                'reserved_slots': slot.reserved_slots,
                'notes': slot.notes,

                # Display info
                'display_name': f"{slot.role.name} - {slot.unit.abbreviation}",
                'display_code': f"{slot.role.abbreviation or 'POS'}-{slot.unit.abbreviation}",
            }

            data.append(slot_data)

        # Sort by available slots (most available first) and then by role name
        data.sort(key=lambda x: (-x['available_slots'], x['role']['name']))

        # Add summary information
        response_data = {
            'recruitment_slots': data,
            'summary': {
                'total_positions': len(data),
                'total_available_slots': sum(s['available_slots'] for s in data),
                'units_included': len(all_unit_ids),
                'primary_unit': {
                    'id': str(unit.id),
                    'name': unit.name,
                    'abbreviation': unit.abbreviation
                },
                'breakdown_by_category': {}
            }
        }

        # Calculate breakdown by role category
        category_breakdown = {}
        for slot_data in data:
            category = slot_data['role']['category']
            if category not in category_breakdown:
                category_breakdown[category] = {
                    'count': 0,
                    'available_slots': 0
                }
            category_breakdown[category]['count'] += 1
            category_breakdown[category]['available_slots'] += slot_data['available_slots']

        response_data['summary']['breakdown_by_category'] = category_breakdown

        return Response(response_data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def current(self, request):
        """
        Get or create the current user's draft application
        """
        # Check for existing draft application
        application = Application.objects.filter(
            user=request.user,
            status=ApplicationStatus.DRAFT
        ).first()

        if not application:
            # Create new draft application
            application = Application.objects.create(
                user=request.user,
                discord_id=request.user.discord_id,
                discord_username=request.user.username,
                email=request.user.email or '',
                status=ApplicationStatus.DRAFT
            )
            # Create progress tracker
            ApplicationProgress.objects.create(application=application)

        serializer = ApplicationDetailSerializer(application, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def save_progress(self, request, pk=None):
        """
        Save progress on the application (auto-save functionality)
        """
        application = self.get_object()

        # Ensure user owns this application
        if application.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You do not have permission to edit this application'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Only allow editing draft applications
        if application.status != ApplicationStatus.DRAFT:
            return Response(
                {'error': 'Cannot edit submitted applications'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApplicationCreateSerializer(
            application,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            # Return full application with progress
            detail_serializer = ApplicationDetailSerializer(
                application,
                context={'request': request}
            )
            return Response(detail_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # backend/apps/onboarding/views.py
    # Replace the existing get_units action with this updated version

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_units(self, request):
        """
        Get available units based on branch selection
        Steps 9-10: Unit selection
        Now includes positions from all subordinate units
        """
        branch_id = request.query_params.get('branch_id')
        unit_type = request.query_params.get('unit_type')  # 'primary' or 'secondary'
        parent_unit_id = request.query_params.get('parent_unit_id')

        if not branch_id:
            return Response(
                {'error': 'branch_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get base query with prefetch
        units = Unit.objects.filter(
            branch_id=branch_id,
            is_active=True
        ).prefetch_related(
            models.Prefetch(
                'recruitment_slots',
                queryset=RecruitmentSlot.objects.filter(is_active=True),
                to_attr='active_recruitment_slots'
            )
        )

        # Filter by unit type - be flexible with field names
        if unit_type == 'primary':
            # Get Squadron/Company level units
            units = units.filter(
                models.Q(unit_type__in=['navy_squadron', 'ground_company', 'aviation_squadron']) |
                models.Q(unit_level__in=['squadron', 'company'])
            )
            print(f"Filtering for primary units (squadrons/companies), found {units.count()} units")
        elif unit_type == 'secondary' and parent_unit_id:
            # Get Division/Platoon level units under the selected primary unit
            units = units.filter(
                parent_unit_id=parent_unit_id
            ).filter(
                models.Q(unit_type__in=['navy_division', 'ground_platoon', 'aviation_division']) |
                models.Q(unit_level__in=['division', 'platoon'])
            )
            print(f"Filtering for secondary units under {parent_unit_id}, found {units.count()} units")

        data = []
        for unit in units:
            # Get all subordinate units recursively
            all_unit_ids = self._get_all_subordinate_units(unit)

            # Calculate total available slots from this unit and all subordinates
            total_available = RecruitmentSlot.objects.filter(
                unit_id__in=all_unit_ids,
                is_active=True
            ).aggregate(
                total=models.Sum(models.F('total_slots') - models.F('filled_slots') - models.F('reserved_slots'))
            )['total'] or 0

            # Get breakdown by career track
            slots_by_track = RecruitmentSlot.objects.filter(
                unit_id__in=all_unit_ids,
                is_active=True
            ).values('career_track').annotate(
                available=models.Sum(models.F('total_slots') - models.F('filled_slots') - models.F('reserved_slots'))
            )

            track_breakdown = {
                'enlisted': 0,
                'warrant': 0,
                'officer': 0
            }
            for slot_data in slots_by_track:
                if slot_data['career_track'] in track_breakdown:
                    track_breakdown[slot_data['career_track']] = slot_data['available'] or 0

            # Get all unique roles available in this unit hierarchy
            available_roles = Role.objects.filter(
                recruitment_slots__unit_id__in=all_unit_ids,
                recruitment_slots__is_active=True
            ).distinct().values('id', 'name', 'category')

            # Get number of subordinate units
            subordinate_count = len(all_unit_ids) - 1  # Exclude the unit itself

            # Only include units with available slots or open recruitment status
            if total_available > 0 or unit.recruitment_status in ['open', 'limited', None]:
                data.append({
                    'id': unit.id,
                    'name': unit.name,
                    'abbreviation': unit.abbreviation,
                    'unit_type': getattr(unit, 'unit_type', None) or getattr(unit, 'unit_level', None),
                    'motto': unit.motto,
                    'description': unit.description,
                    'emblem_url': unit.emblem_url,
                    'available_slots': total_available,
                    'slots_by_track': track_breakdown,
                    'recruitment_status': unit.recruitment_status or 'open',
                    'recruitment_notes': getattr(unit, 'recruitment_notes', None),
                    'is_aviation_only': getattr(unit, 'is_aviation_only', False),
                    'subordinate_units_count': subordinate_count,
                    'total_units_included': len(all_unit_ids),
                    'available_roles_count': len(available_roles),
                    'available_roles': list(available_roles)[:10]  # Show first 10 roles
                })

        return Response(data)

    def _get_all_subordinate_units(self, unit):
        """
        Get all subordinate units recursively, including the unit itself
        Returns a list of unit IDs
        """
        unit_ids = [unit.id]

        # Get all children
        children = Unit.objects.filter(
            parent_unit=unit,
            is_active=True
        ).values_list('id', flat=True)

        unit_ids.extend(children)

        # Recursively get all descendants
        current_level = list(children)
        while current_level:
            next_level = Unit.objects.filter(
                parent_unit_id__in=current_level,
                is_active=True
            ).values_list('id', flat=True)

            unit_ids.extend(next_level)
            current_level = list(next_level)

        return unit_ids

    # backend/apps/onboarding/views.py
    # Replace the existing get_mos_options action with this updated version

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_mos_options(self, request):
        """
        Get available recruitment slots based on unit and track
        Step 12: MOS Selection - Shows open positions based on roles
        Now aggregates positions from selected unit and all subordinate units
        """
        branch_id = request.query_params.get('branch_id')
        career_track = request.query_params.get('career_track')
        unit_id = request.query_params.get('unit_id')

        if not unit_id:
            return Response(
                {'error': 'unit_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the selected unit
        try:
            unit = Unit.objects.get(id=unit_id, is_active=True)
        except Unit.DoesNotExist:
            return Response(
                {'error': 'Unit not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all subordinate units including the selected unit
        all_unit_ids = self._get_all_subordinate_units(unit)

        print(f"Getting MOS options for unit {unit.name} and {len(all_unit_ids) - 1} subordinate units")

        # Get open recruitment slots for all units in hierarchy and career track
        slots_query = RecruitmentSlot.objects.filter(
            unit_id__in=all_unit_ids,
            career_track=career_track,
            is_active=True
        ).select_related('role', 'unit')

        # Create a dictionary to track MOS slots
        mos_slots = {}
        unit_breakdown = {}  # Track which units have which positions

        # Process each recruitment slot
        for slot in slots_query:
            # Only process if slot has available positions
            if slot.available_slots > 0 and slot.role:
                # Try to get MOS from role - adjust this based on your Role model
                role_mos = None

                # Option 1: Direct MOS field
                if hasattr(slot.role, 'mos') and slot.role.mos:
                    role_mos = slot.role.mos
                # Option 2: Required MOS field
                elif hasattr(slot.role, 'required_mos') and slot.role.required_mos:
                    role_mos = slot.role.required_mos
                # Option 3: Use role itself as a pseudo-MOS (if MOS model isn't fully integrated)
                else:
                    # Create a pseudo-MOS entry based on the role
                    role_mos = type('obj', (object,), {
                        'id': f'role_{slot.role.id}',
                        'code': slot.role.abbreviation or f'R{slot.role.id[:8]}',
                        'title': slot.role.name,
                        'category': slot.role.category,
                        'description': slot.role.description or '',
                        'ait_weeks': 0,
                        'physical_demand_rating': ''
                    })()

                if role_mos:
                    mos_id = str(role_mos.id)

                    # Initialize MOS entry if not exists
                    if mos_id not in mos_slots:
                        mos_slots[mos_id] = {
                            'id': role_mos.id,
                            'code': getattr(role_mos, 'code', ''),
                            'title': getattr(role_mos, 'title', slot.role.name),
                            'category': getattr(role_mos, 'category', slot.role.category),
                            'description': getattr(role_mos, 'description', slot.role.description or ''),
                            'ait_weeks': getattr(role_mos, 'ait_weeks', 0),
                            'physical_demand_rating': getattr(role_mos, 'physical_demand_rating', ''),
                            'available_slots': 0,
                            'roles': [],
                            'units': [],
                            'is_command_role': slot.role.is_command_role,
                            'is_staff_role': slot.role.is_staff_role,
                            'is_nco_role': slot.role.is_nco_role,
                            'is_specialist_role': slot.role.is_specialist_role
                        }

                    # Add to available slots count
                    mos_slots[mos_id]['available_slots'] += slot.available_slots

                    # Add role info with unit context
                    role_info = f"{slot.role.name} in {slot.unit.abbreviation} ({slot.available_slots} slots)"
                    if role_info not in mos_slots[mos_id]['roles']:
                        mos_slots[mos_id]['roles'].append(role_info)

                    # Track which units have this position
                    unit_info = {
                        'id': str(slot.unit.id),
                        'name': slot.unit.name,
                        'abbreviation': slot.unit.abbreviation,
                        'level': slot.unit.unit_level,
                        'available_slots': slot.available_slots
                    }

                    # Check if this unit is already in the list
                    unit_already_added = any(u['id'] == unit_info['id'] for u in mos_slots[mos_id]['units'])
                    if not unit_already_added:
                        mos_slots[mos_id]['units'].append(unit_info)

                    # Track unit breakdown
                    if slot.unit.abbreviation not in unit_breakdown:
                        unit_breakdown[slot.unit.abbreviation] = 0
                    unit_breakdown[slot.unit.abbreviation] += slot.available_slots

        # Convert to list and sort by available slots (most available first)
        data = list(mos_slots.values())
        data.sort(key=lambda x: x['available_slots'], reverse=True)

        # If no MOS found with slots but we have a branch, show all entry-level MOS as fallback
        if not data and branch_id:
            try:
                # Try to get MOS from the database
                from apps.units.models import MOS

                all_mos = MOS.objects.filter(
                    branch_id=branch_id,
                    is_active=True,
                    is_entry_level=True
                )

                # For warrant track, filter to aviation MOS
                if career_track == 'warrant':
                    all_mos = all_mos.filter(category='aviation')

                if all_mos.exists():
                    data = [{
                        'id': mos.id,
                        'code': mos.code,
                        'title': mos.title,
                        'category': getattr(mos, 'category', ''),
                        'description': getattr(mos, 'description', ''),
                        'ait_weeks': getattr(mos, 'ait_weeks', 0),
                        'physical_demand_rating': getattr(mos, 'physical_demand_rating', ''),
                        'available_slots': 1,  # Show as available but limited
                        'roles': ['Position availability varies by unit'],
                        'units': [{'name': unit.name, 'abbreviation': unit.abbreviation}]
                    } for mos in all_mos]
                else:
                    # If no MOS in database, use roles as fallback
                    roles = Role.objects.filter(
                        allowed_branches=branch_id,
                        is_active=True
                    )

                    # Filter by career track
                    if career_track == 'enlisted':
                        roles = roles.filter(
                            models.Q(is_nco_role=True) |
                            models.Q(is_specialist_role=True) |
                            models.Q(typical_rank__is_enlisted=True)
                        )
                    elif career_track == 'warrant':
                        roles = roles.filter(
                            models.Q(category='aviation') |
                            models.Q(typical_rank__is_warrant=True)
                        )
                    elif career_track == 'officer':
                        roles = roles.filter(
                            models.Q(is_command_role=True) |
                            models.Q(is_staff_role=True) |
                            models.Q(typical_rank__is_officer=True)
                        )

                    data = [{
                        'id': f'role_{role.id}',
                        'code': role.abbreviation or f'R{str(role.id)[:8]}',
                        'title': role.name,
                        'category': role.category,
                        'description': role.description or '',
                        'available_slots': 1,
                        'roles': [role.name],
                        'units': [{'name': unit.name, 'abbreviation': unit.abbreviation}],
                        'is_command_role': role.is_command_role,
                        'is_staff_role': role.is_staff_role,
                        'is_nco_role': role.is_nco_role,
                        'is_specialist_role': role.is_specialist_role
                    } for role in roles[:20]]  # Limit to 20 roles

                print(f"Using fallback for branch {branch_id}, found {len(data)} MOS/Role options")
            except Exception as e:
                print(f"Error in fallback: {e}")

        # Add summary information
        response_data = {
            'mos_options': data,
            'summary': {
                'total_options': len(data),
                'total_available_slots': sum(m['available_slots'] for m in data),
                'units_included': len(all_unit_ids),
                'primary_unit': {
                    'id': str(unit.id),
                    'name': unit.name,
                    'abbreviation': unit.abbreviation
                },
                'unit_breakdown': unit_breakdown
            }
        }

        return Response(response_data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept_waiver(self, request, pk=None):
        """
        Accept a specific waiver/acknowledgment
        Step 15: Waivers
        """
        application = self.get_object()
        waiver_type_id = request.data.get('waiver_type_id')

        if not waiver_type_id:
            return Response(
                {'error': 'waiver_type_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        waiver_type = get_object_or_404(ApplicationWaiverType, id=waiver_type_id)

        # Get client info for tracking
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        waiver, created = ApplicationWaiver.objects.update_or_create(
            application=application,
            waiver_type=waiver_type,
            defaults={
                'accepted': True,
                'accepted_at': timezone.now(),
                'ip_address': ip_address,
                'user_agent': user_agent
            }
        )

        # Check if all required waivers are accepted
        required_waivers = ApplicationWaiverType.objects.filter(is_required=True)
        accepted_waivers = ApplicationWaiver.objects.filter(
            application=application,
            waiver_type__in=required_waivers,
            accepted=True
        ).count()

        if accepted_waivers == required_waivers.count():
            application.progress.waivers_completed = True
            application.progress.save()

        serializer = ApplicationWaiverSerializer(waiver)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        """
        Final submission of the application
        Step 10: Submit
        """
        application = self.get_object()

        # Ensure user owns this application
        if application.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You do not have permission to submit this application'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already submitted
        if application.status != ApplicationStatus.DRAFT:
            return Response(
                {'error': 'Application has already been submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate all required fields are filled
        errors = []

        if not all([application.first_name, application.last_name, application.email]):
            errors.append('Basic information is incomplete')

        if not application.branch:
            errors.append('Branch selection is required')

        if not application.primary_unit:
            errors.append('Primary unit selection is required')

        if not application.career_track:
            errors.append('Career track selection is required')

        # Check if a recruitment slot is selected
        if not application.selected_recruitment_slot:
            errors.append('Position selection is required')

        if not application.previous_experience or not application.reason_for_joining:
            errors.append('Experience and motivation are required')

        # Check all required waivers are accepted
        required_waivers = ApplicationWaiverType.objects.filter(is_required=True)
        accepted_waivers = ApplicationWaiver.objects.filter(
            application=application,
            waiver_type__in=required_waivers,
            accepted=True
        ).count()

        if accepted_waivers != required_waivers.count():
            errors.append('All waivers and acknowledgments must be accepted')

        if errors:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Submit the application
        with transaction.atomic():
            application.status = ApplicationStatus.SUBMITTED
            application.submitted_at = timezone.now()
            application.save()

            # Update progress
            application.progress.current_step = 11
            application.progress.save()

            # Reserve the slot
            if application.selected_recruitment_slot:
                slot = application.selected_recruitment_slot
                slot.reserved_slots = models.F('reserved_slots') + 1
                slot.save(update_fields=['reserved_slots'])

            # Send Discord notification
            self.send_discord_notification(application)

        # Return success with redirect info
        return Response({
            'success': True,
            'application_number': application.application_number,
            'message': 'Application submitted successfully',
            'redirect': f'/profile/{request.user.id}',
            'next_steps': [
                'Your application has been received and is under review',
                'You will be contacted via Discord for an interview',
                'Check your profile page for application status updates'
            ]
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def check_status(self, request):
        """
        Check status of user's applications
        """
        applications = Application.objects.filter(
            user=request.user
        ).exclude(status=ApplicationStatus.DRAFT).order_by('-submitted_at')

        serializer = ApplicationStatusSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def add_comment(self, request, pk=None):
        """
        Add a comment to an application (admin only)
        """
        application = self.get_object()

        serializer = ApplicationCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                application=application,
                author=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def schedule_interview(self, request, pk=None):
        """
        Schedule an interview for the application
        """
        application = self.get_object()

        serializer = ApplicationInterviewSerializer(data=request.data)
        if serializer.is_valid():
            interview = serializer.save(
                application=application,
                scheduled_by=request.user
            )

            # Update application status
            application.status = ApplicationStatus.INTERVIEW_SCHEDULED
            application.interview_scheduled_at = interview.scheduled_at
            application.save()

            # Send Discord notification about interview
            self.send_interview_notification(application, interview)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve an application
        """
        application = self.get_object()

        with transaction.atomic():
            application.status = ApplicationStatus.APPROVED
            application.decision_at = timezone.now()
            application.reviewer = request.user
            application.reviewer_notes = request.data.get('notes', '')
            application.save()

            # Update recruitment slot - convert reserved to filled
            if application.selected_recruitment_slot:
                slot = application.selected_recruitment_slot
                slot.filled_slots = models.F('filled_slots') + 1
                slot.reserved_slots = models.F('reserved_slots') - 1
                slot.save(update_fields=['filled_slots', 'reserved_slots'])

            # Create onboarding progress
            UserOnboardingProgress.objects.get_or_create(
                user=application.user,
                defaults={'application': application}
            )

            # Create position assignment if needed
            if application.selected_recruitment_slot and application.selected_recruitment_slot.role:
                # Check if there's a vacant position for this role in the unit
                from apps.units.models import Position, UserPosition

                position = Position.objects.filter(
                    role=application.selected_recruitment_slot.role,
                    unit=application.selected_recruitment_slot.unit,
                    is_vacant=True,
                    is_active=True
                ).first()

                if position:
                    # Create position assignment
                    UserPosition.objects.create(
                        user=application.user,
                        position=position,
                        assigned_by=request.user,
                        status='active',
                        assignment_type='primary',
                        notes=f"Assigned via application #{application.application_number}"
                    )

                    # Mark position as filled
                    position.is_vacant = False
                    position.save()

            # Send approval notification
            self.send_approval_notification(application)

        return Response({
            'success': True,
            'message': 'Application approved successfully'
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """
        Reject an application
        """
        application = self.get_object()

        with transaction.atomic():
            application.status = ApplicationStatus.REJECTED
            application.decision_at = timezone.now()
            application.reviewer = request.user
            application.reviewer_notes = request.data.get('notes', '')
            application.save()

            # Release the reserved slot
            if application.selected_recruitment_slot:
                slot = application.selected_recruitment_slot
                slot.reserved_slots = models.F('reserved_slots') - 1
                slot.save(update_fields=['reserved_slots'])

            # Send rejection notification
            self.send_rejection_notification(application)

        return Response({
            'success': True,
            'message': 'Application rejected'
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def withdraw(self, request, pk=None):
        """
        Allow applicant to withdraw their application
        """
        application = self.get_object()

        # Ensure user owns this application
        if application.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You do not have permission to withdraw this application'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Can only withdraw if not yet decided
        if application.status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]:
            return Response(
                {'error': 'Cannot withdraw an application that has already been decided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            application.status = ApplicationStatus.WITHDRAWN
            application.save()

            # Release the reserved slot if application was submitted
            if application.submitted_at and application.selected_recruitment_slot:
                slot = application.selected_recruitment_slot
                slot.reserved_slots = models.F('reserved_slots') - 1
                slot.save(update_fields=['reserved_slots'])

        return Response({
            'success': True,
            'message': 'Application withdrawn successfully'
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_drafts(self, request):
        """
        Get current user's draft applications
        """
        applications = Application.objects.filter(
            user=request.user,
            status=ApplicationStatus.DRAFT
        ).select_related(
            'branch', 'primary_unit', 'secondary_unit',
            'selected_recruitment_slot', 'progress'
        ).order_by('-created_at')

        serializer = ApplicationDetailSerializer(applications, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='status/(?P<discord_id>[^/.]+)',
            permission_classes=[permissions.AllowAny])
    def check_status_by_discord(self, request, discord_id=None):
        """
        Check application status by Discord ID
        Public endpoint for checking application status
        """
        if not discord_id:
            return Response(
                {'error': 'Discord ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the most recent non-draft application for this Discord ID
        application = Application.objects.filter(
            discord_id=discord_id
        ).exclude(
            status=ApplicationStatus.DRAFT
        ).order_by('-submitted_at').first()

        if not application:
            return Response({
                'status': 'not_found',
                'message': 'No submitted applications found for this Discord ID'
            })

        # Return basic status information
        return Response({
            'status': application.status,
            'application_id': application.id,
            'application_number': application.application_number,
            'submitted_at': application.submitted_at,
            'current_status': application.get_status_display(),
            'has_interview': application.interview_scheduled_at is not None,
            'interview_date': application.interview_scheduled_at
        })

    def send_discord_notification(self, application):
        """
        Send Discord webhook notification for new application
        """
        webhook_url = os.environ.get('DISCORD_APPLICATION_WEBHOOK')
        if not webhook_url:
            return

        try:
            # Get role information from recruitment slot
            role_info = "N/A"
            unit_info = "N/A"
            if application.selected_recruitment_slot:
                slot = application.selected_recruitment_slot
                role_info = f"{slot.role.name} ({slot.role.abbreviation})"
                unit_info = f"{slot.unit.name} ({slot.unit.abbreviation})"

            embed = {
                "title": f"New Application Received",
                "description": f"Application #{application.application_number}",
                "color": 3447003,  # Blue
                "fields": [
                    {
                        "name": "Applicant",
                        "value": f"{application.discord_username}",
                        "inline": True
                    },
                    {
                        "name": "Branch",
                        "value": application.branch.name if application.branch else "N/A",
                        "inline": True
                    },
                    {
                        "name": "Track",
                        "value": application.get_career_track_display(),
                        "inline": True
                    },
                    {
                        "name": "Primary Unit",
                        "value": application.primary_unit.name if application.primary_unit else "N/A",
                        "inline": True
                    },
                    {
                        "name": "Applied Position",
                        "value": role_info,
                        "inline": True
                    },
                    {
                        "name": "Position Unit",
                        "value": unit_info,
                        "inline": True
                    }
                ],
                "timestamp": timezone.now().isoformat()
            }

            # Send to applicant
            user_message = {
                "content": f"<@{application.discord_id}>",
                "embeds": [{
                    **embed,
                    "title": "Application Received",
                    "description": f"Thank you for applying! Your application #{application.application_number} has been received and is under review.",
                    "footer": {
                        "text": "You will be contacted soon regarding the next steps."
                    }
                }]
            }

            requests.post(webhook_url, json=user_message)

            # Send to admin channel
            admin_webhook = os.environ.get('DISCORD_ADMIN_WEBHOOK')
            if admin_webhook:
                admin_message = {
                    "embeds": [embed]
                }
                requests.post(admin_webhook, json=admin_message)

            # Mark notification as sent
            application.discord_notification_sent = True
            application.discord_notification_sent_at = timezone.now()
            application.save()

        except Exception as e:
            print(f"Failed to send Discord notification: {e}")


    def send_interview_notification(self, application, interview):
        """Send Discord notification for interview scheduling"""
        webhook_url = os.environ.get('DISCORD_APPLICATION_WEBHOOK')
        if not webhook_url:
            return

        try:
            message = {
                "content": f"<@{application.discord_id}>",
                "embeds": [{
                    "title": "Interview Scheduled",
                    "description": f"Your interview for application #{application.application_number} has been scheduled.",
                    "color": 15844367,  # Gold
                    "fields": [
                        {
                            "name": "Date & Time",
                            "value": interview.scheduled_at.strftime("%B %d, %Y at %H:%M UTC"),
                            "inline": False
                        },
                        {
                            "name": "Type",
                            "value": interview.get_interview_type_display(),
                            "inline": True
                        },
                        {
                            "name": "Interviewer",
                            "value": interview.interviewer.username if interview.interviewer else "TBD",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "Please be available on Discord at the scheduled time."
                    }
                }]
            }

            requests.post(webhook_url, json=message)

        except Exception as e:
            print(f"Failed to send interview notification: {e}")

    def send_approval_notification(self, application):
        """Send Discord notification for application approval"""
        webhook_url = os.environ.get('DISCORD_APPLICATION_WEBHOOK')
        if not webhook_url:
            return

        try:
            message = {
                "content": f"<@{application.discord_id}>",
                "embeds": [{
                    "title": "Application Approved!",
                    "description": f"Congratulations! Your application #{application.application_number} has been approved.",
                    "color": 5763719,  # Green
                    "fields": [
                        {
                            "name": "Next Steps",
                            "value": "1. Discord roles will be assigned shortly\n2. Complete orientation\n3. Begin basic training",
                            "inline": False
                        },
                        {
                            "name": "Assigned Unit",
                            "value": application.primary_unit.name if application.primary_unit else "TBD",
                            "inline": True
                        },
                        {
                            "name": "Career Track",
                            "value": application.get_career_track_display(),
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "Welcome to the unit!"
                    }
                }]
            }

            requests.post(webhook_url, json=message)

        except Exception as e:
            print(f"Failed to send approval notification: {e}")

    def send_rejection_notification(self, application):
        """Send Discord notification for application rejection"""
        webhook_url = os.environ.get('DISCORD_APPLICATION_WEBHOOK')
        if not webhook_url:
            return

        try:
            message = {
                "content": f"<@{application.discord_id}>",
                "embeds": [{
                    "title": "Application Status Update",
                    "description": f"Thank you for your interest. After careful review, we are unable to approve application #{application.application_number} at this time.",
                    "color": 15548997,  # Red
                    "fields": [
                        {
                            "name": "Next Steps",
                            "value": "You may reapply after 30 days. We encourage you to gain more experience and try again.",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": "Thank you for your interest in our unit."
                    }
                }]
            }

            requests.post(webhook_url, json=message)

        except Exception as e:
            print(f"Failed to send rejection notification: {e}")