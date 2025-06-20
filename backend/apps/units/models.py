# backend/apps/units/models.py
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class Branch(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    banner_image_url = models.URLField(blank=True, null=True)
    color_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Rank(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='ranks')
    tier = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    insignia_image_url = models.URLField(blank=True, null=True)
    min_time_in_service = models.IntegerField(default=0, help_text="Days required in service")
    min_time_in_grade = models.IntegerField(default=0, help_text="Days required in current grade")
    color_code = models.CharField(max_length=20, blank=True, null=True)
    is_officer = models.BooleanField(default=False)
    is_enlisted = models.BooleanField(default=False)
    is_warrant = models.BooleanField(default=False)

    class Meta:
        ordering = ['branch', 'tier']

    def __str__(self):
        return f"{self.branch.abbreviation} {self.abbreviation}"


class Unit(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='units')
    parent_unit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subunits')
    unit_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. Division, Battalion, Squad")
    description = models.TextField(blank=True, null=True)
    emblem_url = models.URLField(blank=True, null=True)
    banner_image_url = models.URLField(blank=True, null=True)
    motto = models.CharField(max_length=200, blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    recruitment_status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open for Recruitment'),
            ('limited', 'Limited Recruitment'),
            ('closed', 'Closed to Recruitment'),
            ('frozen', 'Temporarily Frozen')
        ],
        default='open'
    )

    max_personnel = models.IntegerField(
        default=0,
        help_text="Maximum authorized personnel for this unit"
    )

    target_personnel = models.IntegerField(
        default=0,
        help_text="Target personnel strength"
    )

    recruitment_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about recruitment status/requirements"
    )

    # Add fields for better hierarchy tracking
    unit_level = models.CharField(
        max_length=20,
        choices=[
            ('division', 'Division'),
            ('brigade', 'Brigade'),
            ('battalion', 'Battalion'),
            ('company', 'Company'),
            ('platoon', 'Platoon'),
            ('squad', 'Squad'),
            ('team', 'Team')
        ],
        blank=True,
        null=True
    )

    unit_designation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Military designation (e.g., '1st PLT, A/1-61 IN')"
    )

    # Aviation-specific flag
    is_aviation_only = models.BooleanField(
        default=False,
        help_text="Unit restricted to aviation warrant officers only"
    )

    # Add method to check if unit is accepting applications
    def is_accepting_applications(self):
        """Check if unit and all parent units are open for recruitment"""
        if self.recruitment_status in ['closed', 'frozen']:
            return False

        # Check parent units recursively
        if self.parent_unit:
            return self.parent_unit.is_accepting_applications()

        return True

    def get_available_slots(self):
        """Calculate available slots based on positions"""
        total_positions = self.positions.filter(is_active=True).count()
        filled_positions = self.positions.filter(
            is_active=True,
            is_vacant=False
        ).count()
        return total_positions - filled_positions
    def __str__(self):
        return self.name


class Role(BaseModel):
    """Template for positions that can be instantiated across units"""

    # Basic Information
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Role Category
    category = models.CharField(max_length=50, choices=[
        ('command', 'Command'),
        ('staff', 'Staff'),
        ('nco', 'Non-Commissioned Officer'),
        ('specialist', 'Specialist'),
        ('trooper', 'Trooper'),
        ('support', 'Support'),
        ('medical', 'Medical'),
        ('logistics', 'Logistics'),
        ('intelligence', 'Intelligence'),
        ('communications', 'Communications'),
        ('aviation', 'Aviation'),
        ('armor', 'Armor'),
        ('infantry', 'Infantry'),
    ])

    # Role Type Flags
    is_command_role = models.BooleanField(default=False)
    is_staff_role = models.BooleanField(default=False)
    is_nco_role = models.BooleanField(default=False)
    is_specialist_role = models.BooleanField(default=False)

    # Hierarchy Information
    parent_role = models.ForeignKey('self', on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='subordinate_roles',
                                    help_text="Typical reporting relationship")

    # Rank Requirements
    min_rank = models.ForeignKey('Rank', on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 related_name='min_rank_roles')
    max_rank = models.ForeignKey('Rank', on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 related_name='max_rank_roles')
    typical_rank = models.ForeignKey('Rank', on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='typical_rank_roles')

    # Branch Restrictions
    allowed_branches = models.ManyToManyField('Branch',
                                              blank=True,
                                              related_name='allowed_roles',
                                              help_text="Leave empty for all branches")

    # Unit Type Restrictions
    allowed_unit_types = models.JSONField(default=list, blank=True,
                                          help_text="List of unit types where this role can exist")

    # Requirements - Note: Remove these if training app doesn't exist yet
    # required_certifications = models.ManyToManyField('training.Certificate',
    #                                                 blank=True,
    #                                                 related_name='required_for_roles')
    # desired_certifications = models.ManyToManyField('training.Certificate',
    #                                                blank=True,
    #                                                related_name='desired_for_roles')

    # Service Requirements
    min_time_in_service = models.IntegerField(default=0,
                                              help_text="Days required in service")
    min_time_in_grade = models.IntegerField(default=0,
                                            help_text="Days required in current rank")
    min_operations_count = models.IntegerField(default=0,
                                               help_text="Minimum operations attended")

    # Role Details
    responsibilities = models.TextField(blank=True, null=True)
    authorities = models.TextField(blank=True, null=True,
                                   help_text="What this role is authorized to do")

    # Display Information
    icon_url = models.URLField(blank=True, null=True)
    badge_url = models.URLField(blank=True, null=True)
    color_code = models.CharField(max_length=20, blank=True, null=True)

    # Slot Configuration
    default_slots_per_unit = models.IntegerField(default=1,
                                                 help_text="Default number of positions when creating in a unit")
    max_slots_per_unit = models.IntegerField(default=1,
                                             help_text="Maximum allowed positions of this role per unit")

    # Metadata
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0,
                                     help_text="Display order within category")

    class Meta:
        ordering = ['category', 'sort_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Position(BaseModel):
    """Specific instance of a Role within a Unit"""

    # Add these fields to the Position model in backend/apps/units/models.py

    # In the Position class, add these fields:
    # ORBAT Display fields
    display_order = models.IntegerField(
        default=0,
        help_text="Order of display among siblings in ORBAT"
    )
    show_in_orbat = models.BooleanField(
        default=True,
        help_text="Whether to show this position in ORBAT views"
    )

    # You can also add a property to get the current holder


    # Additional display properties
    orbat_display_level = models.CharField(max_length=20, choices=[
        ('full', 'Full Details'),
        ('summary', 'Summary Only'),
        ('minimal', 'Minimal Info')
    ], default='full')

    # Command relationships
    reports_to_external = models.ForeignKey('self', on_delete=models.SET_NULL,
                                            null=True, blank=True,
                                            related_name='external_subordinates',
                                            help_text="For positions that report outside their unit")
    # Role Reference
    role = models.ForeignKey('Role', on_delete=models.CASCADE,
                             related_name='positions', blank=True, null=True, )

    # Unit Assignment
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE,
                             related_name='positions',  blank=True, null=True,)

    # Position-Specific Information
    title = models.CharField(max_length=200, blank=True, null=True,
                             help_text="Override title for this specific position")
    identifier = models.CharField(max_length=50, blank=True, null=True,
                                  help_text="Additional identifier (e.g., 'Alpha', '1st')")

    # Hierarchy within Unit
    parent_position = models.ForeignKey('self', on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name='subordinate_positions')

    # Status
    is_active = models.BooleanField(default=True)
    is_vacant = models.BooleanField(default=True)

    # Override Requirements (optional)
    override_min_rank = models.ForeignKey('Rank', on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='override_min_positions')
    override_max_rank = models.ForeignKey('Rank', on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='override_max_positions')
    additional_requirements = models.TextField(blank=True, null=True)

    # Metadata
    notes = models.TextField(blank=True, null=True)

    is_available_for_recruitment = models.BooleanField(
        default=True,
        help_text="Whether this specific position can be applied for"
    )

    recruitment_priority = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical - Fill Immediately'),
            ('high', 'High Priority'),
            ('normal', 'Normal Priority'),
            ('low', 'Low Priority'),
            ('hold', 'On Hold')
        ],
        default='normal'
    )

    # Track position requirements more specifically
    requires_flight_qualification = models.BooleanField(
        default=False,
        help_text="Position requires aviation qualifications"
    )

    class Meta:
        ordering = ['unit', 'role__sort_order']
        unique_together = ['unit', 'role', 'identifier']

    def __str__(self):
        if self.identifier:
            return f"{self.unit.abbreviation} {self.identifier} {self.role.name}"
        return f"{self.unit.abbreviation} {self.role.name}"



    @property
    def current_holder(self):
        """Get the current active primary assignment holder"""
        active_assignment = self.assignments.filter(
            status='active',
            assignment_type='primary'
        ).select_related('user', 'user__current_rank').first()

        if active_assignment:
            return active_assignment.user
        return None

    @property
    def display_title(self):
        """Get the display title for this position"""
        if self.title:
            return self.title
        if self.identifier:
            return f"{self.identifier} {self.role.name}"
        return self.role.name

    @property
    def min_rank(self):
        """Get effective minimum rank (override or role default)"""
        if self.override_min_rank:
            return self.override_min_rank
        if self.role:
            return self.role.min_rank
        return None

    @property
    def max_rank(self):
        """Get effective maximum rank (override or role default)"""
        if self.override_max_rank:
            return self.override_max_rank
        if self.role:
            return self.role.max_rank
        return None

    @property
    def commander_of_unit(self):
        """Get the unit this position commands, if any"""
        if self.role.is_command_role:
            return self.unit
        return None


class UserPosition(BaseModel):
    """Assignment of a User to a specific Position"""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                             related_name='position_assignments')
    position = models.ForeignKey('Position', on_delete=models.CASCADE,
                                 related_name='assignments')

    # Assignment Details
    assignment_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='positions_assigned')

    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('temporary', 'Temporary'),
        ('training', 'Training'),
        ('suspended', 'Suspended'),
        ('ended', 'Ended')
    ], default='active')

    # Type
    assignment_type = models.CharField(max_length=20, choices=[
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('acting', 'Acting'),
        ('assistant', 'Assistant')
    ], default='primary')

    # Dates
    effective_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Documentation
    order_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-assignment_date']

    def __str__(self):
        return f"{self.user.username} - {self.position.display_title}"

    def clean(self):
        # Validate only one active primary assignment per position
        if self.status == 'active' and self.assignment_type == 'primary':
            existing = UserPosition.objects.filter(
                position=self.position,
                status='active',
                assignment_type='primary'
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("This position already has an active primary assignment.")

    def save(self, *args, **kwargs):
        self.clean()
        # Update position vacancy status
        if self.status == 'active':
            self.position.is_vacant = False
            self.position.save()
        super().save(*args, **kwargs)

    @property
    def unit(self):
        """Compatibility property for existing code"""
        return self.position.unit

    @property
    def is_primary(self):
        """Compatibility property for existing code"""
        return self.assignment_type == 'primary'


class RecruitmentSlot(BaseModel):
    """
    Track recruitment slots at various unit levels
    Allows fine-grained control over available positions
    """
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        related_name='recruitment_slots'
    )

    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        related_name='recruitment_slots'
    )

    career_track = models.CharField(
        max_length=20,
        choices=[
            ('enlisted', 'Enlisted'),
            ('warrant', 'Warrant Officer'),
            ('officer', 'Commissioned Officer')
        ]
    )

    total_slots = models.IntegerField(default=0)
    filled_slots = models.IntegerField(default=0)
    reserved_slots = models.IntegerField(
        default=0,
        help_text="Slots reserved for incoming personnel"
    )

    is_active = models.BooleanField(default=True)

    notes = models.TextField(blank=True, null=True)

    @property
    def available_slots(self):
        return self.total_slots - (self.filled_slots + self.reserved_slots)

    class Meta:
        unique_together = ['unit', 'role', 'career_track']



class UnitStrengthReport(BaseModel):
    """
    Track unit strength over time for reporting
    """
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        related_name='strength_reports'
    )

    report_date = models.DateField(auto_now_add=True)

    authorized_strength = models.IntegerField()
    assigned_strength = models.IntegerField()
    present_strength = models.IntegerField()

    officer_count = models.IntegerField(default=0)
    warrant_count = models.IntegerField(default=0)
    enlisted_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-report_date']
        unique_together = ['unit', 'report_date']

# Keep existing models for backwards compatibility
class UnitHierarchyView(BaseModel):
    """Stores different hierarchy view configurations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    view_type = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Organization'),
            ('branch', 'Branch Specific'),
            ('custom', 'Custom View'),
            ('operational', 'Operational Structure'),
            ('administrative', 'Administrative Structure')
        ],
        default='full'
    )

    # React Flow layout configuration
    layout_config = models.JSONField(default=dict, blank=True)

    # Node positions and styling
    node_positions = models.JSONField(default=dict, blank=True)
    node_styles = models.JSONField(default=dict, blank=True)

    # Filter configuration
    filter_config = models.JSONField(default=dict, blank=True)

    # Units included in this view (null means all units)
    included_units = models.ManyToManyField('Unit', blank=True, related_name='hierarchy_views')

    # View settings
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    show_vacant_positions = models.BooleanField(default=True)
    show_personnel_count = models.BooleanField(default=True)

    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   related_name='created_hierarchy_views')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.view_type})"

    def save(self, *args, **kwargs):
        # Ensure only one default view
        if self.is_default:
            UnitHierarchyView.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class UnitHierarchyNode(BaseModel):
    """Stores custom node data for hierarchy views"""
    hierarchy_view = models.ForeignKey(UnitHierarchyView, on_delete=models.CASCADE, related_name='nodes')
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)

    # Position in the hierarchy view
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)

    # Custom styling for this node in this view
    custom_style = models.JSONField(default=dict, blank=True)

    # Override display settings
    show_details = models.BooleanField(default=True)
    expanded = models.BooleanField(default=True)

    class Meta:
        unique_together = ['hierarchy_view', 'unit']

    def __str__(self):
        return f"{self.unit.name} in {self.hierarchy_view.name}"