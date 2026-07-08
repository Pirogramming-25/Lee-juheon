from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProfileEditForm, SignupForm
from .models import Follow, Profile


User = get_user_model()


def signup(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("posts:feed")
    else:
        form = SignupForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "users/signup.html",
        context,
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        form = AuthenticationForm(
            request=request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("posts:feed")
    else:
        form = AuthenticationForm(request=request)

    context = {
        "form": form,
    }

    return render(
        request,
        "users/login.html",
        context,
    )


@login_required
@require_POST
def logout_view(request):
    logout(request)

    return redirect("users:login")


@login_required
def profile(request, username):
    profile_user = get_object_or_404(
        User,
        username=username,
    )

    profile, _ = Profile.objects.get_or_create(
        user=profile_user,
    )

    posts = profile_user.posts.all()

    follower_count = profile_user.follower_relations.count()
    following_count = profile_user.following_relations.count()

    is_following = False

    if request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user,
        ).exists()

    context = {
        "profile_user": profile_user,
        "profile": profile,
        "posts": posts,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
    }

    return render(
        request,
        "users/profile.html",
        context,
    )


@login_required
def user_search(request):
    query = request.GET.get("q", "").strip()

    users = User.objects.none()

    if query:
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(profile__name__icontains=query)
        ).distinct()

    context = {
        "query": query,
        "users": users,
    }

    return render(
        request,
        "users/search.html",
        context,
    )


@login_required
@require_POST
def follow_toggle(request, username):
    target_user = get_object_or_404(
        User,
        username=username,
    )

    if request.user == target_user:
        return redirect(
            "users:profile",
            username=username,
        )

    follow = Follow.objects.filter(
        follower=request.user,
        following=target_user,
    ).first()

    if follow:
        follow.delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=target_user,
        )

    return redirect(
        "users:profile",
        username=username,
    )

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
    )

    if request.method == "POST":
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "users:profile",
                username=request.user.username,
            )
    else:
        form = ProfileEditForm(
            instance=profile,
        )

    context = {
        "form": form,
        "profile": profile,
    }

    return render(
        request,
        "users/profile_edit.html",
        context,
    )