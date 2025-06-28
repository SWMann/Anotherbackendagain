import requests
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    TokenRefreshResponseSerializer,
    TokenVerifyResponseSerializer
)

User = get_user_model()


class DiscordOAuthURL(APIView):
    """
    Get Discord OAuth URL for frontend
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get Discord OAuth URL",
        responses={200: openapi.Response("Discord OAuth URL", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'auth_url': openapi.Schema(type=openapi.TYPE_STRING, description="Discord OAuth URL")
            }
        ))}
    )
    def get(self, request):
        client_id = settings.SOCIAL_AUTH_DISCORD_KEY
        redirect_uri = request.build_absolute_uri(reverse('discord_callback'))
        scope = '%20'.join(settings.SOCIAL_AUTH_DISCORD_SCOPE)

        discord_auth_url = (
            f"https://discord.com/api/oauth2/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={scope}"
        )

        return Response({'auth_url': discord_auth_url})


class DiscordOAuthCallback(APIView):
    """
    Handle Discord OAuth callback
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')

        # Handle error cases
        if error or not code:
            return redirect(f"{settings.FRONTEND_URL}/login?error=oauth_failed")

        # Exchange code for token
        client_id = settings.SOCIAL_AUTH_DISCORD_KEY
        client_secret = settings.SOCIAL_AUTH_DISCORD_SECRET

        # Build the correct redirect URI
        # This should match EXACTLY what you registered with Discord
        if hasattr(settings, 'FORCE_SCRIPT_NAME') and settings.FORCE_SCRIPT_NAME:
            redirect_uri = request.build_absolute_uri(
                f"{settings.FORCE_SCRIPT_NAME}/api/auth/discord/callback/"
            )
        else:
            redirect_uri = request.build_absolute_uri(reverse('discord_callback'))

        token_url = "https://discord.com/api/oauth2/token"
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(settings.SOCIAL_AUTH_DISCORD_SCOPE)
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Add debugging
        print(f"Token exchange data: {token_data}")

        try:
            token_response = requests.post(token_url, data=token_data, headers=headers)
            print(f"Token response status: {token_response.status_code}")
            print(f"Token response: {token_response.text}")

            token_response.raise_for_status()
            token_json = token_response.json()

            # Rest of your code...

        except requests.exceptions.RequestException as e:
            print(f"Discord OAuth error: {e}")
            return redirect(f"{settings.FRONTEND_URL}/login?error=discord_api_error")


class TokenObtainPairView(APIView):
    """
    Custom JWT token obtain pair view that returns user data
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: TokenRefreshResponseSerializer,
            401: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that returns user data
    """

    @swagger_auto_schema(
        responses={
            200: TokenRefreshResponseSerializer,
            401: "Invalid token"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        refresh_token = serializer.validated_data['refresh']

        # Parse the token to get the user ID
        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get('user_id')
            user = User.objects.get(id=user_id)

            # Add user data to response
            response_data = serializer.validated_data
            response_data['user'] = UserSerializer(user).data

            return Response(response_data, status=status.HTTP_200_OK)
        except (User.DoesNotExist, KeyError):
            return Response(
                {"detail": "Invalid token or user not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class TokenVerifyView(APIView):
    """
    Verify token and return user data
    """

    @swagger_auto_schema(
        responses={
            200: TokenVerifyResponseSerializer,
            401: "Invalid token"
        }
    )
    def get(self, request):
        user = request.user
        return Response({'user': UserSerializer(user).data})


class LogoutView(APIView):
    """
    Logout view
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token")
            },
            required=['refresh']
        ),
        responses={
            205: "Successfully logged out",
            400: "Invalid token"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """
    Get CSRF token for frontend
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})