from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Conversation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    ROLE_CHOICES = (
        ("user", "user"),
        ("assistant", "assistant"),
    )
    # Conversation Foreign 키
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    current_conversation = models.OneToOneField(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_for_profile",
    )