from django.urls import path, include 
from rest_framework.routers import DefaultRouter 
from .views import UserViewSet, UserProfileView 
 
router = DefaultRouter() 
router.register(r'', UserViewSet) 
 
urlpatterns = [ 
    path('', include(router.urls)), 
    path('me/', UserViewSet.as_view({'get': 'me', 'patch': 'update_me'}), name='user-me'), 
] 
