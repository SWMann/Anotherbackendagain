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

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class RankViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Rank.objects.all().order_by('branch', 'tier')
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['branch', 'is_officer', 'is_enlisted', 'is_warrant']
    # Add parsers to handle file uploads
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            from .serializers import RankCreateUpdateSerializer
            return RankCreateUpdateSerializer
        return RankSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def upload_insignia(self, request, pk=None):
        """Upload insignia image for a specific rank"""
        print("\n" + "=" * 50)
        print("UPLOAD_INSIGNIA CALLED")
        print("=" * 50)

        try:
            # Debug request info
            print(f"Rank ID: {pk}")
            print(f"User: {request.user}")
            print(f"Is Admin: {request.user.is_admin}")
            print(f"Request Method: {request.method}")
            print(f"Content Type: {request.content_type}")
            print(f"FILES: {request.FILES}")
            print(f"FILES keys: {list(request.FILES.keys())}")
            print(f"POST data: {request.POST}")

            # Debug storage backend
            print(f"\nStorage Backend: {default_storage.__class__.__name__}")
            print(f"Storage Backend Module: {default_storage.__class__.__module__}")
            print(f"USE_SPACES: {getattr(settings, 'USE_SPACES', 'Not set')}")
            print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")

            rank = self.get_object()
            print(f"\nRank found: {rank.name} ({rank.id})")
            print(f"Current insignia_image: {rank.insignia_image}")
            print(f"Current insignia_image_url: {rank.insignia_image_url}")

            if 'insignia_image' not in request.FILES:
                print("ERROR: No insignia_image in FILES")
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the file
            file_obj = request.FILES['insignia_image']
            print(f"\nFile received: {file_obj.name}")
            print(f"File size: {file_obj.size} bytes")
            print(f"Content type: {file_obj.content_type}")

            # Debug file object
            print(f"File class: {file_obj.__class__.__name__}")
            print(f"File readable: {hasattr(file_obj, 'read')}")

            # Try manual save to storage first
            print("\nTesting direct storage save...")
            try:
                test_path = f"test/manual_{file_obj.name}"
                saved_path = default_storage.save(test_path, file_obj)
                saved_url = default_storage.url(saved_path)
                print(f"Manual save successful!")
                print(f"Saved to: {saved_path}")
                print(f"URL: {saved_url}")

                # Clean up test file
                default_storage.delete(saved_path)
                print("Test file deleted")

                # Reset file pointer
                file_obj.seek(0)
            except Exception as e:
                print(f"Manual save failed: {e}")
                traceback.print_exc()

            # Save the uploaded image to the rank
            print(f"\nSaving to rank.insignia_image field...")
            old_image = rank.insignia_image
            print(f"Old image value: {old_image}")

            try:
                # Try direct assignment
                rank.insignia_image = file_obj
                print(f"Assigned file to field")
                print(f"Field value after assignment: {rank.insignia_image}")

                # Save the model
                rank.save()
                print(f"Model saved")

                # Refresh from database
                rank.refresh_from_db()
                print(f"After refresh - insignia_image: {rank.insignia_image}")
                print(
                    f"After refresh - insignia_image.name: {rank.insignia_image.name if rank.insignia_image else 'None'}")

                # Check if file exists in storage
                if rank.insignia_image:
                    exists = default_storage.exists(rank.insignia_image.name)
                    print(f"File exists in storage: {exists}")
                    if exists:
                        size = default_storage.size(rank.insignia_image.name)
                        print(f"File size in storage: {size}")

            except Exception as e:
                print(f"Error during save: {e}")
                traceback.print_exc()

                # Restore old image
                rank.insignia_image = old_image
                rank.save()

                return Response(
                    {'error': f'Failed to save image: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Serialize and return
            print(f"\nPreparing response...")
            serializer = RankSerializer(rank)
            response_data = serializer.data

            print(f"Response data: {response_data}")
            print("=" * 50 + "\n")

            return Response(response_data)

        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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