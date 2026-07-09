from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from stories.models import Story
from users.models import Follow

from .forms import CommentForm, PostCreateForm, PostUpdateForm
from .models import Comment, Like, Post, PostImage

@login_required
def feed(request):
    User = get_user_model()

    # 현재 사용자가 팔로우한 사람들의 ID를 실제 리스트로 변환
    following_ids = list(
        Follow.objects.filter(
            follower=request.user,
        ).values_list(
            "following_id",
            flat=True,
        )
    )

    # 피드에 표시할 작성자:
    # 나 + 내가 팔로우한 사람
    visible_author_ids = [
        request.user.id,
        *following_ids,
    ]

    # 내 게시글 + 팔로우한 사람의 게시글
    posts = (
        Post.objects
        .filter(
            author_id__in=visible_author_ids,
        )
        .annotate(
            is_liked=Exists(
                Like.objects.filter(
                    post_id=OuterRef("pk"),
                    user=request.user,
                )
            )
        )
        .select_related(
            "author",
            "author__profile",
        )
        .prefetch_related(
            "images",
            "likes",
            "comments__author",
        )
    )

    sort = request.GET.get("sort", "latest")

    if sort == "likes":
        posts = (
            posts
            .annotate(
                like_count=Count(
                    "likes",
                    distinct=True,
                )
            )
            .order_by(
                "-like_count",
                "-created_at",
            )
        )

    elif sort == "comments":
        posts = (
            posts
            .annotate(
                comment_count=Count(
                    "comments",
                    distinct=True,
                )
            )
            .order_by(
                "-comment_count",
                "-created_at",
            )
        )

    else:
        posts = posts.order_by("-created_at")

    # 현재 시점 기준 24시간 전
    story_expiration_time = (
        timezone.now()
        - timedelta(hours=24)
    )

    # 나 + 팔로우한 사람의 24시간 이내 스토리
    # 실제 이미지가 하나 이상 있는 스토리만 조회
    active_stories = (
        Story.objects
        .filter(
            author_id__in=visible_author_ids,
            created_at__gte=story_expiration_time,
            images__isnull=False,
        )
        .select_related(
            "author",
            "author__profile",
        )
        .prefetch_related(
            "images",
        )
        .order_by(
            "-created_at",
        )
        .distinct()
    )

    # 같은 사용자가 여러 번 업로드했으면
    # 가장 최근 Story 하나를 대표 스토리로 사용
    story_cards = []
    added_author_ids = set()

    for story in active_stories:
        if story.author_id in added_author_ids:
            continue

        story_cards.append({
            "user": story.author,
            "story": story,
        })

        added_author_ids.add(
            story.author_id
        )

    recommended_users = (
        User.objects
        .exclude(id=request.user.id)
        .exclude(id__in=following_ids)
        .select_related("profile")
        .order_by("?")[:4]
    )

    context = {
        "posts": posts,
        "sort": sort,
        "story_cards": story_cards,
        "recommended_users": recommended_users,
    }

    return render(
        request,
        "posts/feed.html",
        context,
    )

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects
        .annotate(
            is_liked=Exists(
                Like.objects.filter(
                    post_id=OuterRef("pk"),
                    user=request.user,
                )
            )
        )
        .select_related(
            "author",
            "author__profile",
        )
        .prefetch_related(
            "images",
            "likes",
            "comments__author",
            "comments__replies__author",
        ),
        id=post_id,
    )

    # prefetch된 댓글 캐시를 그대로 사용 (추가 쿼리 없이 최상위 댓글만 추림)
    top_level_comments = [
        comment
        for comment in post.comments.all()
        if comment.parent_id is None
    ]

    comment_form = CommentForm()

    context = {
        "post": post,
        "top_level_comments": top_level_comments,
        "comment_form": comment_form,
    }

    return render(
        request,
        "posts/post_detail.html",
        context,
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            PostImage.objects.create(
                post=post,
                image=form.cleaned_data["image"],
                order=0,
            )

            return redirect(
                "posts:detail",
                post_id=post.id,
            )
    else:
        form = PostCreateForm()

    context = {
        "form": form,
        "page_title": "새 게시물 만들기",
        "submit_text": "공유하기",
    }

    return render(
        request,
        "posts/post_form.html",
        context,
    )


@login_required
def post_update(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user,
    )

    if request.method == "POST":
        form = PostUpdateForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            post = form.save()

            new_image = form.cleaned_data.get("image")

            if new_image:
                for post_image in post.images.all():
                    post_image.image.delete(save=False)
                    post_image.delete()

                PostImage.objects.create(
                    post=post,
                    image=new_image,
                    order=0,
                )

            return redirect(
                "posts:detail",
                post_id=post.id,
            )
    else:
        form = PostUpdateForm(instance=post)

    context = {
        "form": form,
        "post": post,
        "page_title": "게시물 수정",
        "submit_text": "수정 완료",
    }

    return render(
        request,
        "posts/post_form.html",
        context,
    )


@login_required
@require_POST
def post_delete(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user,
    )

    for post_image in post.images.all():
        post_image.image.delete(save=False)

    post.delete()

    return redirect("posts:feed")


@login_required
@require_POST
def comment_create(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )

    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect(
        "posts:detail",
        post_id=post.id,
    )


@login_required
@require_POST
def comment_reply(request, comment_id):
    parent_comment = get_object_or_404(
        Comment,
        id=comment_id,
    )

    form = CommentForm(request.POST)

    if form.is_valid():
        reply = form.save(commit=False)
        reply.post = parent_comment.post
        reply.author = request.user
        reply.parent = parent_comment
        reply.save()

    return redirect(
        "posts:detail",
        post_id=parent_comment.post.id,
    )


@login_required
def comment_update(request, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        author=request.user,
    )

    if request.method == "POST":
        form = CommentForm(
            request.POST,
            instance=comment,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "posts:detail",
                post_id=comment.post.id,
            )
    else:
        form = CommentForm(instance=comment)

    context = {
        "form": form,
        "comment": comment,
    }

    return render(
        request,
        "posts/comment_form.html",
        context,
    )


@login_required
@require_POST
def comment_delete(request, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        author=request.user,
    )

    post_id = comment.post.id
    comment.delete()

    return redirect(
        "posts:detail",
        post_id=post_id,
    )


@login_required
@require_POST
def like_toggle(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )

    like = Like.objects.filter(
        user=request.user,
        post=post,
    ).first()

    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(
            user=request.user,
            post=post,
        )
        liked = True

    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count(),
    })


@login_required
def post_search(request):
    query = request.GET.get("q", "").strip()

    posts = Post.objects.none()

    if query:
        posts = (
            Post.objects
            .filter(
                Q(content__icontains=query)
                | Q(author__username__icontains=query)
            )
            .select_related(
                "author",
                "author__profile",
            )
            .prefetch_related(
                "images",
            )
            .order_by("-created_at")
            .distinct()
        )

    context = {
        "query": query,
        "posts": posts,
    }

    return render(
        request,
        "posts/search.html",
        context,
    )