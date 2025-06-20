# Create new file: backend/apps/units/urls_position_templates.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_position_templates import PositionTemplateViewSet

router = DefaultRouter()
router.register(r'', PositionTemplateViewSet, basename='position-template')

urlpatterns = [
    path('', include(router.urls)),
]

# Add this to backend/config/urls.py after the other unit paths:
# path('api/units/position-templates/', include('apps.units.urls_position_templates')),