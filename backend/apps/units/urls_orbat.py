# backend/apps/units/urls_orbat.py
from django.urls import path
from .views_orbat import ORBATViewSet

# Create URL patterns without using routers for more control
urlpatterns = [
    path('unit_orbat/', ORBATViewSet.as_view({'get': 'unit_orbat'}), name='orbat-unit'),
    path('units_list/', ORBATViewSet.as_view({'get': 'units_list'}), name='orbat-units-list'),
]