from django.db import models
from apps.core.models import BaseModel


class Ship(BaseModel):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50, blank=True, null=True)
    class_type = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_ships')
    assigned_unit = models.ForeignKey('units.Unit', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='assigned_ships')
    description = models.TextField(blank=True, null=True)
    specifications = models.JSONField(blank=True, null=True)
    primary_role = models.CharField(max_length=100)
    secondary_roles = models.JSONField(blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    beam = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    crew_capacity = models.IntegerField(blank=True, null=True)
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )
    approval_date = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_ships')
    primary_image_url = models.URLField(blank=True, null=True)
    gallery_images = models.JSONField(blank=True, null=True)
    model_file_url = models.URLField(blank=True, null=True)
    is_flagship = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.class_type})"