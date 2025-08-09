# backend/apps/onboarding/models.py
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
import uuid


class ApplicationWaiverType(BaseModel):
    """Types of waivers/acknowledgments required during application"""
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField(help_text="Full waiver/acknowledgment text")
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    waiver_type = models.CharField(
        max_length=20,
        choices=[
            ('acknowledgment', 'Acknowledgment'),
            ('waiver', 'Waiver'),
            ('agreement', 'Agreement'),
            ('consent', 'Consent')
        ],
        default='acknowledgment'
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class ApplicationStatus(models.TextChoices):
    """Centralized application status choices"""
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under Review'
    INTERVIEW_SCHEDULED = 'interview_scheduled', 'Interview Scheduled'
    INTERVIEW_COMPLETED = 'interview_completed', 'Interview Completed'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    WITHDRAWN = 'withdrawn', 'Withdrawn'
    ON_HOLD = 'on_hold', 'On Hold'


class Application(BaseModel):
    """Enhanced application model for the new flow"""

    # Application tracking
    application_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Auto-generated application number"
    )

    # User information (Step 2: Basic Information)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='applications_v2',
        null=True,
        blank=True
    )
    discord_id = models.CharField(max_length=100)
    discord_username = models.CharField(max_length=150)
    discord_discriminator = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField()

    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    timezone = models.CharField(max_length=50)
    country = models.CharField(max_length=100)

    # Military structure selection (Steps 3-5)
    branch = models.ForeignKey(
        'units.Branch',
        on_delete=models.SET_NULL,
        null=True,
        related_name='applications_v2'
    )

    # Primary unit (Squadron for Navy, Company for Army/Marines)
    primary_unit = models.ForeignKey(
        'units.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_applications'
    )

    # Secondary unit (Division for Navy, Platoon for Army/Marines)
    secondary_unit = models.ForeignKey(
        'units.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secondary_applications'
    )

    # Career track selection (Step 6)
    career_track = models.CharField(
        max_length=20,
        choices=[
            ('enlisted', 'Enlisted'),
            ('warrant', 'Warrant Officer'),
            ('officer', 'Commissioned Officer')
        ]
    )

    # RecruitmentSlot selection (Step 7) - CHANGED FROM MOS
    selected_recruitment_slot = models.ForeignKey(
        'units.RecruitmentSlot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications',
        help_text="The recruitment slot/position applied for"
    )

    # Alternative recruitment slots (optional)
    alternate_recruitment_slot_1 = models.ForeignKey(
        'units.RecruitmentSlot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alternate1_applications'
    )

    alternate_recruitment_slot_2 = models.ForeignKey(
        'units.RecruitmentSlot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alternate2_applications'
    )

    # Experience and motivation (Step 8)
    previous_experience = models.TextField(
        help_text="Previous gaming/simulation experience"
    )
    reason_for_joining = models.TextField(
        help_text="Why do you want to join this unit?"
    )

    # Role-specific information (Step 9)
    role_specific_answers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Answers to role/position specific questions"
    )

    # Aviation specific
    has_flight_experience = models.BooleanField(default=False)
    flight_hours = models.IntegerField(default=0)

    # Availability
    weekly_availability_hours = models.IntegerField(
        default=0,
        help_text="Hours available per week"
    )
    can_attend_mandatory_events = models.BooleanField(default=True)
    availability_notes = models.TextField(blank=True, null=True)

    # Additional role-specific fields
    leadership_experience = models.TextField(blank=True, null=True)
    technical_experience = models.TextField(blank=True, null=True)

    # Referral
    referrer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals_v2'
    )
    referral_source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="How did you hear about us?"
    )

    # Status tracking
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT
    )

    # Important dates
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    interview_scheduled_at = models.DateTimeField(null=True, blank=True)
    interview_completed_at = models.DateTimeField(null=True, blank=True)
    decision_at = models.DateTimeField(null=True, blank=True)

    # Review information
    reviewer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications_v2'
    )
    reviewer_notes = models.TextField(blank=True, null=True)
    interview_notes = models.TextField(blank=True, null=True)

    # Discord notification tracking
    discord_notification_sent = models.BooleanField(default=False)
    discord_notification_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['application_number']),
            models.Index(fields=['discord_id']),
            models.Index(fields=['status']),
            models.Index(fields=['branch', 'career_track']),
        ]

    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate application number: APP-YYYYMMDD-XXXX
            date_str = timezone.now().strftime('%Y%m%d')
            last_app = Application.objects.filter(
                application_number__startswith=f'APP-{date_str}'
            ).order_by('-application_number').first()

            if last_app:
                last_num = int(last_app.application_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.application_number = f'APP-{date_str}-{new_num:04d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_number} - {self.discord_username}"

    @property
    def selected_role(self):
        """Get the role from the selected recruitment slot"""
        if self.selected_recruitment_slot:
            return self.selected_recruitment_slot.role
        return None

    @property
    def selected_position_unit(self):
        """Get the unit from the selected recruitment slot"""
        if self.selected_recruitment_slot:
            return self.selected_recruitment_slot.unit
        return None


class ApplicationWaiver(BaseModel):
    """Track waiver/acknowledgment acceptance for each application"""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='waivers'
    )
    waiver_type = models.ForeignKey(
        ApplicationWaiverType,
        on_delete=models.CASCADE
    )
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['application', 'waiver_type']

    def save(self, *args, **kwargs):
        if self.accepted and not self.accepted_at:
            self.accepted_at = timezone.now()
        super().save(*args, **kwargs)


class ApplicationProgress(BaseModel):
    """Track progress through the application steps"""
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='progress'
    )

    # Step completion tracking
    basic_info_completed = models.BooleanField(default=False)
    branch_selected = models.BooleanField(default=False)
    primary_unit_selected = models.BooleanField(default=False)
    secondary_unit_selected = models.BooleanField(default=False)
    track_selected = models.BooleanField(default=False)
    position_selected = models.BooleanField(default=False)  # Changed from mos_selected
    experience_completed = models.BooleanField(default=False)
    role_specific_completed = models.BooleanField(default=False)
    waivers_completed = models.BooleanField(default=False)

    # Current step tracking
    current_step = models.IntegerField(default=2)  # Start at basic info
    last_saved_at = models.DateTimeField(auto_now=True)

    # Completion percentage
    completion_percentage = models.IntegerField(default=0)

    def calculate_completion(self):
        """Calculate the completion percentage"""
        steps = [
            self.basic_info_completed,
            self.branch_selected,
            self.primary_unit_selected,
            self.secondary_unit_selected,
            self.track_selected,
            self.position_selected,
            self.experience_completed,
            self.role_specific_completed,
            self.waivers_completed
        ]
        completed = sum(1 for step in steps if step)
        self.completion_percentage = int((completed / len(steps)) * 100)
        return self.completion_percentage

    def save(self, *args, **kwargs):
        self.calculate_completion()
        super().save(*args, **kwargs)


class ApplicationComment(BaseModel):
    """Internal comments on applications"""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    is_visible_to_applicant = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class ApplicationInterview(BaseModel):
    """Track interview scheduling and results"""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    scheduled_at = models.DateTimeField()
    scheduled_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='scheduled_interviews'
    )
    interviewer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_interviews'
    )
    interview_type = models.CharField(
        max_length=20,
        choices=[
            ('initial', 'Initial Interview'),
            ('technical', 'Technical Interview'),
            ('command', 'Command Interview'),
            ('final', 'Final Interview')
        ],
        default='initial'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
            ('rescheduled', 'Rescheduled')
        ],
        default='scheduled'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True, null=True)
    recommendation = models.CharField(
        max_length=25,
        choices=[
            ('strongly_recommend', 'Strongly Recommend'),
            ('recommend', 'Recommend'),
            ('neutral', 'Neutral'),
            ('not_recommend', 'Do Not Recommend'),
            ('strongly_not_recommend', 'Strongly Do Not Recommend')
        ],
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['scheduled_at']


# Keep existing models for backward compatibility but mark as deprecated
class CommissionStage(BaseModel):
    """DEPRECATED - Use ApplicationProgress instead"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(default=0)
    requirements = models.TextField(blank=True, null=True)
    badge_image_url = models.URLField(blank=True, null=True)
    time_requirement = models.IntegerField(null=True, blank=True, help_text="Minimum days required at this stage")
    training_requirements = models.JSONField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order_index']


class UserOnboardingProgress(BaseModel):
    """Track user's onboarding after application approval"""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='onboarding_progress')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True)

    # Onboarding milestones
    discord_roles_assigned = models.BooleanField(default=False)
    orientation_completed = models.BooleanField(default=False)
    basic_training_enrolled = models.BooleanField(default=False)
    basic_training_completed = models.BooleanField(default=False)
    unit_assigned = models.BooleanField(default=False)
    mentor_assigned = models.BooleanField(default=False)

    # Dates
    discord_roles_assigned_at = models.DateTimeField(null=True, blank=True)
    orientation_completed_at = models.DateTimeField(null=True, blank=True)
    basic_training_enrolled_at = models.DateTimeField(null=True, blank=True)
    basic_training_completed_at = models.DateTimeField(null=True, blank=True)
    unit_assigned_at = models.DateTimeField(null=True, blank=True)
    mentor_assigned_at = models.DateTimeField(null=True, blank=True)

    onboarding_status = models.CharField(
        max_length=50,
        choices=[
            ('pending_discord', 'Pending Discord Setup'),
            ('pending_orientation', 'Pending Orientation'),
            ('in_training', 'In Basic Training'),
            ('pending_assignment', 'Pending Unit Assignment'),
            ('active', 'Active Member'),
            ('inactive', 'Inactive'),
        ],
        default='pending_discord'
    )

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Onboarding: {self.user.username}"


class MentorAssignment(BaseModel):
    """Mentor assignments for new members"""
    recruit = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='mentor_assignments')
    mentor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='mentee_assignments')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('terminated', 'Terminated'),
            ('on_hold', 'On Hold')
        ],
        default='active'
    )
    assignment_notes = models.TextField(blank=True, null=True)
    progress_reports = models.JSONField(blank=True, null=True)
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                    related_name='mentor_assignments_made')

    def __str__(self):
        return f"{self.mentor.username} mentoring {self.recruit.username}"