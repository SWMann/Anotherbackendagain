from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ship
from .serializers import (
    ShipListSerializer, ShipDetailSerializer, ShipCreateUpdateSerializer,
    ShipApprovalSerializer
)
from apps.users.views import IsAdminOrReadOnly


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a ship or admins to edit it
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.is_admin


class ShipViewSet(viewsets.ModelViewSet):
    queryset = Ship.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_type', 'manufacturer', 'owner', 'assigned_unit', 'approval_status', 'is_flagship']
    search_fields = ['name', 'designation', 'class_type', 'manufacturer', 'primary_role', 'description']
    ordering_fields = ['name', 'created_at', 'length', 'crew_capacity']
    ordering = ['name']
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return ShipListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ShipCreateUpdateSerializer
        return ShipDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve or reject a ship submission."""
        ship = self.get_object()

        # Only admins can approve ships
        if not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to approve ships."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ShipApprovalSerializer(data=request.data)
        if serializer.is_valid():
            approval_status = serializer.validated_data['approval_status']

            ship.approval_status = approval_status
            ship.approved_by = request.user
            ship.approval_date = timezone.now()
            ship.save()

            return Response({
                "id": ship.id,
                "name": ship.name,
                "approval_status": ship.approval_status,
                "approved_by": request.user.username
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def fleet(self, request):
        """Get fleet overview by unit and class type."""
        units = Ship.objects.filter(approval_status='Approved').values(
            'assigned_unit__name', 'assigned_unit__id', 'class_type'
        ).distinct()

        result = {}
        for unit_data in units:
            unit_name = unit_data['assigned_unit__name'] or 'Unassigned'
            unit_id = unit_data['assigned_unit__id']
            class_type = unit_data['class_type']

            if unit_name not in result:
                result[unit_name] = {
                    'unit_id': unit_id,
                    'classes': {}
                }

            ships = Ship.objects.filter(
                assigned_unit__id=unit_id if unit_id else None,
                class_type=class_type,
                approval_status='Approved'
            )

            result[unit_name]['classes'][class_type] = ShipListSerializer(ships, many=True).data

        return Response(result)