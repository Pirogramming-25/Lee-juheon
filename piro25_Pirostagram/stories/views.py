from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from users.models import Follow

from .forms import StoryCreateForm
from .models import Story, StoryImage


@login_required
@require_http_methods(["GET", "POST"])
def story_create(request):
    if request.method == "POST":
        form = StoryCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            images = form.cleaned_data["images"]

            with transaction.atomic():
                story = Story.objects.create(
                    author=request.user,
                )

                for order, image in enumerate(images):
                    StoryImage.objects.create(
                        story=story,
                        image=image,
                        order=order,
                    )

            return redirect("posts:feed")

    else:
        form = StoryCreateForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "stories/story_form.html",
        context,
    )


@login_required
@require_GET
def story_detail_data(request, story_id):
    following_ids = Follow.objects.filter(
        follower=request.user,
    ).values_list(
        "following_id",
        flat=True,
    )

    allowed_author_ids = [
        request.user.id,
        *following_ids,
    ]

    story = get_object_or_404(
        Story.objects
        .filter(
            id=story_id,
            author_id__in=allowed_author_ids,
            created_at__gte=(
                timezone.now()
                - timedelta(hours=24)
            ),
        )
        .select_related(
            "author",
            "author__profile",
        )
        .prefetch_related(
            "images",
        )
    )

    profile = getattr(
        story.author,
        "profile",
        None,
    )

    profile_image_url = None

    if profile and profile.profile_image:
        profile_image_url = profile.profile_image.url

    images = [
        {
            "id": story_image.id,
            "url": story_image.image.url,
            "order": story_image.order,
        }
        for story_image in story.images.all()
    ]

    return JsonResponse({
        "story_id": story.id,
        "username": story.author.username,
        "profile_image_url": profile_image_url,
        "created_at": story.created_at.isoformat(),
        "images": images,
    })