from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_mos import MOSViewSet

router = DefaultRouter()
router.register(r'', MOSViewSet, basename='mos')

urlpatterns = [
    path('', include(router.urls)),
]