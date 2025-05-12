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
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
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