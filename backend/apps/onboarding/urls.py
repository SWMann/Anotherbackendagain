from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommissionStageViewSet, ApplicationViewSet, UserOnboardingProgressViewSet,
    BranchApplicationViewSet, MentorAssignmentViewSet, UserOnboardingActionViewSet
)

router = DefaultRouter()
router.register(r'commission-stages', CommissionStageViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'onboarding-progress', UserOnboardingProgressViewSet)
router.register(r'branch-applications', BranchApplicationViewSet)
router.register(r'mentor-assignments', MentorAssignmentViewSet)
router.register(r'actions', UserOnboardingActionViewSet, basename='onboarding-actions')

urlpatterns = [
    path('', include(router.urls)),
    path('status/<str:discord_id>/', ApplicationViewSet.as_view({'get': 'status'}), name='application-status'),
    path('branch-applications/templates/<uuid:branch_id>/', BranchApplicationViewSet.as_view({'get': 'templates'}), name='branch-application-templates'),
    path('my/onboarding-progress/', UserOnboardingProgressViewSet.as_view({'get': 'my'}), name='my-onboarding-progress'),
    path('my/branch-applications/', BranchApplicationViewSet.as_view({'get': 'my'}), name='my-branch-applications'),
    path('my/next-requirements/', UserOnboardingActionViewSet.as_view({'get': 'next_requirements'}), name='my-next-requirements'),
]