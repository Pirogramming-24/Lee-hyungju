# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, UniqueConstraint

class User(AbstractUser):
    name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

class Follow(models.Model):
    follower = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="following_relations")
    following = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="follower_relations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["follower", "following"], name="uq_follow"),
            models.CheckConstraint(check=~Q(follower=models.F("following")), name="ck_no_self_follow"),
        ]
        indexes = [
            models.Index(fields=["follower", "created_at"]),
            models.Index(fields=["following", "created_at"]),
        ]
