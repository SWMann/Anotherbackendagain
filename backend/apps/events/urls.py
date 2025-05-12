from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet

router = DefaultRouter()
router.register(r'', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upcoming/', EventViewSet.as_view({'get': 'upcoming'}), name='upcoming-events'),
    path('calendar/', EventViewSet.as_view({'get': 'calendar'}), name='calendar-events'),
]