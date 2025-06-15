# backend/apps/units/views_orbat.py
"""
Complete ORBAT implementation for Django backend
This provides the endpoints that the React ORBAT page expects
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q, Count
from .models import Unit, Position, UserPosition, Role
from .serializers_orbat import ORBATNodeSerializer, ORBATUnitSerializer


class ORBATViewSet(viewsets.ViewSet):
    """
    ViewSet for ORBAT (Order of Battle) visualization
    Provides the endpoints expected by the React ORBAT page
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def unit_orbat(self, request):
        """
        Get ORBAT data for a specific unit

        Expected URL: /api/units/orbat/unit_orbat/?unit_id={uuid}&include_subunits=true

        Query params:
        - unit_id: UUID of the unit (required)
        - include_subunits: Include sub-units in the hierarchy (default: true)

        Returns:
        {
            "unit": { unit details },
            "nodes": [ array of position nodes ],
            "edges": [ array of connections between positions ],
            "statistics": { summary statistics }
        }
        """
        unit_id = request.query_params.get('unit_id')

        if not unit_id:
            return Response(
                {'error': 'unit_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the unit
        try:
            unit = Unit.objects.select_related('branch').get(id=unit_id)
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
            def get_all_subunits(parent_unit):
                subunits = list(Unit.objects.filter(parent_unit=parent_unit, is_active=True))
                all_subunits = []
                for subunit in subunits:
                    all_subunits.append(subunit)
                    all_subunits.extend(get_all_subunits(subunit))
                return all_subunits

            units_to_include.extend(get_all_subunits(unit))

        # Get all positions for these units
        positions = Position.objects.filter(
            unit__in=units_to_include,
            is_active=True
        ).select_related(
            'role',
            'unit',
            'unit__branch',
            'parent_position'
        ).prefetch_related(
            Prefetch(
                'assignments',
                queryset=UserPosition.objects.filter(
                    status='active'
                ).select_related('user', 'user__current_rank'),
                to_attr='active_assignments'
            )
        ).order_by('unit__name', 'display_order', 'role__sort_order')

        # Build nodes
        nodes = []
        position_map = {}

        for position in positions:
            # Get the active primary assignment
            active_assignment = None
            for assignment in position.active_assignments:
                if assignment.assignment_type == 'primary':
                    active_assignment = assignment
                    break

            # Determine position type based on role
            position_type = 'standard'
            if position.role:
                if position.role.is_command_role:
                    position_type = 'command'
                elif position.role.is_staff_role:
                    position_type = 'staff'
                elif position.role.category == 'nco':
                    position_type = 'nco'
                elif position.role.category == 'specialist':
                    position_type = 'specialist'

            # Create node data
            node_data = {
                'id': str(position.id),
                'display_title': position.display_title,
                'unit_info': {
                    'id': str(position.unit.id),
                    'name': position.unit.name,
                    'abbreviation': position.unit.abbreviation,
                    'unit_type': position.unit.unit_type,
                    'branch_name': position.unit.branch.name if position.unit.branch else None
                },
                'role_info': {
                    'id': str(position.role.id),
                    'name': position.role.name,
                    'category': position.role.category,
                    'is_command_role': position.role.is_command_role,
                    'is_staff_role': position.role.is_staff_role
                } if position.role else None,
                'position_type': position_type,
                'is_vacant': position.is_vacant,
                'display_order': position.display_order,
                'current_holder': None
            }

            # Add current holder information if position is filled
            if active_assignment and active_assignment.user:
                user = active_assignment.user
                node_data['current_holder'] = {
                    'id': str(user.id),
                    'username': user.username,
                    'service_number': user.service_number,
                    'avatar_url': user.avatar_url,
                    'rank': {
                        'abbreviation': user.current_rank.abbreviation,
                        'name': user.current_rank.name,
                        'insignia_url': user.current_rank.insignia_image_url
                    } if user.current_rank else None
                }

            nodes.append(node_data)
            position_map[position.id] = node_data

        # Build edges based on parent-child relationships
        edges = []
        edge_id = 1

        for position in positions:
            if position.parent_position and position.parent_position.id in position_map:
                edges.append({
                    'id': f'edge-{edge_id}',
                    'source': str(position.parent_position.id),
                    'target': str(position.id),
                    'type': 'smoothstep',
                    'animated': False
                })
                edge_id += 1

        # Calculate statistics
        total_positions = len(nodes)
        filled_positions = sum(1 for n in nodes if not n['is_vacant'])
        vacant_positions = total_positions - filled_positions

        # Build response
        response_data = {
            'unit': {
                'id': str(unit.id),
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'unit_type': unit.unit_type,
                'branch_name': unit.branch.name if unit.branch else None,
                'emblem_url': unit.emblem_url,
                'motto': unit.motto
            },
            'nodes': nodes,
            'edges': edges,
            'statistics': {
                'total_positions': total_positions,
                'filled_positions': filled_positions,
                'vacant_positions': vacant_positions,
                'units_included': len(units_to_include)
            }
        }

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def units_list(self, request):
        """
        Get list of all units for the ORBAT dropdown

        Expected URL: /api/units/orbat/units_list/

        Returns: Array of units with basic information
        """
        units = Unit.objects.filter(
            is_active=True
        ).select_related('branch').order_by('name')

        # Annotate with position counts
        units = units.annotate(
            position_count=Count('positions', filter=Q(positions__is_active=True)),
            filled_count=Count('positions', filter=Q(
                positions__is_active=True,
                positions__is_vacant=False
            ))
        )

        # Serialize the data
        units_data = []
        for unit in units:
            units_data.append({
                'id': str(unit.id),
                'name': unit.name,
                'abbreviation': unit.abbreviation,
                'unit_type': unit.unit_type,
                'branch_name': unit.branch.name if unit.branch else None,
                'emblem_url': unit.emblem_url,
                'position_count': unit.position_count,
                'filled_count': unit.filled_count,
                'parent_unit_id': str(unit.parent_unit.id) if unit.parent_unit else None
            })

        return Response(units_data)


