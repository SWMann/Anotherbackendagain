from django.db import models
from apps.core.models import BaseModel


class Event(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('Operation', 'Operation'),
            ('Training', 'Training'),
            ('Ceremony', 'Ceremony'),
            ('Meeting', 'Meeting'),
            ('Social', 'Social'),
            ('Other', 'Other')
        ],
        default='Training'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    coordinates = models.CharField(max_length=100, blank=True, null=True, help_text="For in-game locations")
    host_unit = models.ForeignKey('units.Unit', on_delete=models.CASCADE, related_name='hosted_events')
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='created_events')
    image_url = models.URLField(blank=True, null=True)
    max_participants = models.IntegerField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=False)
    required_units = models.JSONField(blank=True, null=True)
    required_ranks = models.JSONField(blank=True, null=True)
    operation_order = models.OneToOneField('operations.OperationOrder', on_delete=models.SET_NULL, null=True,
                                           blank=True, related_name='event_linked')
    briefing_url = models.URLField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Scheduled', 'Scheduled'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled'),
            ('Postponed', 'Postponed')
        ],
        default='Scheduled'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_time']


class EventAttendance(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='event_attendances')
    status = models.CharField(
        max_length=20,
        choices=[
            ('Attending', 'Attending'),
            ('Declined', 'Declined'),
            ('Maybe', 'Maybe'),
            ('Excused', 'Excused'),
            ('No Response', 'No Response')
        ],
        default='No Response'
    )
    response_time = models.DateTimeField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    performance_rating = models.IntegerField(null=True, blank=True, help_text="1-5 rating")

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

    class Meta:
        unique_together = ['event', 'user']