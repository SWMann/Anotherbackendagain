# backend/apps/vehicles/models.py
from django.db import models
from apps.core.models import BaseModel


class Vehicle(BaseModel):
    name = models.CharField(max_length=200)
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ('Tank', 'Tank'),
            ('APC', 'Armored Personnel Carrier'),
            ('IFV', 'Infantry Fighting Vehicle'),
            ('Artillery', 'Artillery'),
            ('Helicopter', 'Helicopter'),
            ('Transport', 'Transport'),
            ('Support', 'Support'),
            ('Other', 'Other')
        ]
    )
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    assigned_unit = models.ForeignKey('units.Unit', on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='vehicles')
    status = models.CharField(
        max_length=20,
        choices=[
            ('Operational', 'Operational'),
            ('Maintenance', 'Maintenance'),
            ('Damaged', 'Damaged'),
            ('Destroyed', 'Destroyed'),
            ('Reserve', 'Reserve')
        ],
        default='Operational'
    )
    crew_size = models.IntegerField(default=1)
    image_url = models.URLField(blank=True, null=True)
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )

    def __str__(self):
        return f"{self.name} ({self.serial_number})"