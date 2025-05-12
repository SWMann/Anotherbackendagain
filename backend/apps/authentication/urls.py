from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    DiscordOAuthURL,
    DiscordOAuthCallback,
    TokenObtainPairView,
    CustomTokenRefreshView,
    TokenVerifyView,
    LogoutView,
    get_csrf_token
)

urlpatterns = [
    # Discord OAuth
    path('discord/', DiscordOAuthURL.as_view(), name='discord_auth'),
    path('discord/callback/', DiscordOAuthCallback.as_view(), name='discord_callback'),

    # JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # CSRF
    path('csrf/', get_csrf_token, name='csrf_token'),
]