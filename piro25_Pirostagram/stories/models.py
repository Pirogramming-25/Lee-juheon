from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Story(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stories",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def expires_at(self):
        return self.created_at + timedelta(hours=24)

    @property
    def is_active(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.author.username}의 스토리"


class StoryImage(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="stories/",
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.story.author.username} 스토리 이미지 {self.order}"