# backend/apps/units/views_orbat.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q
from .models import Unit, Position, UserPosition
from .serializers_orbat import ORBATNodeSerializer, ORBATUnitSerializer


class ORBATViewSet(viewsets.ViewSet):
    """
    ViewSet for ORBAT (Organizational Battle & Administrative Timeline) visualization
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def unit_orbat(self, request):
        """
        Get ORBAT data for a specific unit
        Query params:
        - unit_id: UUID of the unit (required)
        - include_subunits: Include sub-units (default: true)
        """
        unit_id = request.query_params.get('unit_id')

        if not unit_id:
            return Response(
                {'error': 'unit_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the unit
        try:
            unit = Unit.objects.get(id=unit_id)
        except Unit.DoesNotExist:
            return Response(
                {'error': 'Unit not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        include_subunits = request.query_params.get('include_subunits', 'true').lower() == 'true'

        # Get all units to include
        units_to_include = [unit]
        if include_subunits:
            # Get all subunits recursively
            def get_subunits(parent_unit):
                subunits = list(Unit.objects.filter(parent_unit=parent_unit, is_active=True))
                all_subunits = []
                for subunit in subunits:
                    all_subunits.append(subunit)
                    all_subunits.extend(get_subunits(subunit))
                return all_subunits

            units_to_include.extend(get_subunits(unit))

        # Get all positions for these units
        positions = Position.objects.filter(
            unit__in=units_to_include,
            is_active=True,
            show_in_orbat=True
        ).select_related(
            'role',
            'unit',
            'parent_position'
        ).prefetch_related(
            Prefetch(
                'assignments',
                queryset=UserPosition.objects.filter(
                    status='active'
                ).select_related('user', 'user__current_rank')
            )
        ).order_by('unit__name', 'display_order', 'role__sort_order')

        # Build nodes
        nodes = []
        node_ids = set()

        for position in positions:
            node_data = ORBATNodeSerializer(position).data
            nodes.append(node_data)
            node_ids.add(str(position.id))

        # Build edges
        edges = []
        for position in positions:
            if position.parent_position and str(position.parent_position.id) in node_ids:
                edges.append({
                    'id': f'edge-{position.parent_position.id}-{position.id}',
                    'source': str(position.parent_position.id),
                    'target': str(position.id),
                    'type': 'smoothstep',
                    'animated': False
                })

        # Prepare response
        return Response({
            'unit': ORBATUnitSerializer(unit).data,
            'nodes': nodes,
            'edges': edges,
            'statistics': {
                'total_positions': len(nodes),
                'filled_positions': sum(1 for n in nodes if not n['is_vacant']),
                'vacant_positions': sum(1 for n in nodes if n['is_vacant']),
                'units_included': len(units_to_include)
            }
        })

    @action(detail=False, methods=['get'])
    def units_list(self, request):
        """Get list of all units for the dropdown"""
        units = Unit.objects.filter(is_active=True).order_by('name')
        return Response(ORBATUnitSerializer(units, many=True).data)