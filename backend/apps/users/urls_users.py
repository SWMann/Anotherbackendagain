# Add these to backend/apps/users/urls_users.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserDetailView, UserSensitiveFieldsView
from .views_profile import UserProfileDetailView, UserRankProgressionView, UserUnitHistoryView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('me/', UserViewSet.as_view({'get': 'me', 'patch': 'update_me'}), name='user-me'),
    path('profile/<uuid:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profile/me/', UserProfileDetailView.as_view(), name='user-profile-me'),
    path('<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<uuid:pk>/sensitive-fields/', UserSensitiveFieldsView.as_view(), name='user-sensitive-fields'),
    path('<uuid:pk>/rank-progression/', UserRankProgressionView.as_view(), name='user-rank-progression'),
    path('<uuid:pk>/unit-history/', UserUnitHistoryView.as_view(), name='user-unit-history'),
]