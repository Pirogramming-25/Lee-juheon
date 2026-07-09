from django.urls import path

from . import views


app_name = "posts"


urlpatterns = [
    path(
        "",
        views.feed,
        name="feed",
    ),

    path(
        "posts/create/",
        views.post_create,
        name="create",
    ),

    path(
        "posts/search/",
        views.post_search,
        name="search",
    ),

    path(
    "posts/<int:post_id>/like/",
    views.like_toggle,
    name="like_toggle",
    ),

    path(
        "posts/<int:post_id>/",
        views.post_detail,
        name="detail",
    ),

    path(
        "posts/<int:post_id>/edit/",
        views.post_update,
        name="update",
    ),

    path(
        "posts/<int:post_id>/delete/",
        views.post_delete,
        name="delete",
    ),

    path(
        "posts/<int:post_id>/comments/create/",
        views.comment_create,
        name="comment_create",
    ),

    path(
        "comments/<int:comment_id>/edit/",
        views.comment_update,
        name="comment_update",
    ),

    path(
        "comments/<int:comment_id>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),

    path(
        "comments/<int:comment_id>/reply/",
        views.comment_reply,
        name="comment_reply",
    ),
]