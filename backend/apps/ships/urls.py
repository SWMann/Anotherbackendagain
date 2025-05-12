from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipViewSet

router = DefaultRouter()
router.register(r'', ShipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('fleet/', ShipViewSet.as_view({'get': 'fleet'}), name='fleet-overview'),
]