# backend/apps/units/urls_promotion.py
"""
URLs for promotion requirements system
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_promotion import (
    PromotionRequirementTypeViewSet,
    RankPromotionRequirementViewSet,
    UserPromotionProgressView,
    PromotionChecklistView,
    PromoteUserView,
    RankHistoryViewSet,
    PromotionWaiverViewSet
)

router = DefaultRouter()
router.register(r'requirement-types', PromotionRequirementTypeViewSet)
router.register(r'rank-requirements', RankPromotionRequirementViewSet)
router.register(r'rank-history', RankHistoryViewSet)
router.register(r'waivers', PromotionWaiverViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # User promotion progress
    path('progress/', UserPromotionProgressView.as_view(), name='promotion-progress'),
    path('progress/<uuid:user_id>/', UserPromotionProgressView.as_view(), name='user-promotion-progress'),

    # Simplified checklist for career progression page
    path('checklist/', PromotionChecklistView.as_view(), name='promotion-checklist'),

    # Promote user
    path('promote/', PromoteUserView.as_view(), name='promote-user'),
]

# Add this to backend/config/urls.py:
# path('api/promotions/', include('apps.units.urls_promotion')),