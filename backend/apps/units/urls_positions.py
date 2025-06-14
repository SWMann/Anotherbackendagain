# backend/apps/units/urls_positions.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_positions import PositionViewSet  # Changed from .views to .views_positions

router = DefaultRouter()
router.register(r'', PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

router = DefaultRouter()
router.register(r'', PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]