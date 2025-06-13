# backend/apps/units/views_roles.py
"""
Views for Role management
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import Role, Position, UserPosition
from .serializers import (
    RoleListSerializer, RoleDetailSerializer,
    PositionListSerializer, UserPositionSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role management"""
    queryset = Role.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = [
        'category', 'is_command_role', 'is_staff_role',
        'is_nco_role', 'is_specialist_role', 'is_active'
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category', 'sort_order']
    ordering = ['category', 'sort_order', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        return RoleDetailSerializer

    @action(detail=True, methods=['get'])
    def positions(self, request, pk=None):
        """Get all positions of this role"""
        role = self.get_object()
        positions = role.positions.filter(is_active=True).select_related(
            'unit', 'unit__branch'
        )

        # Apply filters
        unit_id = request.query_params.get('unit')
        if unit_id:
            positions = positions.filter(unit_id=unit_id)

        is_vacant = request.query_params.get('is_vacant')
        if is_vacant is not None:
            positions = positions.filter(is_vacant=is_vacant.lower() == 'true')

        serializer = PositionListSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def eligible_users(self, request, pk=None):
        """Get users who meet the requirements for this role"""
        role = self.get_object()

        # Start with all active users
        users = User.objects.filter(is_active=True)

        # Filter by rank requirements
        if role.min_rank:
            users = users.filter(
                current_rank__tier__gte=role.min_rank.tier,
                current_rank__branch=role.min_rank.branch
            )

        if role.max_rank:
            users = users.filter(
                current_rank__tier__lte=role.max_rank.tier,
                current_rank__branch=role.max_rank.branch
            )

        # Filter by time in service
        if role.min_time_in_service > 0:
            from datetime import timedelta
            from django.utils import timezone
            min_join_date = timezone.now() - timedelta(days=role.min_time_in_service)
            users = users.filter(join_date__lte=min_join_date)

        # Filter by branch if restricted
        if role.allowed_branches.exists():
            users = users.filter(branch__in=role.allowed_branches.all())

        # Exclude users already in this role (active assignments)
        assigned_user_ids = UserPosition.objects.filter(
            position__role=role,
            status='active'
        ).values_list('user_id', flat=True)
        users = users.exclude(id__in=assigned_user_ids)

        # Serialize the results
        from apps.users.serializers import UserSerializer
        serializer = UserSerializer(users, many=True)

        return Response({
            'count': users.count(),
            'eligible_users': serializer.data
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this role"""
        role = self.get_object()

        total_positions = role.positions.filter(is_active=True).count()
        filled_positions = role.positions.filter(
            is_active=True,
            is_vacant=False
        ).count()

        # Get distribution by unit type
        unit_distribution = role.positions.filter(is_active=True).values(
            'unit__unit_type'
        ).annotate(count=Count('id')).order_by('-count')

        # Get current holders by rank
        rank_distribution = UserPosition.objects.filter(
            position__role=role,
            status='active',
            assignment_type='primary'
        ).values(
            'user__current_rank__abbreviation',
            'user__current_rank__name'
        ).annotate(count=Count('id')).order_by('-count')

        return Response({
            'total_positions': total_positions,
            'filled_positions': filled_positions,
            'vacant_positions': total_positions - filled_positions,
            'fill_rate': round((filled_positions / total_positions * 100) if total_positions > 0 else 0, 1),
            'unit_distribution': unit_distribution,
            'rank_distribution': rank_distribution
        })
