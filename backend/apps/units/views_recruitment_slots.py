# backend/apps/units/views_recruitment_slots.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, Q
from .models import RecruitmentSlot, Unit
from .serializers import (
    RecruitmentSlotSerializer,
    RecruitmentSlotCreateUpdateSerializer,
    UnitRecruitmentStatusSerializer
)
from apps.users.views import IsAdminOrReadOnly


class RecruitmentSlotViewSet(viewsets.ModelViewSet):
    """ViewSet for managing recruitment slots"""
    queryset = RecruitmentSlot.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['unit', 'role', 'career_track', 'is_active']
    search_fields = ['unit__name', 'role__name', 'notes']
    ordering = ['unit__name', 'role__name', 'career_track']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecruitmentSlotCreateUpdateSerializer
        return RecruitmentSlotSerializer

    @action(detail=False, methods=['get'])
    def by_unit(self, request):
        """Get all recruitment slots for a specific unit"""
        unit_id = request.query_params.get('unit_id')
        if not unit_id:
            return Response(
                {'error': 'unit_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = self.queryset.filter(unit_id=unit_id).select_related(
            'unit', 'role'
        ).order_by('career_track', 'role__name')

        serializer = self.get_serializer(slots, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def bulk_create(self, request):
        """Create multiple recruitment slots at once"""
        slots_data = request.data.get('slots', [])
        created_slots = []
        errors = []

        for idx, slot_data in enumerate(slots_data):
            serializer = RecruitmentSlotCreateUpdateSerializer(data=slot_data)
            if serializer.is_valid():
                slot = serializer.save()
                created_slots.append(RecruitmentSlotSerializer(slot).data)
            else:
                errors.append({
                    'index': idx,
                    'data': slot_data,
                    'errors': serializer.errors
                })

        return Response({
            'created': created_slots,
            'errors': errors,
            'summary': {
                'total': len(slots_data),
                'created': len(created_slots),
                'failed': len(errors)
            }
        }, status=status.HTTP_201_CREATED if created_slots else status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reserve_slots(self, request, pk=None):
        """Reserve slots for incoming personnel"""
        slot = self.get_object()
        count = request.data.get('count', 0)

        if count <= 0:
            return Response(
                {'error': 'Count must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if count > slot.available_slots:
            return Response(
                {'error': f'Cannot reserve {count} slots. Only {slot.available_slots} available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slot.reserved_slots += count
        slot.save()

        return Response(RecruitmentSlotSerializer(slot).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def fill_slots(self, request, pk=None):
        """Mark slots as filled"""
        slot = self.get_object()
        count = request.data.get('count', 0)
        from_reserved = request.data.get('from_reserved', False)

        if count <= 0:
            return Response(
                {'error': 'Count must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if from_reserved:
            if count > slot.reserved_slots:
                return Response(
                    {'error': f'Cannot fill {count} slots from reserved. Only {slot.reserved_slots} reserved'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            slot.reserved_slots -= count
        elif count > slot.available_slots:
            return Response(
                {'error': f'Cannot fill {count} slots. Only {slot.available_slots} available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slot.filled_slots += count
        slot.save()

        return Response(RecruitmentSlotSerializer(slot).data)


class UnitRecruitmentViewSet(viewsets.ViewSet):
    """ViewSet for unit recruitment management"""
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get recruitment status for all units or specific unit"""
        unit_id = request.query_params.get('unit_id')

        if unit_id:
            unit = get_object_or_404(Unit, id=unit_id)
            serializer = UnitRecruitmentStatusSerializer(unit)
            return Response(serializer.data)

        # Get all units with recruitment data
        units = Unit.objects.filter(is_active=True).prefetch_related(
            'recruitment_slots',
            'recruitment_slots__role'
        ).annotate(
            total_slots_count=Sum('recruitment_slots__total_slots',
                                  filter=Q(recruitment_slots__is_active=True)),
            filled_slots_count=Sum('recruitment_slots__filled_slots',
                                   filter=Q(recruitment_slots__is_active=True))
        ).order_by('name')

        serializer = UnitRecruitmentStatusSerializer(units, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        """Update unit recruitment status"""
        unit = get_object_or_404(Unit, pk=pk)

        # Update recruitment fields
        recruitment_status = request.data.get('recruitment_status')
        if recruitment_status:
            unit.recruitment_status = recruitment_status

        max_personnel = request.data.get('max_personnel')
        if max_personnel is not None:
            unit.max_personnel = max_personnel

        target_personnel = request.data.get('target_personnel')
        if target_personnel is not None:
            unit.target_personnel = target_personnel

        recruitment_notes = request.data.get('recruitment_notes')
        if recruitment_notes is not None:
            unit.recruitment_notes = recruitment_notes

        unit.save()

        serializer = UnitRecruitmentStatusSerializer(unit)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def initialize_slots(self, request, pk=None):
        """Initialize recruitment slots based on unit positions"""
        unit = get_object_or_404(Unit, pk=pk)

        # Get all active positions for this unit
        positions = unit.positions.filter(is_active=True).select_related('role')

        created_slots = []
        for position in positions:
            if not position.role:
                continue

            # Determine career track based on role
            career_track = 'enlisted'  # default
            if position.role.typical_rank:
                if position.role.typical_rank.is_officer:
                    career_track = 'officer'
                elif position.role.typical_rank.is_warrant:
                    career_track = 'warrant'

            # Check if slot already exists
            slot, created = RecruitmentSlot.objects.get_or_create(
                unit=unit,
                role=position.role,
                career_track=career_track,
                defaults={
                    'total_slots': 1,
                    'filled_slots': 0 if position.is_vacant else 1,
                    'reserved_slots': 0,
                    'is_active': True
                }
            )

            if created:
                created_slots.append(RecruitmentSlotSerializer(slot).data)

        return Response({
            'message': f'Initialized {len(created_slots)} recruitment slots',
            'created_slots': created_slots
        })