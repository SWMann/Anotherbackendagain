from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StandardGroupViewSet, StandardSubGroupViewSet, StandardViewSet

router_groups = DefaultRouter()
router_groups.register(r'groups', StandardGroupViewSet)

router_subgroups = DefaultRouter()
router_subgroups.register(r'subgroups', StandardSubGroupViewSet)

router_standards = DefaultRouter()
router_standards.register(r'standards', StandardViewSet)

urlpatterns = [
    path('', include(router_groups.urls)),
    path('', include(router_subgroups.urls)),
    path('', include(router_standards.urls)),
    path('standards/search/', StandardViewSet.as_view({'get': 'search'}), name='standards-search'),
    path('standards/recent/', StandardViewSet.as_view({'get': 'recent'}), name='standards-recent'),
]