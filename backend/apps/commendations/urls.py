# backend/apps/commendations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommendationTypeViewSet, CommendationViewSet, CommendationDeviceViewSet

router = DefaultRouter()
router.register(r'types', CommendationTypeViewSet, basename='commendation-types')
router.register(r'awards', CommendationViewSet, basename='commendations')
router.register(r'devices', CommendationDeviceViewSet, basename='commendation-devices')

urlpatterns = [
    path('', include(router.urls)),
]