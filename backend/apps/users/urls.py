from django.urls import path 
from rest_framework_simplejwt.views import TokenRefreshView 
from .views import DiscordTokenObtainPairView, LogoutView 
from .auth import discord_auth 
 
urlpatterns = [ 
    path('discord/', discord_auth, name='discord_auth'), 
    path('token/', DiscordTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('logout/', LogoutView.as_view(), name='auth_logout'), 
] 
