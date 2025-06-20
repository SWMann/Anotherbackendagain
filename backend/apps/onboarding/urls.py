from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommissionStageViewSet, ApplicationViewSet, UserOnboardingProgressViewSet,
    BranchApplicationViewSet, MentorAssignmentViewSet, UserOnboardingActionViewSet
)
from ..units.views_recruitment import RecruitmentStatusViewSet

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
    path('recruitment/brigades/', RecruitmentStatusViewSet.as_view({'get': 'brigades'})),
    path('recruitment/brigades/<uuid:pk>/platoons/', RecruitmentStatusViewSet.as_view({'get': 'platoons'})),
    path('recruitment/check-eligibility/', ApplicationViewSet.as_view({'post': 'check_eligibility'})),

]