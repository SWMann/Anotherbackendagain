# backend/apps/announcements/views.py
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Announcement
from .serializers import AnnouncementSerializer
from apps.users.views import IsAdminOrReadOnly


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.filter(is_published=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_pinned', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'publish_date']
    ordering = ['-is_pinned', '-created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)