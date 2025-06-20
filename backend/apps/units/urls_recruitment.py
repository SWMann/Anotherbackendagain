# backend/apps/units/urls_recruitment.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_recruitment_slots import RecruitmentSlotViewSet, UnitRecruitmentViewSet

router = DefaultRouter()
router.register(r'slots', RecruitmentSlotViewSet, basename='recruitment-slots')
router.register(r'units', UnitRecruitmentViewSet, basename='unit-recruitment')

urlpatterns = [
    path('', include(router.urls)),
]

# Add this to backend/config/urls.py after the other unit paths:
# path('api/units/recruitment/', include('apps.units.urls_recruitment')),