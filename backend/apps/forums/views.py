from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import ForumCategory, ForumThread, ForumPost
from .serializers import (
    ForumCategorySerializer, ForumThreadListSerializer, ForumThreadDetailSerializer,
    ForumPostSerializer, ForumThreadCreateSerializer, ForumPostCreateSerializer
)
from apps.users.views import IsAdminOrReadOnly


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of content or admins to edit it
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_admin


class ForumCategoryViewSet(viewsets.ModelViewSet):
    queryset = ForumCategory.objects.all()
    serializer_class = ForumCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ForumThreadViewSet(viewsets.ModelViewSet):
    queryset = ForumThread.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'is_pinned', 'is_locked']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'last_activity', 'view_count']
    ordering = ['-is_pinned', '-last_activity']
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return ForumThreadListSerializer
        elif self.action == 'create':
            return ForumThreadCreateSerializer
        return ForumThreadDetailSerializer

    def perform_create(self, serializer):
        thread = serializer.save(author=self.request.user)

        # Create the first post for this thread
        ForumPost.objects.create(
            content=self.request.data.get('content', ''),
            thread=thread,
            author=self.request.user
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        thread = self.get_object()
        posts = thread.posts.all()

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = ForumPostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ForumPostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_post(self, request, pk=None):
        thread = self.get_object()

        # Check if thread is locked
        if thread.is_locked:
            return Response({
                "detail": "This thread is locked and cannot be replied to."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = ForumPostCreateSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(
                thread=thread,
                author=request.user
            )

            return Response(ForumPostSerializer(post).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['thread', 'author']
    search_fields = ['content']

    def perform_update(self, serializer):
        serializer.save(is_edited=True, edit_timestamp=timezone.now())