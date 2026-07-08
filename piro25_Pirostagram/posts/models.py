from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    content = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}의 게시글 {self.id}"


class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="posts/",
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"게시글 {self.post.id} 이미지"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_post_like",
            )
        ]

    def __str__(self):
        return f"{self.user.username} → 게시글 {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )

    content = models.CharField(
        max_length=300,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"