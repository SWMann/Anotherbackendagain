from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from .models import TrainingCertificate, UserCertificate
from .serializers import (
    TrainingCertificateSerializer, UserCertificateSerializer,
    IssueCertificateSerializer, RevokeCertificateSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


class TrainingCertificateViewSet(viewsets.ModelViewSet):
    queryset = TrainingCertificate.objects.all()
    serializer_class = TrainingCertificateSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'is_required_for_promotion', 'min_rank_requirement']
    search_fields = ['name', 'abbreviation', 'description', 'requirements']
    ordering_fields = ['name', 'branch']
    ordering = ['branch', 'name']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def issue(self, request, pk=None):
        """Issue a certificate to a user."""
        certificate = self.get_object()

        # Check if user has permission to issue certificates
        is_trainer = request.user.is_admin
        if not is_trainer and certificate.authorized_trainers:
            # Check if user holds any of the authorized positions
            user_positions = request.user.userposition_set.values_list('position_id', flat=True)
            authorized_positions = certificate.authorized_trainers
            is_trainer = any(str(pos) in authorized_positions for pos in user_positions)

        if not is_trainer:
            return Response(
                {"detail": "You do not have permission to issue this certificate."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = IssueCertificateSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            training_event_id = serializer.validated_data.get('training_event_id')
            certificate_file_url = serializer.validated_data.get('certificate_file_url', '')
            expiry_days = serializer.validated_data.get('expiry_days')

            user = get_object_or_404(User, id=user_id)

            # Calculate expiry date if applicable
            expiry_date = None
            if expiry_days is not None:
                expiry_date = timezone.now() + timedelta(days=expiry_days)
            elif certificate.expiration_period:
                expiry_date = timezone.now() + timedelta(days=certificate.expiration_period)

            # Create the user certificate
            user_cert = UserCertificate.objects.create(
                user=user,
                certificate=certificate,
                issuer=request.user,
                expiry_date=expiry_date,
                training_event_id=training_event_id,
                certificate_file_url=certificate_file_url
            )

            return Response(UserCertificateSerializer(user_cert).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def revoke(self, request, pk=None):
        """Revoke a user's certificate."""
        certificate = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has permission to revoke certificates
        if not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to revoke certificates."},
                status=status.HTTP_403_FORBIDDEN
            )

        user_cert = get_object_or_404(
            UserCertificate,
            user_id=user_id,
            certificate=certificate,
            is_active=True
        )

        serializer = RevokeCertificateSerializer(data=request.data)
        if serializer.is_valid():
            revocation_reason = serializer.validated_data['revocation_reason']

            user_cert.is_active = False
            user_cert.revocation_reason = revocation_reason
            user_cert.revoked_by = request.user
            user_cert.revocation_date = timezone.now()
            user_cert.save()

            return Response(UserCertificateSerializer(user_cert).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)