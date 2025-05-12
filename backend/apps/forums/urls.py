from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForumCategoryViewSet, ForumThreadViewSet, ForumPostViewSet

router = DefaultRouter()
router.register(r'categories', ForumCategoryViewSet)
router.register(r'threads', ForumThreadViewSet)
router.register(r'posts', ForumPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
]