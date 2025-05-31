# backend/apps/units/views_hierarchy.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import UnitHierarchyView, UnitHierarchyNode, Unit
from .serializers import (
    UnitHierarchyViewSerializer, UnitHierarchyNodeSerializer,
    UnitNodeSerializer, HierarchyDataSerializer
)
from apps.users.views import IsAdminOrReadOnly


class UnitHierarchyViewViewSet(viewsets.ModelViewSet):
    queryset = UnitHierarchyView.objects.all()
    serializer_class = UnitHierarchyViewSerializer


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get complete hierarchy data for a view"""
        hierarchy_view = self.get_object()

        # Get units based on view configuration
        if hierarchy_view.included_units.exists():
            units = hierarchy_view.included_units.filter(is_active=True)
        else:
            units = Unit.objects.filter(is_active=True)

        # Apply filters from view configuration
        if hierarchy_view.filter_config:
            if 'branch_ids' in hierarchy_view.filter_config:
                units = units.filter(branch_id__in=hierarchy_view.filter_config['branch_ids'])
            if 'unit_types' in hierarchy_view.filter_config:
                units = units.filter(unit_type__in=hierarchy_view.filter_config['unit_types'])

        # Build nodes and edges
        nodes = []
        edges = []
        node_positions = {}

        # Get custom node data
        custom_nodes = UnitHierarchyNode.objects.filter(
            hierarchy_view=hierarchy_view
        ).select_related('unit')

        custom_node_map = {cn.unit_id: cn for cn in custom_nodes}

        for unit in units:
            # Use custom position if available
            if unit.id in custom_node_map:
                custom_node = custom_node_map[unit.id]
                node_positions[str(unit.id)] = {
                    'x': custom_node.position_x,
                    'y': custom_node.position_y
                }

            nodes.append(unit)

            # Create edges for parent-child relationships
            if unit.parent_unit and unit.parent_unit in units:
                edges.append({
                    'id': f'e{unit.parent_unit.id}-{unit.id}',
                    'source': str(unit.parent_unit.id),
                    'target': str(unit.id),
                    'type': 'smoothstep',
                    'animated': False
                })

        # Serialize the data
        nodes_data = UnitNodeSerializer(nodes, many=True).data

        return Response({
            'view': UnitHierarchyViewSerializer(hierarchy_view).data,
            'nodes': nodes_data,
            'edges': edges,
            'node_positions': node_positions
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def save_positions(self, request, pk=None):
        """Save node positions for a hierarchy view"""
        hierarchy_view = self.get_object()
        positions = request.data.get('positions', {})

        for unit_id, position in positions.items():
            unit = get_object_or_404(Unit, id=unit_id)

            UnitHierarchyNode.objects.update_or_create(
                hierarchy_view=hierarchy_view,
                unit=unit,
                defaults={
                    'position_x': position.get('x', 0),
                    'position_y': position.get('y', 0)
                }
            )

        return Response({'status': 'positions saved'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_layout(self, request, pk=None):
        """Update layout configuration"""
        hierarchy_view = self.get_object()
        hierarchy_view.layout_config = request.data.get('layout_config', {})
        hierarchy_view.save()

        return Response({'status': 'layout updated'})

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get the default hierarchy view"""
        default_view = UnitHierarchyView.objects.filter(is_default=True).first()

        if not default_view:
            # Create a default view if none exists
            default_view = UnitHierarchyView.objects.create(
                name='Full Organization Structure',
                description='Complete organizational hierarchy',
                view_type='full',
                is_default=True,
                is_public=True
            )

        return Response(UnitHierarchyViewSerializer(default_view).data)