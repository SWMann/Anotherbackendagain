# backend/apps/units/models_promotion.py
"""
Models for complex rank promotion requirements system
"""
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
from datetime import timedelta


class PromotionRequirementType(BaseModel):
    """Types of requirements that can be defined for promotions"""

    REQUIREMENT_CATEGORIES = [
        ('time_based', 'Time-Based Requirements'),
        ('position_based', 'Position-Based Requirements'),
        ('qualification_based', 'Qualification-Based Requirements'),
        ('deployment_based', 'Deployment-Based Requirements'),
        ('performance_based', 'Performance-Based Requirements'),
        ('administrative', 'Administrative Requirements'),
    ]

    EVALUATION_TYPES = [
        ('time_in_service', 'Total Time in Service'),
        ('time_in_grade', 'Time in Current Grade'),
        ('time_in_unit', 'Time in Current Unit'),
        ('time_in_unit_type', 'Time in Unit Type'),
        ('time_in_position', 'Time in Specific Position'),
        ('time_in_position_type', 'Time in Position Type'),
        ('certification_required', 'Required Certification'),
        ('certifications_count', 'Number of Certifications'),
        ('deployments_count', 'Number of Deployments'),
        ('deployment_time', 'Total Deployment Time'),
        ('deployment_in_position', 'Deployments in Specific Position'),
        ('event_participation', 'Event Participation Count'),
        ('leadership_time', 'Time in Leadership Position'),
        ('command_time', 'Time in Command Position'),
        ('performance_rating', 'Average Performance Rating'),
        ('commendations_count', 'Number of Commendations'),
        ('mos_qualification', 'MOS Qualification Level'),
        ('custom_evaluation', 'Custom Evaluation Function'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=REQUIREMENT_CATEGORIES)
    evaluation_type = models.CharField(max_length=30, choices=EVALUATION_TYPES)
    description = models.TextField(blank=True, null=True)

    # For custom evaluations
    custom_evaluation_function = models.TextField(
        blank=True,
        null=True,
        help_text="Python code for custom evaluation (use with caution)"
    )

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class RankPromotionRequirement(BaseModel):
    """Defines specific requirements for promotion to a rank"""

    rank = models.ForeignKey(
        'units.Rank',
        on_delete=models.CASCADE,
        related_name='promotion_requirements'
    )

    requirement_type = models.ForeignKey(
        PromotionRequirementType,
        on_delete=models.CASCADE
    )

    # Value configuration based on requirement type
    value_required = models.IntegerField(
        default=0,
        help_text="Numeric value required (days, count, etc.)"
    )

    # For position/unit type requirements
    unit_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Specific unit type required"
    )

    position_role = models.ForeignKey(
        'units.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Specific position role required"
    )

    position_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Position category (command, staff, etc.)"
    )

    # For certification requirements
    required_certification = models.ForeignKey(
        'training.TrainingCertificate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    certification_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Category of certifications required"
    )

    # For MOS requirements
    required_mos_level = models.IntegerField(
        null=True,
        blank=True,
        choices=[(10, 'Level 10'), (20, 'Level 20'), (30, 'Level 30'), (40, 'Level 40')]
    )

    # Conditional requirements
    is_mandatory = models.BooleanField(
        default=True,
        help_text="If false, this is an alternative requirement"
    )

    requirement_group = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Group identifier for OR requirements"
    )

    # Display
    display_order = models.IntegerField(default=0)
    display_text = models.CharField(
        max_length=200,
        help_text="Human-readable requirement text"
    )

    # Waivers
    waiverable = models.BooleanField(
        default=False,
        help_text="Can this requirement be waived?"
    )

    waiver_authority = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('unit_commander', 'Unit Commander'),
            ('branch_commander', 'Branch Commander'),
            ('admin', 'Admin Only'),
        ]
    )

    class Meta:
        ordering = ['rank', 'display_order', 'requirement_type']
        unique_together = ['rank', 'requirement_type', 'position_role', 'required_certification']

    def __str__(self):
        return f"{self.rank.abbreviation} - {self.requirement_type.name}"

    def evaluate_for_user(self, user):
        """Evaluate if user meets this requirement"""
        from apps.events.models import EventAttendance
        from apps.training.models import UserCertificate

        evaluation_type = self.requirement_type.evaluation_type

        # Time in service
        if evaluation_type == 'time_in_service':
            if user.join_date:
                days_in_service = (timezone.now() - user.join_date).days
                return days_in_service >= self.value_required, days_in_service
            return False, 0

        # Time in current grade
        elif evaluation_type == 'time_in_grade':
            # This would require tracking when rank was assigned
            # For now, we'll use a simplified version
            if hasattr(user, 'rank_history'):
                last_promotion = user.rank_history.filter(
                    rank=user.current_rank
                ).order_by('-date_assigned').first()
                if last_promotion:
                    days_in_grade = (timezone.now() - last_promotion.date_assigned).days
                    return days_in_grade >= self.value_required, days_in_grade
            return False, 0

        # Time in current unit
        elif evaluation_type == 'time_in_unit':
            if user.unit_assignment_date:
                days_in_unit = (timezone.now() - user.unit_assignment_date).days
                return days_in_unit >= self.value_required, days_in_unit
            return False, 0

        # Time in specific position type
        elif evaluation_type == 'time_in_position_type':
            from apps.units.models import UserPosition

            total_days = 0
            positions = UserPosition.objects.filter(
                user=user,
                position__role__category=self.position_category
            )

            for position in positions:
                start = position.assignment_date
                end = position.end_date or timezone.now()
                total_days += (end - start).days

            return total_days >= self.value_required, total_days

        # Required certification
        elif evaluation_type == 'certification_required':
            if self.required_certification:
                has_cert = UserCertificate.objects.filter(
                    user=user,
                    certificate=self.required_certification,
                    is_active=True
                ).exists()
                return has_cert, 1 if has_cert else 0
            return False, 0

        # Number of deployments
        elif evaluation_type == 'deployments_count':
            deployment_count = EventAttendance.objects.filter(
                user=user,
                event__event_type__in=['Fleet_Battle', 'Ground_Assault', 'Station_Defense'],
                status='Attending',
                check_in_time__isnull=False
            ).count()
            return deployment_count >= self.value_required, deployment_count

        # Time in leadership positions
        elif evaluation_type == 'leadership_time':
            from apps.units.models import UserPosition

            total_days = 0
            positions = UserPosition.objects.filter(
                user=user,
                position__role__is_nco_role=True
            ) | UserPosition.objects.filter(
                user=user,
                position__role__is_command_role=True
            )

            for position in positions.distinct():
                start = position.assignment_date
                end = position.end_date or timezone.now()
                total_days += (end - start).days

            return total_days >= self.value_required, total_days

        # Default: requirement not met
        return False, 0


class UserPromotionProgress(BaseModel):
    """Tracks user's progress toward next rank promotion"""

    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='promotion_progress'
    )

    next_rank = models.ForeignKey(
        'units.Rank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Next eligible rank"
    )

    # Cached evaluation results
    last_evaluation_date = models.DateTimeField(null=True, blank=True)
    requirements_met = models.JSONField(
        default=dict,
        help_text="Map of requirement IDs to (met, current_value) tuples"
    )

    overall_eligible = models.BooleanField(default=False)
    eligibility_percentage = models.FloatField(default=0.0)

    # Waiver tracking
    active_waivers = models.JSONField(
        default=list,
        help_text="List of waived requirement IDs"
    )

    # Board/Review status
    board_eligible = models.BooleanField(default=False)
    board_scheduled_date = models.DateTimeField(null=True, blank=True)
    board_completed_date = models.DateTimeField(null=True, blank=True)
    board_result = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('deferred', 'Deferred'),
        ],
        blank=True,
        null=True
    )

    # Notes
    notes = models.TextField(blank=True, null=True)

    def evaluate_requirements(self):
        """Evaluate all requirements for next rank"""
        if not self.next_rank:
            return

        requirements = self.next_rank.promotion_requirements.filter(
            is_mandatory=True
        ).select_related('requirement_type')

        results = {}
        met_count = 0
        total_count = 0

        for req in requirements:
            # Skip waived requirements
            if str(req.id) in self.active_waivers:
                results[str(req.id)] = (True, "Waived")
                met_count += 1
                total_count += 1
                continue

            met, current_value = req.evaluate_for_user(self.user)
            results[str(req.id)] = (met, current_value)

            if met:
                met_count += 1
            total_count += 1

        # Handle OR requirement groups
        requirement_groups = {}
        for req in self.next_rank.promotion_requirements.filter(
                is_mandatory=False,
                requirement_group__isnull=False
        ):
            group = req.requirement_group
            if group not in requirement_groups:
                requirement_groups[group] = []

            met, current_value = req.evaluate_for_user(self.user)
            requirement_groups[group].append((req, met, current_value))

        # Check if at least one requirement in each group is met
        for group, group_reqs in requirement_groups.items():
            group_met = any(met for _, met, _ in group_reqs)
            if group_met:
                met_count += 1
            total_count += 1

            # Store the best progress from the group
            best_req = max(group_reqs, key=lambda x: x[2] if isinstance(x[2], (int, float)) else 0)
            results[f"group_{group}"] = (group_met, best_req[2])

        # Update progress
        self.requirements_met = results
        self.eligibility_percentage = (met_count / total_count * 100) if total_count > 0 else 0
        self.overall_eligible = met_count == total_count
        self.board_eligible = self.overall_eligible
        self.last_evaluation_date = timezone.now()
        self.save()

        return results

    class Meta:
        ordering = ['user']

    def __str__(self):
        return f"{self.user.username} - Progress to {self.next_rank.abbreviation if self.next_rank else 'N/A'}"


class UserRankHistory(BaseModel):
    """Track user's rank progression history"""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='rank_history'
    )

    rank = models.ForeignKey(
        'units.Rank',
        on_delete=models.CASCADE
    )

    date_assigned = models.DateTimeField()
    date_ended = models.DateTimeField(null=True, blank=True)

    promoted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotions_given'
    )

    promotion_order = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Promotion order number"
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_assigned']
        unique_together = ['user', 'rank', 'date_assigned']

    def __str__(self):
        return f"{self.user.username} - {self.rank.abbreviation} ({self.date_assigned.date()})"


class PromotionWaiver(BaseModel):
    """Track waivers for specific promotion requirements"""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='promotion_waivers'
    )

    requirement = models.ForeignKey(
        RankPromotionRequirement,
        on_delete=models.CASCADE
    )

    waived_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='waivers_granted'
    )

    waiver_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this waiver expires"
    )

    reason = models.TextField()

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-waiver_date']
        unique_together = ['user', 'requirement']

    def __str__(self):
        return f"Waiver for {self.user.username} - {self.requirement.display_text}"