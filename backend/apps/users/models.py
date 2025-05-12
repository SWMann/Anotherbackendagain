


import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from apps.core.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, discord_id, username, email=None, password=None, **extra_fields):
        if not discord_id:
            raise ValueError('Users must have a discord ID')

        user = self.model(
            discord_id=discord_id,
            username=username,
            email=self.normalize_email(email) if email else None,
            **extra_fields
        )

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, discord_id, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        return self.create_user(discord_id, username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    discord_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    service_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    current_rank = models.ForeignKey('units.Rank', on_delete=models.SET_NULL, related_name='users', null=True,
                                     blank=True)
    primary_unit = models.ForeignKey('units.Unit', on_delete=models.SET_NULL, related_name='primary_members', null=True,
                                     blank=True)
    branch = models.ForeignKey('units.Branch', on_delete=models.SET_NULL, related_name='members', null=True, blank=True)
    background_image_url = models.URLField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    discord_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    commission_stage = models.ForeignKey('onboarding.CommissionStage', on_delete=models.SET_NULL, null=True, blank=True)
    onboarding_status = models.CharField(
        max_length=50,
        choices=[
            ('Applied', 'Applied'),
            ('BIT Completed', 'BIT Completed'),
            ('Branch Applied', 'Branch Applied'),
            ('Branch Inducted', 'Branch Inducted'),
            ('Unit Assigned', 'Unit Assigned'),
            ('Active', 'Active'),
        ],
        default='Applied',
        blank=True,
        null=True
    )
    recruit_status = models.BooleanField(default=True)
    training_completion_date = models.DateTimeField(blank=True, null=True)
    mentor = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='mentees', null=True, blank=True)
    application_date = models.DateTimeField(blank=True, null=True)
    bit_completion_date = models.DateTimeField(blank=True, null=True)
    branch_application_date = models.DateTimeField(blank=True, null=True)
    branch_induction_date = models.DateTimeField(blank=True, null=True)
    unit_assignment_date = models.DateTimeField(blank=True, null=True)
    officer_candidate = models.BooleanField(default=False)
    warrant_officer_candidate = models.BooleanField(default=False)

    USERNAME_FIELD = 'discord_id'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
