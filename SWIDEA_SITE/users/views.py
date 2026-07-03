from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('ideas:idea-list')
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('ideas:idea-list')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('ideas:idea-list')

    return redirect('ideas:idea-list')

@login_required
def profile(request):
    my_ideas = request.user.ideas.all().order_by('-created_at')

    context = {
        'my_ideas': my_ideas,
    }

    return render(request, 'users/profile.html', context)