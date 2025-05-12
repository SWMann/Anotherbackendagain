from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingCertificateViewSet

router = DefaultRouter()
router.register(r'', TrainingCertificateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]