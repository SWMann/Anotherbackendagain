from django.db import models
from apps.core.models import BaseModel


class TrainingCertificate(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    branch = models.ForeignKey('units.Branch', on_delete=models.CASCADE, related_name='certificates')
    badge_image_url = models.URLField(blank=True, null=True)
    is_required_for_promotion = models.BooleanField(default=False)
    min_rank_requirement = models.ForeignKey('units.Rank', on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='required_for_certificates')
    expiration_period = models.IntegerField(null=True, blank=True,
                                            help_text="Days until expiration, null for no expiration")
    authorized_trainers = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.branch.abbreviation} {self.name}"


class UserCertificate(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    certificate = models.ForeignKey(TrainingCertificate, on_delete=models.CASCADE)
    issuer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='issued_certificates')
    issue_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    training_event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True)
    certificate_file_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    revocation_reason = models.TextField(blank=True, null=True)
    revoked_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='revoked_certificates')
    revocation_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.certificate.name}"

    class Meta:
        unique_together = ['user', 'certificate', 'is_active']