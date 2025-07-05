# backend/apps/events/models.py
from django.db import models
from apps.core.models import BaseModel


class Event(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(
        max_length=50,
        choices=[
            # Combat Operations
            ('Fleet_Battle', 'Fleet Battle'),
            ('Fighter_Patrol', 'Fighter Patrol'),
            ('Ground_Assault', 'Ground Assault'),
            ('Station_Defense', 'Station Defense'),
            ('Boarding_Op', 'Boarding Operation'),
            ('Escort_Mission', 'Escort Mission'),

            # Economic Operations
            ('Mining_Op', 'Mining Operation'),
            ('Cargo_Run', 'Cargo Run'),
            ('Trade_Mission', 'Trade Mission'),
            ('Salvage_Op', 'Salvage Operation'),

            # Training & Exercises
            ('Flight_Training', 'Flight Training'),
            ('Combat_Training', 'Combat Training'),
            ('Fleet_Exercise', 'Fleet Exercise'),
            ('Certification', 'Certification Course'),

            # Other
            ('Exploration', 'Exploration Mission'),
            ('Diplomacy', 'Diplomatic Mission'),
            ('Meeting', 'Meeting'),
            ('Social', 'Social Event'),
            ('Ceremony', 'Ceremony'),
        ],
        default='Flight_Training'
    )

    # Location information
    star_system = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Star system where event takes place"
    )
    planet_moon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Planet or moon name"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Specific location (station, outpost, coordinates)"
    )
    rendezvous_point = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Meeting point for participants"
    )

    # Time information
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Organization
    host_unit = models.ForeignKey('units.Unit', on_delete=models.CASCADE, related_name='hosted_events')
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='created_events')

    # Event details
    image_url = models.URLField(blank=True, null=True)
    max_participants = models.IntegerField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=False)

    # Requirements
    required_units = models.JSONField(
        blank=True,
        null=True,
        help_text="List of required unit IDs"
    )
    required_ranks = models.JSONField(
        blank=True,
        null=True,
        help_text="List of minimum required ranks"
    )
    required_ships = models.JSONField(
        blank=True,
        null=True,
        help_text="Required ship types/classes"
    )
    required_certifications = models.ManyToManyField(
        'training.TrainingCertificate',
        blank=True,
        help_text="Required certifications to participate"
    )

    # Mission details
    threat_level = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low Threat'),
            ('Medium', 'Medium Threat'),
            ('High', 'High Threat'),
            ('Extreme', 'Extreme Threat'),
        ],
        default='Medium',
        blank=True,
        null=True
    )

    expected_opposition = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Expected enemy forces"
    )

    # Linked content
    operation_order = models.OneToOneField(
        'operations.OperationOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_linked'
    )
    briefing_url = models.URLField(blank=True, null=True)

    # Fleet composition
    fleet_composition = models.JSONField(
        blank=True,
        null=True,
        help_text="Required fleet composition"
    )

    # Status
    is_public = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Planning', 'Planning'),
            ('Scheduled', 'Scheduled'),
            ('Briefing', 'Briefing'),
            ('In_Progress', 'In Progress'),
            ('Debriefing', 'Debriefing'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled'),
            ('Postponed', 'Postponed')
        ],
        default='Planning'
    )

    # Results
    mission_success = models.BooleanField(null=True, blank=True)
    casualties = models.JSONField(
        blank=True,
        null=True,
        help_text="Casualty report"
    )

    # Economic tracking
    credits_earned = models.IntegerField(default=0, help_text="Total credits earned")
    resources_gathered = models.JSONField(
        blank=True,
        null=True,
        help_text="Resources mined/salvaged"
    )

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-start_time']


class EventAttendance(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='event_attendances')

    # Response status
    status = models.CharField(
        max_length=20,
        choices=[
            ('Attending', 'Attending'),
            ('Declined', 'Declined'),
            ('Maybe', 'Maybe'),
            ('Excused', 'Excused'),
            ('No_Response', 'No Response')
        ],
        default='No_Response'
    )

    # Assignment details
    assigned_ship = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Ship assigned for this event"
    )
    assigned_position = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Position on ship (pilot, gunner, etc.)"
    )
    assigned_role = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Tactical role in operation"
    )

    # Timing
    response_time = models.DateTimeField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    # Performance
    feedback = models.TextField(blank=True, null=True)
    performance_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="1-5 rating"
    )

    # Statistics
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    credits_earned = models.IntegerField(default=0)
    commendations_earned = models.JSONField(
        blank=True,
        null=True,
        help_text="Commendations earned during event"
    )

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

    class Meta:
        unique_together = ['event', 'user']