from django.contrib import admin 
from django.urls import path, include 
from django.conf import settings 
from django.conf.urls.static import static 
from rest_framework_simplejwt.views import TokenRefreshView 
 
urlpatterns = [ 
    path('admin/', admin.site.urls), 
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('api/auth/', include('apps.users.urls')), 
    path('api/users/', include('apps.users.urls_users')), 
    path('api/units/', include('apps.units.urls')),
    path('api/units/hierarchy/', include('apps.units.urls_hierarchy')),
    path('api/events/', include('apps.events.urls')), 
    path('api/opords/', include('apps.operations.urls')), 
    path('api/certificates/', include('apps.training.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    path('api/ships/', include('apps.ships.urls')),
    path('api/forums/', include('apps.forums.urls')),
    path('api/training/', include('apps.training.urls')),
    path('api/onboarding/', include('apps.onboarding.urls')),
    path('api/sops/', include('apps.standards.urls')), 
    path('api/applications/', include('apps.onboarding.urls')), 
    path('api/ranks/', include('apps.units.urls_ranks')), 
    path('api/branches/', include('apps.units.urls_branches')),
    path('api/vehicles/', include('apps.vehicles.urls')),
    path('api/positions/', include('apps.units.urls_positions')),
]
 
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
