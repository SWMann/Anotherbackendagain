from datetime import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import MOS, Unit, Position
from .serializers_mos import (
    MOSListSerializer, MOSDetailSerializer, MOSCreateUpdateSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model
from apps.units.serializers import UnitListSerializer
from apps.units.serializers import PositionListSerializer
from apps.users.serializers import UserSerializer

User = get_user_model()


class MOSViewSet(viewsets.ModelViewSet):
    """ViewSet for Military Occupational Specialty management"""
    queryset = MOS.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = [
        'branch', 'category', 'is_active', 'is_entry_level',
        'security_clearance_required', 'physical_demand_rating'
    ]
    search_fields = ['code', 'title', 'description']
    ordering_fields = ['code', 'title', 'category']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'list':
            return MOSListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MOSCreateUpdateSerializer
        return MOSDetailSerializer

    @action(detail=False, methods=['get'])
    def entry_level(self, request):
        """Get all entry-level MOS available for new recruits"""
        mos_list = self.queryset.filter(
            is_active=True,
            is_entry_level=True
        ).select_related('branch')

        # Group by branch
        grouped = {}
        for mos in mos_list:
            branch_name = mos.branch.name
            if branch_name not in grouped:
                grouped[branch_name] = []
            grouped[branch_name].append(MOSListSerializer(mos).data)

        return Response(grouped)

    @action(detail=True, methods=['get'])
    def units(self, request, pk=None):
        """Get all units that authorize this MOS"""
        mos = self.get_object()
        units = mos.authorized_units.filter(is_active=True)

        # Filter by unit type if provided
        unit_type = request.query_params.get('unit_type')
        if unit_type:
            units = units.filter(unit_type=unit_type)

        serializer = UnitListSerializer(units, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def positions(self, request, pk=None):
        """Get all positions requiring this MOS"""
        mos = self.get_object()
        positions = Position.objects.filter(
            required_mos=mos,
            is_active=True
        ).select_related('unit', 'role')

        # Filter vacant positions
        is_vacant = request.query_params.get('is_vacant')
        if is_vacant is not None:
            positions = positions.filter(is_vacant=is_vacant.lower() == 'true')

        serializer = PositionListSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def holders(self, request, pk=None):
        """Get all users with this MOS"""
        mos = self.get_object()

        # Get primary and secondary holders
        primary_holders = User.objects.filter(
            primary_mos=mos,
            is_active=True
        ).select_related('current_rank', 'primary_unit')

        secondary_holders = User.objects.filter(
            secondary_mos=mos,
            is_active=True
        ).exclude(
            primary_mos=mos
        ).select_related('current_rank', 'primary_unit')


        return Response({
            'primary': UserSerializer(primary_holders, many=True).data,
            'secondary': UserSerializer(secondary_holders, many=True).data,
            'total_primary': primary_holders.count(),
            'total_secondary': secondary_holders.count()
        })

    @action(detail=True, methods=['get'])
    def training_pipeline(self, request, pk=None):
        """Get training pipeline information for this MOS"""
        mos = self.get_object()

        # Get users currently in training for this MOS
        in_training = User.objects.filter(
            primary_mos=mos,
            mos_skill_level=10,
            is_active=True,
            recruit_status=True
        ).count()

        # Get training units
        training_units = Unit.objects.filter(
            mos_training_capability=mos,
            is_active=True
        )

        return Response({
            'mos': MOSDetailSerializer(mos).data,
            'ait_weeks': mos.ait_weeks,
            'ait_location': mos.ait_location,
            'currently_in_training': in_training,
            'training_units': [
                {
                    'id': unit.id,
                    'name': unit.name,
                    'location': unit.location
                } for unit in training_units
            ],
            'required_certifications': [
                {
                    'id': cert.id,
                    'name': cert.name,
                    'abbreviation': cert.abbreviation
                } for cert in mos.required_certifications.all()
            ]
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign_to_user(self, request, pk=None):
        """Assign MOS to a user"""
        mos = self.get_object()
        user_id = request.data.get('user_id')
        assignment_type = request.data.get('assignment_type', 'primary')  # primary or secondary
        skill_level = request.data.get('skill_level', 10)

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)

        # Check if user meets requirements
        if mos.min_asvab_score > 0:
            # In real implementation, check user's ASVAB score
            pass

        if assignment_type == 'primary':
            user.primary_mos = mos
            user.mos_skill_level = skill_level
            user.mos_qualified_date = timezone.now().date()
            user.save()

            return Response({
                'message': f'Primary MOS {mos.code} assigned to {user.username}',
                'user_id': user.id,
                'mos': MOSDetailSerializer(mos).data
            })
        else:
            user.secondary_mos.add(mos)

            return Response({
                'message': f'Secondary MOS {mos.code} assigned to {user.username}',
                'user_id': user.id,
                'mos': MOSDetailSerializer(mos).data
            })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def remove_from_user(self, request, pk=None):
        """Remove MOS from a user"""
        mos = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)

        if user.primary_mos == mos:
            user.primary_mos = None
            user.mos_qualified_date = None
            user.save()
            message = f'Primary MOS {mos.code} removed from {user.username}'
        else:
            user.secondary_mos.remove(mos)
            message = f'Secondary MOS {mos.code} removed from {user.username}'

        return Response({'message': message})