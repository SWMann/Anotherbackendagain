from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Branch, Rank, Unit, Position, UserPosition
from .serializers import (
    BranchSerializer, RankSerializer, UnitListSerializer, UnitDetailSerializer,
    PositionSerializer, UserPositionSerializer, UnitMemberSerializer,
    UnitHierarchySerializer, ChainOfCommandSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage  # Add this import
import traceback  # Add this for better error handling
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.views import MediaContextMixin
from .models import Rank
from .serializers import RankSerializer, RankCreateUpdateSerializer
from ..core.views import MediaContextMixin

User = get_user_model()


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def units(self, request, pk=None):
        branch = self.get_object()
        units = Unit.objects.filter(branch=branch)
        serializer = UnitListSerializer(units, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def ranks(self, request, pk=None):
        branch = self.get_object()
        ranks = Rank.objects.filter(branch=branch)
        serializer = RankSerializer(ranks, many=True)
        return Response(serializer.data)


# backend/apps/units/views.py
# Update the RankViewSet class:




class RankViewSet(MediaContextMixin, viewsets.ModelViewSet):
    """
    ViewSet for Rank management with proper media URL handling
    """
    pagination_class = None
    queryset = Rank.objects.all().order_by('branch', 'tier')
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['branch', 'is_officer', 'is_enlisted', 'is_warrant']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return RankCreateUpdateSerializer
        return RankSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def upload_insignia(self, request, pk=None):
        """Upload insignia image for a specific rank"""
        rank = self.get_object()

        if 'insignia_image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the uploaded image
        rank.insignia_image = request.FILES['insignia_image']
        rank.save()

        # Return serialized rank with proper context
        serializer = RankSerializer(rank, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAdminUser])
    def delete_insignia(self, request, pk=None):
        """Delete the insignia image for a specific rank"""
        rank = self.get_object()

        if rank.insignia_image:
            # Delete the file
            rank.insignia_image.delete(save=False)
            rank.insignia_image = None
            rank.save()

            return Response({'message': 'Insignia image deleted successfully'})

        return Response(
            {'error': 'No insignia image to delete'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def progression(self, request):
        """Get rank progression path for all branches."""
        branches = Branch.objects.all()
        result = {}

        for branch in branches:
            enlisted_ranks = Rank.objects.filter(branch=branch, is_enlisted=True).order_by('tier')
            officer_ranks = Rank.objects.filter(branch=branch, is_officer=True).order_by('tier')
            warrant_ranks = Rank.objects.filter(branch=branch, is_warrant=True).order_by('tier')

            result[branch.name] = {
                'enlisted': RankSerializer(enlisted_ranks, many=True).data,
                'officer': RankSerializer(officer_ranks, many=True).data,
                'warrant': RankSerializer(warrant_ranks, many=True).data
            }

        return Response(result)

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['branch', 'parent_unit', 'is_active']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UnitDetailSerializer
        return UnitListSerializer

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def members(self, request, pk=None):
        unit = self.get_object()
        user_positions = UserPosition.objects.filter(unit=unit)
        serializer = UnitMemberSerializer(user_positions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def positions(self, request, pk=None):
        unit = self.get_object()
        positions = Position.objects.filter(unit=unit)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def events(self, request, pk=None):
        unit = self.get_object()
        events = unit.event_set.all()
        from apps.events.serializers import EventListSerializer
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def hierarchy(self, request, pk=None):
        unit = self.get_object()
        serializer = UnitHierarchySerializer(unit)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def structure(self, request):
        # Get all top-level units (those without parent units)
        top_units = Unit.objects.filter(parent_unit=None)
        serializer = UnitHierarchySerializer(top_units, many=True)
        return Response(serializer.data)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['unit']  # Removed 'is_command_position', 'is_staff_position'

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def users(self, request, pk=None):
        position = self.get_object()
        user_positions = UserPosition.objects.filter(position=position)
        serializer = UserPositionSerializer(user_positions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def chain_of_command(self, request):
        # Get top-level positions (those without parent positions)
        top_positions = Position.objects.filter(parent_position=None, is_command_position=True)
        serializer = ChainOfCommandSerializer(top_positions, many=True)
        return Response(serializer.data)