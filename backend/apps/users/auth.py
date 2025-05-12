import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def discord_auth(request):
    code = request.data.get('code')

    if not code:
        return Response({'error': 'No authorization code provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Exchange authorization code for an access token
    data = {
        'client_id': settings.SOCIAL_AUTH_DISCORD_KEY,
        'client_secret': settings.SOCIAL_AUTH_DISCORD_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.data.get('redirect_uri', 'http://localhost:3000/auth/callback'),
        'scope': 'identify email',
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)

    if response.status_code != 200:
        return Response({'error': 'Failed to retrieve access token from Discord'}, status=status.HTTP_400_BAD_REQUEST)

    tokens = response.json()
    access_token = tokens['access_token']

    # Get the user's Discord information
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get('https://discord.com/api/users/@me', headers=headers)

    if response.status_code != 200:
        return Response({'error': 'Failed to retrieve user info from Discord'}, status=status.HTTP_400_BAD_REQUEST)

    user_data = response.json()

    # Get or create the user
    try:
        user = User.objects.get(discord_id=user_data['id'])
        # Update user data
        user.username = user_data['username']
        if 'email' in user_data:
            user.email = user_data['email']
        if 'avatar' in user_data:
            user.avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
        user.save()
    except User.DoesNotExist:
        # Create a new user
        user = User.objects.create_user(
            discord_id=user_data['id'],
            username=user_data['username'],
            email=user_data.get('email', ''),
        )
        if 'avatar' in user_data:
            user.avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
            user.save()

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'discord_id': user.discord_id,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'is_admin': user.is_admin,
            'is_staff': user.is_staff,
        }
    })
