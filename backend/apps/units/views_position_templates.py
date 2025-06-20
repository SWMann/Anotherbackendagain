# Create new file: backend/apps/units/views_position_templates.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models

from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import PositionTemplate, TemplatePosition, Position, Unit
from .serializers import (
    PositionTemplateSerializer,
    PositionTemplateCreateSerializer,
    ApplyTemplateSerializer,
    TemplatePreviewSerializer,
    PositionDetailSerializer
)
from apps.users.views import IsAdminOrReadOnly


class PositionTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing position templates"""
    queryset = PositionTemplate.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['template_type', 'name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PositionTemplateCreateSerializer
        return PositionTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview what positions would be created from this template"""
        template = self.get_object()
        unit_id = request.data.get('unit_id')

        if not unit_id:
            return Response(
                {'error': 'unit_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        unit = get_object_or_404(Unit, id=unit_id)

        # Check if template can be applied to this unit
        if template.applicable_unit_types and unit.unit_type not in template.applicable_unit_types:
            return Response(
                {'error': f'Template cannot be applied to unit type {unit.unit_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate preview
        preview_data = self._generate_preview(template, unit)

        return Response(preview_data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def apply(self, request, pk=None):
        """Apply template to create positions in a unit"""
        template = self.get_object()

        serializer = ApplyTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        unit = serializer.validated_data['unit']
        preview_only = serializer.validated_data.get('preview_only', False)
        position_overrides = serializer.validated_data.get('position_overrides', {})

        if preview_only:
            preview_data = self._generate_preview(template, unit, position_overrides)
            return Response(preview_data)

        # Apply template and create positions
        with transaction.atomic():
            created_positions = self._apply_template(template, unit, position_overrides)

        return Response({
            'message': f'Successfully created {len(created_positions)} positions',
            'positions': PositionDetailSerializer(created_positions, many=True).data
        })

    def _generate_preview(self, template, unit, overrides=None):
        """Generate preview of positions that would be created"""
        if overrides is None:
            overrides = {}

        positions_data = []
        hierarchy = {}
        position_map = {}

        # Get all template positions ordered by display order
        template_positions = template.template_positions.all().order_by('display_order')

        for tp in template_positions:
            generated = tp.generate_positions(unit)

            for i, pos_data in enumerate(generated):
                # Apply any overrides
                tp_override_key = f"{tp.id}_{i}"
                if tp_override_key in overrides:
                    pos_data.update(overrides[tp_override_key])

                # Create preview data
                preview_pos = {
                    'template_position_id': tp.id,
                    'role': {
                        'id': pos_data['role'].id,
                        'name': pos_data['role'].name,
                        'category': pos_data['role'].category
                    },
                    'unit': {
                        'id': unit.id,
                        'name': unit.name,
                        'abbreviation': unit.abbreviation
                    },
                    'identifier': pos_data.get('identifier'),
                    'title': pos_data.get('title'),
                    'display_title': pos_data.get(
                        'title') or f"{pos_data.get('identifier', '')} {pos_data['role'].name}".strip(),
                    'display_order': pos_data.get('display_order', 0)
                }

                positions_data.append(preview_pos)

                # Track for hierarchy building
                temp_id = f"temp_{tp.id}_{i}"
                position_map[temp_id] = preview_pos

                if tp.parent_template_position:
                    parent_temp_id = f"temp_{tp.parent_template_position.id}_0"
                    if parent_temp_id not in hierarchy:
                        hierarchy[parent_temp_id] = []
                    hierarchy[parent_temp_id].append(temp_id)

        # Calculate summary
        summary = {
            'total_positions': len(positions_data),
            'by_role': {},
            'by_category': {}
        }

        for pos in positions_data:
            role_name = pos['role']['name']
            category = pos['role']['category']

            summary['by_role'][role_name] = summary['by_role'].get(role_name, 0) + 1
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1

        return {
            'positions': positions_data,
            'hierarchy': hierarchy,
            'summary': summary
        }

    def _apply_template(self, template, unit, overrides=None):
        """Apply template and create actual positions"""
        if overrides is None:
            overrides = {}

        created_positions = []
        position_mapping = {}  # Map template positions to created positions

        # Get all template positions ordered by display order
        template_positions = template.template_positions.all().order_by('display_order')

        for tp in template_positions:
            generated = tp.generate_positions(unit)

            for i, pos_data in enumerate(generated):
                # Apply any overrides
                tp_override_key = f"{tp.id}_{i}"
                if tp_override_key in overrides:
                    pos_data.update(overrides[tp_override_key])

                # Remove template_position from data
                pos_data.pop('template_position', None)

                # Handle parent position
                if tp.parent_template_position and tp.parent_template_position.id in position_mapping:
                    # Use the first created position as parent
                    pos_data['parent_position'] = position_mapping[tp.parent_template_position.id][0]

                # Create position
                position = Position.objects.create(**pos_data)
                created_positions.append(position)

                # Track mapping
                if tp.id not in position_mapping:
                    position_mapping[tp.id] = []
                position_mapping[tp.id].append(position)

        return created_positions

    @action(detail=False, methods=['get'])
    def by_unit_type(self, request):
        """Get templates applicable to a specific unit type"""
        unit_type = request.query_params.get('unit_type')

        if not unit_type:
            return Response(
                {'error': 'unit_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get templates that either have no restrictions or include this unit type
        templates = self.queryset.filter(
            is_active=True
        ).filter(
            models.Q(applicable_unit_types__len=0) |
            models.Q(applicable_unit_types__contains=[unit_type])
        )

        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def duplicate(self, request, pk=None):
        """Duplicate a template"""
        template = self.get_object()
        new_name = request.data.get('name', f"{template.name} (Copy)")

        # Create new template
        new_template = PositionTemplate.objects.create(
            name=new_name,
            description=template.description,
            template_type=template.template_type,
            applicable_unit_types=template.applicable_unit_types,
            is_active=True,
            created_by=request.user
        )

        # Copy branch restrictions
        new_template.allowed_branches.set(template.allowed_branches.all())

        # Copy template positions
        old_to_new_mapping = {}
        for tp in template.template_positions.all().order_by('display_order'):
            old_id = tp.id
            tp.id = None  # Clear ID to create new instance
            tp.template = new_template
            tp.save()
            old_to_new_mapping[old_id] = tp

        # Update parent relationships
        for old_id, new_tp in old_to_new_mapping.items():
            old_tp = TemplatePosition.objects.get(id=old_id)
            if old_tp.parent_template_position:
                new_tp.parent_template_position = old_to_new_mapping.get(
                    old_tp.parent_template_position.id
                )
                new_tp.save()

        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)