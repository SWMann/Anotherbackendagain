# backend/apps/announcements/serializers.py
from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'author', 'is_pinned',
                  'is_published', 'publish_date', 'created_at']

    def get_author(self, obj):
        if obj.author:
            return {
                'id': obj.author.id,
                'username': obj.author.username,
                'avatar_url': obj.author.avatar_url,
                'current_rank': {
                    'abbreviation': obj.author.current_rank.abbreviation,
                    'name': obj.author.current_rank.name
                } if obj.author.current_rank else None
            }
        return None