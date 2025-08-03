# backend/apps/commendations/models.py
from django.db import models
from apps.core.models import BaseModel
from django.core.validators import FileExtensionValidator


class CommendationType(BaseModel):
    """Types/categories of commendations"""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=[
        ('valor', 'Valor'),
        ('achievement', 'Achievement'),
        ('service', 'Service'),
        ('campaign', 'Campaign'),
        ('qualification', 'Qualification'),
        ('unit', 'Unit Citation'),
        ('special', 'Special Recognition')
    ])
    precedence = models.IntegerField(
        help_text="Order of precedence (lower numbers = higher precedence)"
    )

    # Visual elements
    ribbon_image = models.ImageField(
        upload_to='commendations/ribbons/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'svg'])],
        help_text='Ribbon bar image'
    )
    medal_image = models.ImageField(
        upload_to='commendations/medals/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'svg'])],
        help_text='Full medal image'
    )
    ribbon_image_url = models.URLField(blank=True, null=True)  # Fallback URL
    medal_image_url = models.URLField(blank=True, null=True)  # Fallback URL

    # Requirements
    eligibility_criteria = models.TextField(blank=True, null=True)
    min_rank_requirement = models.ForeignKey(
        'units.Rank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commendation_min_rank'
    )
    requires_nomination = models.BooleanField(default=True)
    auto_award_criteria = models.JSONField(
        default=dict,
        blank=True,
        help_text="Criteria for automatic awarding (e.g., time in service, operations count)"
    )

    # Restrictions
    is_active = models.BooleanField(default=True)
    multiple_awards_allowed = models.BooleanField(default=True)
    max_awards_per_user = models.IntegerField(default=0, help_text="0 = unlimited")

    # Branch restrictions
    allowed_branches = models.ManyToManyField(
        'units.Branch',
        blank=True,
        related_name='available_commendations'
    )

    class Meta:
        ordering = ['precedence', 'name']

    def __str__(self):
        return f"{self.abbreviation} - {self.name}"

    @property
    def ribbon_display_url(self):
        """Return the best available ribbon image URL"""
        if self.ribbon_image:
            return self.ribbon_image.url
        return self.ribbon_image_url

    @property
    def medal_display_url(self):
        """Return the best available medal image URL"""
        if self.medal_image:
            return self.medal_image.url
        return self.medal_image_url


class Commendation(BaseModel):
    """Individual commendation awarded to a user"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='commendations')
    commendation_type = models.ForeignKey(CommendationType, on_delete=models.CASCADE)

    # Award details
    awarded_date = models.DateTimeField()
    awarded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='commendations_awarded'
    )

    # Citation
    citation = models.TextField(
        help_text="Official citation text describing the reason for the award"
    )
    short_citation = models.CharField(
        max_length=500,
        help_text="Brief summary for display"
    )

    # Related information
    related_event = models.ForeignKey(
        'events.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Event/operation related to this commendation"
    )
    related_unit = models.ForeignKey(
        'units.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Unit the member was serving with"
    )

    # Administrative
    order_number = models.CharField(max_length=50, blank=True, null=True)
    is_public = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commendations_verified'
    )
    verified_date = models.DateTimeField(null=True, blank=True)

    # For multiple awards of same commendation
    award_number = models.IntegerField(
        default=1,
        help_text="Which number award this is (for multiple awards)"
    )

    # Attachments
    supporting_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="URLs to supporting documents"
    )

    class Meta:
        ordering = ['-awarded_date']
        unique_together = ['user', 'commendation_type', 'award_number']

    def __str__(self):
        return f"{self.user.username} - {self.commendation_type.abbreviation} ({self.award_number})"


class CommendationDevice(BaseModel):
    """Devices/clusters that can be added to commendations"""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    device_type = models.CharField(max_length=50, choices=[
        ('bronze_star', 'Bronze Star'),
        ('silver_star', 'Silver Star'),
        ('gold_star', 'Gold Star'),
        ('oak_leaf', 'Oak Leaf Cluster'),
        ('v_device', 'Valor Device'),
        ('numeric', 'Numeric Device')
    ])
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class CommendationDeviceAwarded(BaseModel):
    """Devices awarded with specific commendations"""
    commendation = models.ForeignKey(Commendation, on_delete=models.CASCADE, related_name='devices')
    device = models.ForeignKey(CommendationDevice, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ['commendation', 'device']