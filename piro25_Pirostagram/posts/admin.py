from django.contrib import admin

from .models import Comment, Like, Post, PostImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author",
        "created_at",
        "updated_at",
    ]


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post",
        "order",
    ]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "post",
        "created_at",
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author",
        "post",
        "content",
        "created_at",
    ]