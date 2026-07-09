from django.contrib import admin

from .models import Story, StoryImage


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author",
        "created_at",
    ]


@admin.register(StoryImage)
class StoryImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "story",
        "order",
    ]