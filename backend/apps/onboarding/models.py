from django.db import models
from apps.core.models import BaseModel


class CommissionStage(BaseModel):
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



class Application(BaseModel):
    discord_id = models.CharField(max_length=100)
    username = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    preferred_branch = models.ForeignKey('units.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    preferred_unit = models.ForeignKey('units.Unit', on_delete=models.SET_NULL, null=True, blank=True)
    motivation = models.TextField()
    experience = models.TextField(blank=True, null=True)
    referrer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='referrals')
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
            ('Interviewing', 'Interviewing')
        ],
        default='Pending'
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_applications')
    review_date = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True, null=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    onboarding_complete = models.BooleanField(default=False)

    # Add these fields to the Application model
    preferred_mos = models.ManyToManyField(
        'units.MOS',
        blank=True,
        related_name='applications',
        help_text="User's preferred MOS choices (up to 3)"
    )
    mos_priority_1 = models.ForeignKey(
        'units.MOS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='first_choice_applications'
    )
    mos_priority_2 = models.ForeignKey(
        'units.MOS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='second_choice_applications'
    )
    mos_priority_3 = models.ForeignKey(
        'units.MOS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='third_choice_applications'
    )
    meets_mos_requirements = models.BooleanField(
        default=False,
        help_text="Applicant meets requirements for desired MOS"
    )
    mos_waiver_requested = models.BooleanField(
        default=False,
        help_text="Applicant requesting waiver for MOS requirements"
    )
    mos_waiver_reason = models.TextField(blank=True, null=True)

    preferred_brigade = models.ForeignKey(
        'units.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brigade_applications',
        limit_choices_to={'unit_level': 'brigade'}
    )

    preferred_battalion = models.ForeignKey(
        'units.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='battalion_applications',
        limit_choices_to={'unit_level': 'battalion'}
    )

    preferred_platoon = models.ForeignKey(
        'units.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='platoon_applications',
        limit_choices_to={'unit_level': 'platoon'}
    )

    # Validate aviation requirements
    has_flight_experience = models.BooleanField(
        default=False,
        help_text="Applicant claims flight simulation experience"
    )

    flight_hours = models.IntegerField(
        default=0,
        help_text="Self-reported flight simulation hours"
    )

    def clean(self):
        # Validate aviation unit applications
        if self.preferred_unit and self.preferred_unit.is_aviation_only:
            if self.entry_path != 'warrant':
                raise ValueError(
                    "Aviation units only accept warrant officer candidates"
                )
            if not self.has_flight_experience:
                raise ValueError(
                    "Aviation units require flight experience"
                )

    def __str__(self):
        return f"Application from {self.username}"


class UserOnboardingProgress(BaseModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='onboarding_progress')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True)
    bit_event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='bit_attendees')
    branch_application = models.ForeignKey('BranchApplication', on_delete=models.SET_NULL, null=True, blank=True)
    branch_induction_event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True,
                                               related_name='induction_attendees')
    onboarding_status = models.CharField(
        max_length=50,
        choices=[
            ('Applied', 'Applied'),
            ('BIT Completed', 'BIT Completed'),
            ('Branch Applied', 'Branch Applied'),
            ('Branch Inducted', 'Branch Inducted'),
            ('Unit Assigned', 'Unit Assigned'),
            ('Active', 'Active'),
        ],
        default='Applied'
    )
    officer_track = models.BooleanField(default=False)
    warrant_track = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Onboarding progress for {self.user.username}"


class BranchApplication(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='branch_applications')
    branch = models.ForeignKey('units.Branch', on_delete=models.CASCADE, related_name='branch_applications')
    application_type = models.CharField(
        max_length=20,
        choices=[
            ('Enlisted', 'Enlisted'),
            ('Officer', 'Officer'),
            ('Warrant', 'Warrant')
        ],
        default='Enlisted'
    )
    motivation = models.TextField()
    experience = models.TextField(blank=True, null=True)
    preferred_role = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
            ('Under Review', 'Under Review')
        ],
        default='Pending'
    )
    reviewer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_branch_applications')
    review_date = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True, null=True)
    approval_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s application to {self.branch.name}"


class MentorAssignment(BaseModel):
    recruit = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='mentor_assignments')
    mentor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='mentee_assignments')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Completed', 'Completed'),
            ('Terminated', 'Terminated')
        ],
        default='Active'
    )
    assignment_notes = models.TextField(blank=True, null=True)
    progress_reports = models.JSONField(blank=True, null=True)
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                    related_name='mentor_assignments_made')

    def __str__(self):
        return f"{self.mentor.username} mentoring {self.recruit.username}"