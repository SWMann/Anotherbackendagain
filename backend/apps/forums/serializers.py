from rest_framework import serializers
from .models import ForumCategory, ForumThread, ForumPost


class ForumCategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()
    threads_count = serializers.SerializerMethodField()

    class Meta:
        model = ForumCategory
        fields = '__all__'

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    def get_threads_count(self, obj):
        return obj.threads.count()


class ForumThreadListSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    author_avatar = serializers.ReadOnlyField(source='author.avatar_url')
    category_name = serializers.ReadOnlyField(source='category.name')
    posts_count = serializers.SerializerMethodField()
    last_post = serializers.SerializerMethodField()

    class Meta:
        model = ForumThread
        fields = ['id', 'title', 'author_username', 'author_avatar', 'category',
                  'category_name', 'is_pinned', 'is_locked', 'view_count',
                  'created_at', 'last_activity', 'posts_count', 'last_post']

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_last_post(self, obj):
        last_post = obj.posts.order_by('-created_at').first()
        if last_post:
            return {
                'id': last_post.id,
                'author': last_post.author.username,
                'created_at': last_post.created_at
            }
        return None


class ForumThreadDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    author_avatar = serializers.ReadOnlyField(source='author.avatar_url')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = ForumThread
        fields = '__all__'


class ForumPostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    author_avatar = serializers.ReadOnlyField(source='author.avatar_url')
    author_rank = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = '__all__'

    def get_author_rank(self, obj):
        if obj.author.current_rank:
            return {
                'name': obj.author.current_rank.name,
                'abbreviation': obj.author.current_rank.abbreviation,
                'insignia_image_url': obj.author.current_rank.insignia_image_url
            }
        return None


class ForumThreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumThread
        fields = ['title', 'content', 'category']


class ForumPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = ['content']