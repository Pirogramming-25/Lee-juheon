from django.shortcuts import render, redirect, get_object_or_404
from .models import Idea, DevTool, IdeaStar
from .forms import IdeaForm, DevToolForm


def idea_list(request):
    sort = request.GET.get('sort', 'latest')

    ideas = Idea.objects.select_related('devtool').all()

    if sort == 'name':
        ideas = ideas.order_by('title')
    elif sort == 'interest':
        ideas = ideas.order_by('-interest')
    elif sort == 'old':
        ideas = ideas.order_by('created_at')
    else:
        ideas = ideas.order_by('-created_at')

    starred_ids = set(IdeaStar.objects.values_list('idea_id', flat=True))

    context = {
        'ideas': ideas,
        'starred_ids': starred_ids,
        'sort': sort,
    }
    return render(request, 'ideas/idea_list.html', context)


def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save()
            return redirect('ideas:idea-detail', idea.pk)
    else:
        form = IdeaForm()

    return render(request, 'ideas/idea_form.html', {'form': form})


def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    is_starred = IdeaStar.objects.filter(idea=idea).exists()

    context = {
        'idea': idea,
        'is_starred': is_starred,
    }
    return render(request, 'ideas/idea_detail.html', context)


def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            idea = form.save()
            return redirect('ideas:idea-detail', idea.pk)
    else:
        form = IdeaForm(instance=idea)

    return render(request, 'ideas/idea_form.html', {'form': form})


def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        idea.delete()
        return redirect('ideas:idea-list')

    return render(request, 'ideas/idea_confirm_delete.html', {'idea': idea})


def idea_star_toggle(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    star = IdeaStar.objects.filter(idea=idea).first()

    if star:
        star.delete()
    else:
        IdeaStar.objects.create(idea=idea)

    return redirect(request.META.get('HTTP_REFERER', 'ideas:idea-list'))


def idea_interest_update(request, pk, action):
    idea = get_object_or_404(Idea, pk=pk)

    if action == 'plus':
        idea.interest += 1
    elif action == 'minus' and idea.interest > 0:
        idea.interest -= 1

    idea.save()

    return redirect(request.META.get('HTTP_REFERER', 'ideas:idea-list'))


def devtool_list(request):
    devtools = DevTool.objects.all()
    return render(request, 'ideas/devtool_list.html', {'devtools': devtools})


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


def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == 'POST':
        devtool.delete()
        return redirect('ideas:devtool-list')

    return render(request, 'ideas/devtool_confirm_delete.html', {'devtool': devtool})