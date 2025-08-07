# backend/apps/onboarding/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet

router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='application')

urlpatterns = [
    # Application flow endpoints
    path('applications/recruitment-data/', ApplicationViewSet.as_view({'get': 'recruitment_data'}),
         name='recruitment-data'),
    path('applications/current/', ApplicationViewSet.as_view({'get': 'current'}), name='current-application'),
    path('applications/check-status/', ApplicationViewSet.as_view({'get': 'check_status'}),
         name='check-application-status'),
    path('applications/get-units/', ApplicationViewSet.as_view({'get': 'get_units'}), name='get-units'),
    path('applications/get-mos-options/', ApplicationViewSet.as_view({'get': 'get_mos_options'}),
         name='get-mos-options'),

    # Application actions
    path('applications/<uuid:pk>/save-progress/', ApplicationViewSet.as_view({'post': 'save_progress'}),
         name='save-application-progress'),
    path('applications/<uuid:pk>/accept-waiver/', ApplicationViewSet.as_view({'post': 'accept_waiver'}),
         name='accept-waiver'),
    path('applications/<uuid:pk>/submit/', ApplicationViewSet.as_view({'post': 'submit'}), name='submit-application'),

    # Admin actions
    path('applications/<uuid:pk>/add-comment/', ApplicationViewSet.as_view({'post': 'add_comment'}),
         name='add-application-comment'),
    path('applications/<uuid:pk>/schedule-interview/', ApplicationViewSet.as_view({'post': 'schedule_interview'}),
         name='schedule-interview'),
    path('applications/<uuid:pk>/approve/', ApplicationViewSet.as_view({'post': 'approve'}),
         name='approve-application'),
    path('applications/<uuid:pk>/reject/', ApplicationViewSet.as_view({'post': 'reject'}), name='reject-application'),

    # Include router URLs
    path('', include(router.urls)),
]