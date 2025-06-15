# backend/apps/units/views_orbat.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Unit, Position, UserPosition
from .serializers_orbat import (
    ORBATNodeSerializer, ORBATEdgeSerializer, ORBATDataSerializer
)


class ORBATViewSet(viewsets.ViewSet):
    """ViewSet for ORBAT (Organization) visualization data"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def unit_orbat(self, request):
        """Get ORBAT data for a specific unit and its sub-units"""
        unit_id = request.query_params.get('unit_id')
        include_subunits = request.query_params.get('include_subunits', 'true').lower() == 'true'

        if not unit_id:
            return Response({'error': 'unit_id parameter required'}, status=400)

        unit = get_object_or_404(Unit, id=unit_id)

        # Get all positions for this unit and optionally sub-units
        if include_subunits:
            units = [unit] + list(unit.subunits.filter(is_active=True))
            positions = Position.objects.filter(
                unit__in=units,
                is_active=True,
                show_in_orbat=True
            ).select_related(
                'role', 'unit', 'parent_position'
            ).prefetch_related(
                'assignments__user__current_rank'
            )
        else:
            positions = unit.positions.filter(
                is_active=True,
                show_in_orbat=True
            ).select_related(
                'role', 'parent_position'
            ).prefetch_related(
                'assignments__user__current_rank'
            )

        # Build nodes and edges
        nodes = []
        edges = []
        position_map = {pos.id: pos for pos in positions}

        for position in positions:
            # Create node data
            node_data = ORBATNodeSerializer(position).data
            nodes.append(node_data)

            # Create edges for reporting relationships
            if position.parent_position and position.parent_position.id in position_map:
                edge = {
                    'id': f'edge-{position.parent_position.id}-{position.id}',
                    'source': str(position.parent_position.id),
                    'target': str(position.id),
                    'type': 'smoothstep',
                    'animated': False,
                    'data': {
                        'relationship': 'reports_to',
                        'label': 'Reports to'
                    }
                }
                edges.append(edge)

            # Handle external reporting relationships
            if position.reports_to_external and position.reports_to_external.id in position_map:
                edge = {
                    'id': f'edge-ext-{position.reports_to_external.id}-{position.id}',
                    'source': str(position.reports_to_external.id),
                    'target': str(position.id),
                    'type': 'smoothstep',
                    'animated': True,
                    'style': {'strokeDasharray': '5 5'},
                    'data': {
                        'relationship': 'external_reports_to',
                        'label': 'Coordinates with'
                    }
                }
                edges.append(edge)

        return Response({
            'unit': {
                'id': unit.id,
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'unit_type': unit.unit_type
            },
            'nodes': nodes,
            'edges': edges,
            'statistics': {
                'total_positions': len(positions),
                'filled_positions': sum(1 for p in positions if not p.is_vacant),
                'units_included': len(units) if include_subunits else 1
            }
        })

    @action(detail=False, methods=['get'])
    def full_orbat(self, request):
        """Get complete ORBAT for entire organization"""
        # Get top-level units
        top_units = Unit.objects.filter(
            parent_unit=None,
            is_active=True
        )

        all_units = []
        for unit in top_units:
            all_units.extend(self._get_unit_tree(unit))

        # Get all positions
        positions = Position.objects.filter(
            unit__in=all_units,
            is_active=True,
            show_in_orbat=True
        ).select_related(
            'role', 'unit', 'parent_position'
        ).prefetch_related(
            'assignments__user__current_rank'
        )

        # Build the complete ORBAT
        nodes = []
        edges = []

        for position in positions:
            nodes.append(ORBATNodeSerializer(position).data)

            if position.parent_position:
                edges.append({
                    'id': f'edge-{position.parent_position.id}-{position.id}',
                    'source': str(position.parent_position.id),
                    'target': str(position.id),
                    'type': 'smoothstep',
                    'animated': False
                })

        return Response({
            'nodes': nodes,
            'edges': edges,
            'units': [{
                'id': u.id,
                'name': u.name,
                'parent_id': u.parent_unit.id if u.parent_unit else None
            } for u in all_units]
        })

    def _get_unit_tree(self, unit):
        """Recursively get unit and all sub-units"""
        units = [unit]
        for subunit in unit.subunits.filter(is_active=True):
            units.extend(self._get_unit_tree(subunit))
        return units

