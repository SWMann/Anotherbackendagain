from django.db import models
from apps.core.models import BaseModel


class StandardGroup(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    banner_image_url = models.URLField(blank=True, null=True)
    branch = models.ForeignKey('units.Branch', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='standard_groups')
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   related_name='created_standard_groups')

    def __str__(self):
        return self.name


class StandardSubGroup(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    standard_group = models.ForeignKey(StandardGroup, on_delete=models.CASCADE, related_name='subgroups')
    icon_url = models.URLField(blank=True, null=True)
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   related_name='created_standard_subgroups')

    def __str__(self):
        return f"{self.standard_group.name} - {self.name}"


class Standard(BaseModel):
    title = models.CharField(max_length=200)
    document_number = models.CharField(max_length=50, blank=True, null=True)
    standard_sub_group = models.ForeignKey(StandardSubGroup, on_delete=models.CASCADE, related_name='standards')
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    image_urls = models.JSONField(blank=True, null=True)
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(
        max_length=20,
        choices=[
            ('Draft', 'Draft'),
            ('Active', 'Active'),
            ('Archived', 'Archived')
        ],
        default='Draft'
    )
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_standards')
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_standards')
    approval_date = models.DateTimeField(null=True, blank=True)
    effective_date = models.DateTimeField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    related_standards = models.JSONField(blank=True, null=True)
    related_training = models.JSONField(blank=True, null=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('Basic', 'Basic'),
            ('Intermediate', 'Intermediate'),
            ('Advanced', 'Advanced')
        ],
        default='Basic'
    )
    tags = models.JSONField(blank=True, null=True)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.document_number}: {self.title}" if self.document_number else self.title