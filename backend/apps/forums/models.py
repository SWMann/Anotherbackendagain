from django.db import models
from apps.core.models import BaseModel


class ForumCategory(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Forum categories"


class ForumThread(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='forum_threads')
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_pinned', '-last_activity']


class ForumPost(BaseModel):
    content = models.TextField()
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='forum_posts')
    is_edited = models.BooleanField(default=False)
    edit_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Post by {self.author.username} in {self.thread.title}"

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        # Update thread's last_activity timestamp
        self.thread.last_activity = self.created_at or self.updated_at
        self.thread.save(update_fields=['last_activity'])
        super().save(*args, **kwargs)