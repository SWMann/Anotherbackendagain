from django.db import models
from apps.core.models import BaseModel


class OperationOrder(BaseModel):
    operation_name = models.CharField(max_length=200)

    situation = models.TextField(blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    execution = models.TextField(blank=True, null=True)
    service_support = models.TextField(blank=True, null=True)
    command_signal = models.TextField(blank=True, null=True)
    attachments = models.JSONField(blank=True, null=True)
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='created_opords')
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_opords')
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('Draft', 'Draft'),
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Draft'
    )
    classification = models.CharField(
        max_length=20,
        choices=[
            ('Unclassified', 'Unclassified'),
            ('Confidential', 'Confidential'),
            ('Secret', 'Secret'),
            ('Top Secret', 'Top Secret')
        ],
        default='Unclassified'
    )
    version = models.IntegerField(default=1)

    def __str__(self):
        return self.operation_name