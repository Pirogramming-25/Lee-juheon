from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

from .models import Idea, DevTool, IdeaStar
from .forms import IdeaForm, DevToolForm
from django.db.models import Q, Count


def idea_list(request):
    sort = request.GET.get('sort', 'latest')
    q = request.GET.get('q', '').strip()

    ideas = (
        Idea.objects
        .select_related('devtool', 'author')
        .prefetch_related('stars')
        .annotate(star_count=Count('stars'))
    )

    if q:
        ideas = ideas.filter(
            Q(title__icontains=q) |
            Q(devtool__name__icontains=q) |
            Q(devtool__kind__icontains=q)
        )

    if sort == 'name':
        ideas = ideas.order_by('title')
    elif sort == 'interest':
        ideas = ideas.order_by('-interest')
    elif sort == 'old':
        ideas = ideas.order_by('created_at')
    elif sort == 'star':
        ideas = ideas.order_by('-star_count', '-created_at')
    else:
        ideas = ideas.order_by('-created_at')

    paginator = Paginator(ideas, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        starred_ids = set(
            IdeaStar.objects.filter(user=request.user)
            .values_list('idea_id', flat=True)
        )
    else:
        starred_ids = set()

    context = {
        'page_obj': page_obj,
        'ideas': page_obj,
        'starred_ids': starred_ids,
        'sort': sort,
        'q': q,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'ideas/_idea_results.html',
            context,
            request=request
        )

        return JsonResponse({
            'html': html,
        })

    return render(request, 'ideas/idea_list.html', context)

@login_required
def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.save()
            return redirect('ideas:idea-detail', idea.pk)
    else:
        form = IdeaForm()

    return render(request, 'ideas/idea_form.html', {'form': form})


def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.user.is_authenticated:
        is_starred = IdeaStar.objects.filter(user=request.user, idea=idea).exists()
    else:
        is_starred = False

    context = {
        'idea': idea,
        'is_starred': is_starred,
    }
    return render(request, 'ideas/idea_detail.html', context)


@login_required
def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if idea.author != request.user:
        return redirect('ideas:idea-detail', idea.pk)

    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            idea = form.save()
            return redirect('ideas:idea-detail', idea.pk)
    else:
        form = IdeaForm(instance=idea)

    return render(request, 'ideas/idea_form.html', {'form': form})


@login_required
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if idea.author != request.user:
        return redirect('ideas:idea-detail', idea.pk)

    if request.method == 'POST':
        idea.delete()
        return redirect('ideas:idea-list')

    return render(request, 'ideas/idea_confirm_delete.html', {'idea': idea})


@login_required
@require_POST
def idea_star_toggle(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    star, created = IdeaStar.objects.get_or_create(
        user=request.user,
        idea=idea
    )

    if not created:
        star.delete()
        is_starred = False
    else:
        is_starred = True

    return JsonResponse({
        'is_starred': is_starred,
        'star_count': idea.stars.count()
    })


@require_POST
def idea_interest_update(request, pk, action):
    idea = get_object_or_404(Idea, pk=pk)

    if action == 'plus':
        idea.interest += 1
    elif action == 'minus' and idea.interest > 0:
        idea.interest -= 1

    idea.save()

    return JsonResponse({
        'interest': idea.interest
    })


def devtool_list(request):
    devtools = DevTool.objects.all().order_by('name')

    paginator = Paginator(devtools, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'devtools': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'ideas/devtool_list.html', context)


@login_required
def devtool_create(request):
    if request.method == 'POST':
        form = DevToolForm(request.POST)
        if form.is_valid():
            devtool = form.save()
            return redirect('ideas:devtool-detail', devtool.pk)
    else:
        form = DevToolForm()

    return render(request, 'ideas/devtool_form.html', {'form': form})


def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    ideas = devtool.ideas.all()

    context = {
        'devtool': devtool,
        'ideas': ideas,
    }
    return render(request, 'ideas/devtool_detail.html', context)


@login_required
def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == 'POST':
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid():
            devtool = form.save()
            return redirect('ideas:devtool-detail', devtool.pk)
    else:
        form = DevToolForm(instance=devtool)

    return render(request, 'ideas/devtool_form.html', {'form': form})


@login_required
def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == 'POST':
        devtool.delete()
        return redirect('ideas:devtool-list')

    return render(request, 'ideas/devtool_confirm_delete.html', {'devtool': devtool})