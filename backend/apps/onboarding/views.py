from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import CommissionStage, Application, UserOnboardingProgress, BranchApplication, MentorAssignment
from .serializers import (
    CommissionStageSerializer, ApplicationListSerializer, ApplicationDetailSerializer,
    ApplicationCreateSerializer, ApplicationUpdateSerializer, ApplicationStatusSerializer,
    UserOnboardingProgressSerializer, BranchApplicationSerializer, BranchApplicationCreateSerializer,
    BranchApplicationUpdateSerializer, MentorAssignmentSerializer, MentorAssignmentCreateSerializer,
    NextRequirementsSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


class CommissionStageViewSet(viewsets.ModelViewSet):
    queryset = CommissionStage.objects.all().order_by('order_index')
    serializer_class = CommissionStageSerializer
    permission_classes = [IsAdminOrReadOnly]


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all().order_by('-submission_date')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'preferred_branch', 'preferred_unit']
    search_fields = ['discord_id', 'username', 'email', 'motivation', 'experience']
    ordering_fields = ['submission_date', 'review_date', 'interview_date']

    def get_permissions(self):
        if self.action in ['create', 'status']:
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        elif self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        elif self.action == 'status':
            return ApplicationStatusSerializer
        return ApplicationDetailSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def status(self, request):
        """Check application status by Discord ID."""
        discord_id = request.query_params.get('discord_id')

        if not discord_id:
            return Response({"detail": "Discord ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        application = get_object_or_404(Application, discord_id=discord_id)
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class UserOnboardingProgressViewSet(viewsets.ModelViewSet):
    queryset = UserOnboardingProgress.objects.all()
    serializer_class = UserOnboardingProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['onboarding_status', 'officer_track', 'warrant_track']
    ordering_fields = ['last_updated']
    ordering = ['-last_updated']

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        """Get current user's onboarding progress."""
        try:
            progress = UserOnboardingProgress.objects.get(user=request.user)
            serializer = self.get_serializer(progress)
            return Response(serializer.data)
        except UserOnboardingProgress.DoesNotExist:
            return Response(
                {"detail": "Onboarding progress not found for user."},
                status=status.HTTP_404_NOT_FOUND
            )


class BranchApplicationViewSet(viewsets.ModelViewSet):
    queryset = BranchApplication.objects.all().order_by('-submission_date')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['branch', 'application_type', 'status', 'user']
    ordering_fields = ['submission_date', 'review_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return BranchApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BranchApplicationUpdateSerializer
        return BranchApplicationSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        """Get current user's branch applications."""
        applications = BranchApplication.objects.filter(user=request.user)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def templates(self, request):
        """Get branch application templates."""
        branch_id = request.query_params.get('branch_id')

        if not branch_id:
            return Response({"detail": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # This is a placeholder - in a real implementation, you'd fetch actual templates
        # from a database or other storage
        templates = {
            "enlisted": {
                "motivation_prompt": "Why do you want to join as an enlisted member?",
                "experience_prompt": "What relevant experience do you have?",
                "role_prompt": "What role are you interested in?"
            },
            "officer": {
                "motivation_prompt": "Why do you want to join as an officer?",
                "experience_prompt": "What leadership experience do you have?",
                "role_prompt": "What officer role are you interested in?"
            },
            "warrant": {
                "motivation_prompt": "Why do you want to join as a warrant officer?",
                "experience_prompt": "What technical experience do you have?",
                "role_prompt": "What warrant officer role are you interested in?"
            }
        }

        return Response(templates)


class MentorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = MentorAssignment.objects.all().order_by('-start_date')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recruit', 'mentor', 'status']
    ordering_fields = ['start_date', 'end_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return MentorAssignmentCreateSerializer
        return MentorAssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_progress_report(self, request, pk=None):
        """Add a progress report to a mentor assignment."""
        assignment = self.get_object()

        # Check if user is the mentor or an admin
        if not (request.user.is_admin or request.user == assignment.mentor):
            return Response(
                {"detail": "You do not have permission to add progress reports."},
                status=status.HTTP_403_FORBIDDEN
            )

        report = request.data.get('report')

        if not report:
            return Response({"detail": "Report content is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get existing reports or initialize empty list
        reports = assignment.progress_reports or []

        # Add new report with timestamp
        reports.append({
            "date": timezone.now().isoformat(),
            "author": request.user.username,
            "content": report
        })

        # Save updated reports
        assignment.progress_reports = reports
        assignment.save()

        return Response({
            "id": assignment.id,
            "latest_report": reports[-1]
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser()])
    def complete(self, request, pk=None):
        """Mark a mentor assignment as completed."""
        assignment = self.get_object()
        notes = request.data.get('notes', '')

        assignment.status = 'Completed'
        assignment.end_date = timezone.now()
        assignment.assignment_notes += f"\n\nCompleted on {timezone.now().strftime('%Y-%m-%d')}. Notes: {notes}"
        assignment.save()

        return Response({
            "id": assignment.id,
            "status": assignment.status,
            "end_date": assignment.end_date
        })


class UserOnboardingActionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser()])
    def complete_bit(self, request, pk=None):
        """Mark BIT as completed for a user."""
        event = get_object_or_404('events.Event', pk=pk)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        # Update user's onboarding progress
        progress, created = UserOnboardingProgress.objects.get_or_create(
            user=user,
            defaults={
                'onboarding_status': 'BIT Completed',
                'bit_event': event
            }
        )

        if not created:
            progress.onboarding_status = 'BIT Completed'
            progress.bit_event = event
            progress.save()

        # Update user model
        user.bit_completion_date = timezone.now()
        user.onboarding_status = 'BIT Completed'
        user.save()

        return Response({
            "user_id": user.id,
            "username": user.username,
            "onboarding_status": user.onboarding_status,
            "bit_completion_date": user.bit_completion_date
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser()])
    def complete_induction(self, request, pk=None):
        """Mark branch induction as completed for a user."""
        event = get_object_or_404('events.Event', pk=pk)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        # Update user's onboarding progress
        progress, created = UserOnboardingProgress.objects.get_or_create(
            user=user,
            defaults={
                'onboarding_status': 'Branch Inducted',
                'branch_induction_event': event
            }
        )

        if not created:
            progress.onboarding_status = 'Branch Inducted'
            progress.branch_induction_event = event
            progress.save()

        # Update user model
        user.branch_induction_date = timezone.now()
        user.onboarding_status = 'Branch Inducted'
        user.save()

        return Response({
            "user_id": user.id,
            "username": user.username,
            "onboarding_status": user.onboarding_status,
            "branch_induction_date": user.branch_induction_date
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser()])
    def assign_unit(self, request, pk=None):
        """Assign user to a unit."""
        user = get_object_or_404(User, pk=pk)
        unit_id = request.data.get('unit_id')
        position_id = request.data.get('position_id')

        if not unit_id:
            return Response({"detail": "Unit ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        unit = get_object_or_404('units.Unit', id=unit_id)

        # Update user model
        user.primary_unit = unit
        user.unit_assignment_date = timezone.now()
        user.onboarding_status = 'Unit Assigned'
        user.save()

        # Update user's onboarding progress
        progress, created = UserOnboardingProgress.objects.get_or_create(
            user=user,
            defaults={'onboarding_status': 'Unit Assigned'}
        )

        if not created:
            progress.onboarding_status = 'Unit Assigned'
            progress.save()

        # Assign position if provided
        if position_id:
            from apps.units.models import Position, UserPosition
            position = get_object_or_404(Position, id=position_id)

            UserPosition.objects.create(
                user=user,
                position=position,
                unit=unit,
                is_primary=True
            )

        return Response({
            "user_id": user.id,
            "username": user.username,
            "onboarding_status": user.onboarding_status,
            "unit": unit.name,
            "unit_assignment_date": user.unit_assignment_date
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def next_requirements(self, request):
        """Get requirements for next stage."""
        try:
            progress = UserOnboardingProgress.objects.get(user=request.user)
            serializer = NextRequirementsSerializer(progress)
            return Response(serializer.data)
        except UserOnboardingProgress.DoesNotExist:
            return Response(
                {"detail": "Onboarding progress not found for user."},
                status=status.HTTP_404_NOT_FOUND
            )