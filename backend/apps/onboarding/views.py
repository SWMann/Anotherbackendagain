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

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_units(self, request):
        """
        Get available units based on branch selection
        Steps 9-10: Unit selection
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
            # Calculate total available slots using prefetched data
            total_available = sum(
                slot.available_slots for slot in unit.active_recruitment_slots
            )

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
                    'recruitment_status': unit.recruitment_status or 'open',
                    'recruitment_notes': getattr(unit, 'recruitment_notes', None),
                    'is_aviation_only': getattr(unit, 'is_aviation_only', False)
                })

        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_mos_options(self, request):
        """
        Get available recruitment slots based on unit and track
        Step 12: MOS Selection - Shows open positions based on roles

        NOTE: This assumes Role has either a 'mos' or 'required_mos' field.
        If your Role model has a different relationship to MOS, update this method accordingly.
        """
        branch_id = request.query_params.get('branch_id')
        career_track = request.query_params.get('career_track')
        unit_id = request.query_params.get('unit_id')

        if not unit_id:
            return Response(
                {'error': 'unit_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get open recruitment slots for the unit and career track
        slots_query = RecruitmentSlot.objects.filter(
            unit_id=unit_id,
            career_track=career_track,
            is_active=True
        ).select_related('role')

        # Create a dictionary to track MOS slots
        mos_slots = {}

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
                # Option 3: Many-to-many relationship (uncomment if needed)
                # elif hasattr(slot.role, 'mos_set'):
                #     for mos in slot.role.mos_set.all():
                #         # Process each MOS...

                if role_mos:
                    mos_id = str(role_mos.id)
                    if mos_id not in mos_slots:
                        mos_slots[mos_id] = {
                            'id': role_mos.id,
                            'code': role_mos.code,
                            'title': role_mos.title,
                            'category': getattr(role_mos, 'category', ''),
                            'description': getattr(role_mos, 'description', ''),
                            'ait_weeks': getattr(role_mos, 'ait_weeks', 0),
                            'physical_demand_rating': getattr(role_mos, 'physical_demand_rating', ''),
                            'available_slots': 0,
                            'roles': []
                        }

                    mos_slots[mos_id]['available_slots'] += slot.available_slots

                    # Add role info
                    role_info = f"{slot.role.name} ({slot.available_slots} slots)"
                    if role_info not in mos_slots[mos_id]['roles']:
                        mos_slots[mos_id]['roles'].append(role_info)

        # Convert to list and sort by available slots (most available first)
        data = list(mos_slots.values())
        data.sort(key=lambda x: x['available_slots'], reverse=True)

        # If no MOS found with slots but we have a branch, show all entry-level MOS
        # This is a fallback if the Role-MOS relationship isn't set up
        if not data and branch_id:
            try:
                all_mos = MOS.objects.filter(
                    branch_id=branch_id,
                    is_active=True,
                    is_entry_level=True
                )

                # For warrant track, filter to aviation MOS
                if career_track == 'warrant':
                    all_mos = all_mos.filter(category='aviation')

                data = [{
                    'id': mos.id,
                    'code': mos.code,
                    'title': mos.title,
                    'category': getattr(mos, 'category', ''),
                    'description': getattr(mos, 'description', ''),
                    'ait_weeks': getattr(mos, 'ait_weeks', 0),
                    'physical_demand_rating': getattr(mos, 'physical_demand_rating', ''),
                    'available_slots': 1,  # Show as available but limited
                    'roles': ['Position availability varies by unit']
                } for mos in all_mos]

                # Log that we're using the fallback
                print(f"Using MOS fallback for branch {branch_id}, found {len(data)} MOS options")
            except Exception as e:
                print(f"Error in MOS fallback: {e}")

        return Response(data)

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
        Step 16: Submit
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

        if not application.primary_mos:
            errors.append('Primary MOS selection is required')

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
            application.progress.current_step = 17
            application.progress.save()

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

            # Create onboarding progress
            UserOnboardingProgress.objects.get_or_create(
                user=application.user,
                defaults={'application': application}
            )

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

        application.status = ApplicationStatus.REJECTED
        application.decision_at = timezone.now()
        application.reviewer = request.user
        application.reviewer_notes = request.data.get('notes', '')
        application.save()

        # Send rejection notification
        self.send_rejection_notification(application)

        return Response({
            'success': True,
            'message': 'Application rejected'
        })

    def send_discord_notification(self, application):
        """
        Send Discord webhook notification for new application
        Step 18: Discord notification
        """
        webhook_url = os.environ.get('DISCORD_APPLICATION_WEBHOOK')
        if not webhook_url:
            return

        try:
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
                        "name": "MOS",
                        "value": f"{application.primary_mos.code} - {application.primary_mos.title}" if application.primary_mos else "N/A",
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