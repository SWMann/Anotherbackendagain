from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_roles import RoleViewSet

router = DefaultRouter()
router.register(r'', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
