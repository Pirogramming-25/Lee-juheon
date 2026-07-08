from django.contrib import admin

from .models import Follow, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "name",
    ]

    search_fields = [
        "user__username",
        "name",
    ]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "follower",
        "following",
        "created_at",
    ]