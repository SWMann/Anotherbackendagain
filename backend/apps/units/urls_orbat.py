from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_orbat import ORBATViewSet

router = DefaultRouter()
router.register(r'', ORBATViewSet, basename='orbat')

urlpatterns = [
    path('', include(router.urls)),
]