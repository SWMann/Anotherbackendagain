from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import StandardGroup, StandardSubGroup, Standard
from .serializers import (
    StandardGroupListSerializer, StandardGroupDetailSerializer,
    StandardSubGroupSerializer, StandardListSerializer, StandardDetailSerializer,
    StandardApproveSerializer
)
from apps.users.views import IsAdminOrReadOnly
from django.db import models


class StandardGroupViewSet(viewsets.ModelViewSet):
    queryset = StandardGroup.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order_index']
    ordering = ['order_index', 'name']
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return StandardGroupListSerializer
        return StandardGroupDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def subgroups(self, request, pk=None):
        group = self.get_object()
        subgroups = group.subgroups.all().order_by('order_index', 'name')

        serializer = StandardSubGroupSerializer(subgroups, many=True)
        return Response(serializer.data)


class StandardSubGroupViewSet(viewsets.ModelViewSet):
    queryset = StandardSubGroup.objects.all()
    serializer_class = StandardSubGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['standard_group', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order_index']
    ordering = ['order_index', 'name']
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def standards(self, request, pk=None):
        subgroup = self.get_object()
        standards = subgroup.standards.all().order_by('document_number', 'title')

        serializer = StandardListSerializer(standards, many=True)
        return Response(serializer.data)


class StandardViewSet(viewsets.ModelViewSet):
    queryset = Standard.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['standard_sub_group', 'status', 'difficulty_level', 'is_required', 'author']
    search_fields = ['title', 'document_number', 'content', 'summary', 'tags']
    ordering_fields = ['document_number', 'title', 'effective_date', 'created_at']
    ordering = ['document_number', 'title']
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return StandardListSerializer
        return StandardDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        standard = self.get_object()

        # Only admins can approve standards
        if not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to approve standards."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StandardApproveSerializer(data=request.data)
        if serializer.is_valid():
            status_value = serializer.validated_data['status']
            effective_date = serializer.validated_data.get('effective_date')
            review_date = serializer.validated_data.get('review_date')

            standard.status = status_value
            standard.approved_by = request.user
            standard.approval_date = timezone.now()

            if effective_date:
                standard.effective_date = effective_date

            if review_date:
                standard.review_date = review_date

            standard.save()

            return Response({
                "id": standard.id,
                "title": standard.title,
                "status": standard.status,
                "approved_by": request.user.username,
                "approval_date": standard.approval_date
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search standards by keyword."""
        query = request.query_params.get('q', '')

        if not query:
            return Response({"detail": "Search query is required."}, status=status.HTTP_400_BAD_REQUEST)

        standards = Standard.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(document_number__icontains=query) |
            models.Q(content__icontains=query) |
            models.Q(summary__icontains=query) |
            models.Q(tags__contains=[query])
        )

        serializer = StandardListSerializer(standards, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently updated standards."""
        recent_standards = Standard.objects.filter(
            status='Active'
        ).order_by('-updated_at')[:10]

        serializer = StandardListSerializer(recent_standards, many=True)
        return Response(serializer.data)