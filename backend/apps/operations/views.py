from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import OperationOrder
from .serializers import (
    OperationOrderListSerializer, OperationOrderDetailSerializer,
    OperationOrderCreateUpdateSerializer, OperationOrderApprovalSerializer
)
from apps.users.views import IsAdminOrReadOnly


class IsCreatorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an opord or admins to edit it
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user or request.user.is_admin


class OperationOrderViewSet(viewsets.ModelViewSet):
    queryset = OperationOrder.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'approval_status', 'classification', 'creator']
    search_fields = ['operation_name', 'situation', 'mission']
    ordering_fields = ['created_at', 'version']
    ordering = ['-created_at']
    permission_classes = [IsCreatorOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return OperationOrderListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OperationOrderCreateUpdateSerializer
        return OperationOrderDetailSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve or reject an operation order."""
        opord = self.get_object()

        # Only admins or commanders can approve operation orders
        if not (request.user.is_admin or request.user.userposition_set.filter(
                position__is_command_position=True,
                is_primary=True
        ).exists()):
            return Response(
                {"detail": "You do not have permission to approve operation orders."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OperationOrderApprovalSerializer(data=request.data)
        if serializer.is_valid():
            approval_status = serializer.validated_data['approval_status']

            opord.approval_status = approval_status
            opord.approved_by = request.user
            opord.save()

            return Response({
                "id": opord.id,
                "operation_name": opord.operation_name,
                "approval_status": opord.approval_status,
                "approved_by": request.user.username
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)