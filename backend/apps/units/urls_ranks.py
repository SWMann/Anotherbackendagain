from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RankViewSet

router = DefaultRouter()
router.register(r'', RankViewSet)

urlpatterns = [
    path('', include(router.urls)),
]