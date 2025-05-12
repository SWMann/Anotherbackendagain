from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserDetailView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('me/', UserViewSet.as_view({'get': 'me', 'patch': 'update_me'}), name='user-me'),
    path('<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
]
