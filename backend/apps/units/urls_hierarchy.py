# Add this to backend/config/urls.py after the other unit-related paths:
# path('api/units/hierarchy/', include('apps.units.urls_hierarchy')),
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_hierarchy import UnitHierarchyViewViewSet

router = DefaultRouter()
router.register(r'', UnitHierarchyViewViewSet, basename='hierarchy-view')

urlpatterns = [
    path('', include(router.urls)),
    path('default/', UnitHierarchyViewViewSet.as_view({'get': 'default'}), name='hierarchy-default'),
]