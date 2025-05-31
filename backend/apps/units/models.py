from django.db import models
from apps.core.models import BaseModel


class Branch(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    banner_image_url = models.URLField(blank=True, null=True)
    color_code = models.CharField(max_length=20, blank=True, null=True)
    commander_position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='commanded_branch')

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
    commander_position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='commanded_unit')
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.name


class Position(BaseModel):
    title = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='positions')
    parent_position = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='subordinate_positions')
    description = models.TextField(blank=True, null=True)
    min_rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='min_rank_positions')
    max_rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='max_rank_positions')
    is_command_position = models.BooleanField(default=False)
    is_staff_position = models.BooleanField(default=False)
    required_certifications = models.JSONField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    max_slots = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.unit.abbreviation} {self.title}"


class UserPosition(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_positions')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    assignment_date = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('Active', 'Active'),
        ('Temporary', 'Temporary'),
        ('Training', 'Training')
    ], default='Active')
    order_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.position.title} ({self.unit.abbreviation})"

class UnitHierarchyView(BaseModel):
    """Stores different hierarchy view configurations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    view_type = models.CharField(
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