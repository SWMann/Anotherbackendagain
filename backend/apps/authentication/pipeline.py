import requests
from django.utils import timezone
from django.conf import settings
from users.models import User


def create_user(backend, user=None, response=None, *args, **kwargs):
    """
    Create user if it doesn't exist.
    This function is part of the social auth pipeline.
    """
    if user:
        return {'is_new': False}

    if backend.name == 'discord':
        discord_id = response.get('id')
        email = response.get('email')
        username = response.get('username')

        if not email or not username:
            return None

        # Check if user exists with this discord_id
        user = User.objects.filter(discord_id=discord_id).first()

        if user:
            # User exists, update the email if it changed
            if user.email != email:
                user.email = email
                user.save()
            return {'is_new': False, 'user': user}

        # Check if user exists with this email
        user = User.objects.filter(email=email).first()

        if user:
            # User exists, update the discord_id if it wasn't set
            if not user.discord_id:
                user.discord_id = discord_id
                user.save()
            return {'is_new': False, 'user': user}

        # Create new user
        user = User.objects.create(
            discord_id=discord_id,
            email=email,
            username=username,
            is_active=True
        )

        return {'is_new': True, 'user': user}

    return None


def update_user_details(backend, user, response, *args, **kwargs):
    """
    Update user details from Discord response.
    This function is part of the social auth pipeline.
    """
    if backend.name == 'discord' and user:
        discord_id = response.get('id')
        email = response.get('email')
        username = response.get('username')
        discriminator = response.get('discriminator', '')
        avatar = response.get('avatar')

        # Update last login time
        user.last_login = timezone.now()

        # Update profile info if changed
        changed = False

        if user.username != username:
            user.username = username
            changed = True

        if user.email != email:
            user.email = email
            changed = True

        # Update Discord avatar if it exists
        if avatar:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png"
            if user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
                changed = True

        if changed:
            user.save()

        return {'user': user}