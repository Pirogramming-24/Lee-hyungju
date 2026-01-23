# posts/models.py
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from datetime import timedelta

class Post(models.Model):
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["author", "-created_at"])]

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [UniqueConstraint(fields=["post", "order"], name="uq_post_image_order")]

class PostLike(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="post_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["user", "post"], name="uq_post_like")]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["post", "created_at"])]

class Story(models.Model):
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="stories")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["expires_at"]),
        ]

class StoryItem(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="items")
    image = models.ImageField(upload_to="stories/")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["story", "order"], name="uq_story_item_order")]
