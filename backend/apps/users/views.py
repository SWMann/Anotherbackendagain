from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, ProfileSerializer, DiscordTokenObtainPairSerializer, UserProfileSerializer, \
    UserSensitiveFieldsSerializer
from django.shortcuts import get_object_or_404

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit users
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsUserOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a profile or admins to edit it
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.id == request.user.id


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_me(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def certificates(self, request, pk=None):
        user = self.get_object()
        certificates = user.usercertificate_set.all()
        from apps.training.serializers import UserCertificateSerializer
        serializer = UserCertificateSerializer(certificates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def positions(self, request, pk=None):
        user = self.get_object()
        positions = user.position_assignments.all()  # CORRECT - uses the related_name
        from apps.units.serializers import UserPositionSerializer
        serializer = UserPositionSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def events(self, request, pk=None):
        user = self.get_object()
        events = user.eventattendance_set.all()
        from apps.events.serializers import EventAttendanceSerializer
        serializer = EventAttendanceSerializer(events, many=True)
        return Response(serializer.data)


class DiscordTokenObtainPairView(TokenObtainPairView):
    serializer_class = DiscordTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Just return success as JWT is stateless
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserDetailView(generics.RetrieveAPIView):
    """
    Get a user by ID
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserSensitiveFieldsView(generics.UpdateAPIView):
    """
    Update sensitive user fields (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSensitiveFieldsSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    http_method_names = ['put']  # Only allow PUT method

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return the full user object with updated fields
        return Response(UserSerializer(instance).data)