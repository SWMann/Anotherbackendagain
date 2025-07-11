# backend/apps/users/models.py

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
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, discord_id, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

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
    commission_stage = models.ForeignKey('onboarding.CommissionStage', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='user_commissioning')
    onboarding_status = models.CharField(
        max_length=50,
        choices=[
            ('Applied', 'Applied'),
            ('Awaiting Interview', 'Awaiting Interview'),
            ('Accepted BIT Awaiting', 'Accepted BIT Awaiting'),
            ('Awaiting Review', 'Awaiting Review'),
            ('BIT Completed', 'BIT Completed'),
            ('Unit Inducted', 'Unit Inducted'),
            ('Active', 'Active'),
        ],
        default='Applied',
        blank=True,
        null=True

    )
    recruit_status = models.BooleanField(default=True)
    training_completion_date = models.DateTimeField(blank=True, null=True)
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

    # Add these fields to the User model
    primary_mos = models.ForeignKey(
        'units.MOS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_holders',
        help_text="User's primary MOS"
    )
    secondary_mos = models.ManyToManyField(
        'units.MOS',
        blank=True,
        related_name='secondary_holders',
        help_text="Additional MOS qualifications"
    )
    mos_skill_level = models.IntegerField(
        default=10,
        choices=[
            (10, 'Skill Level 10 - Entry'),
            (20, 'Skill Level 20 - Journeyman'),
            (30, 'Skill Level 30 - Senior'),
            (40, 'Skill Level 40 - Master')
        ]
    )
    mos_qualified_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date user qualified for primary MOS"
    )

    def __str__(self):
        return self.username

    # Remove the is_superuser property - let PermissionsMixin handle it
    # The PermissionsMixin already provides is_superuser as a BooleanField

    def save(self, *args, **kwargs):
        # Sync is_superuser with is_admin if needed
        if self.is_admin and not self.is_superuser:
            self.is_superuser = True
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        # Admin users have all permissions
        if self.is_admin:
            return True
        # Otherwise, check specific permissions
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        # Admin users have access to all apps
        if self.is_admin:
            return True
        # Otherwise, check specific module permissions
        return super().has_module_perms(app_label)