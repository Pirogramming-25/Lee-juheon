from django.shortcuts import render, get_object_or_404, redirect
from .models import Review

def format_running_time(minutes):
    minutes = int(minutes)

    hours = minutes // 60
    remain_minutes = minutes % 60

    if hours > 0 and remain_minutes > 0:
        return f'{hours}시간 {remain_minutes}분'
    elif hours > 0:
        return f'{hours}시간'
    else:
        return f'{remain_minutes}분'

def review_list(request):
    sort = request.GET.get('sort', 'latest')

    sort_options = {
        'latest': '-created_at',
        'title': 'title',
        'rating_high': '-rating',
        'rating_low': 'rating',
        'running_time_short': 'running_time',
        'running_time_long': '-running_time',
    }

    order = sort_options.get(sort, '-created_at')

    reviews = Review.objects.all().order_by(order)

    for review in reviews:
        review.running_time_text = format_running_time(review.running_time)

    return render(request, 'reviews/review_list.html', {
        'reviews': reviews,
        'sort': sort,
    })

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.running_time_text = format_running_time(review.running_time)
    return render(request, 'reviews/review_detail.html', {'review': review})


def review_create(request):
    if request.method == 'POST':
        Review.objects.create(
            title=request.POST.get('title'),
            release_year=request.POST.get('release_year'),
            director=request.POST.get('director'),
            actor=request.POST.get('actor'),
            genre=request.POST.get('genre'),
            rating=request.POST.get('rating'),
            running_time=request.POST.get('running_time'),
            content=request.POST.get('content'),
        )
        return redirect('review-list')

    return render(request, 'reviews/review_form.html',{
        'genre_choices': Review.GENRE_CHOICES,
    })


def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if request.method == 'POST':
        review.title = request.POST.get('title')
        review.release_year = request.POST.get('release_year')
        review.director = request.POST.get('director')
        review.actor = request.POST.get('actor')
        review.genre = request.POST.get('genre')
        review.rating = request.POST.get('rating')
        review.running_time = request.POST.get('running_time')
        review.content = request.POST.get('content')
        review.save()

        return redirect('review-detail', pk=pk)

    return render(request, 'reviews/review_form.html', {'review': review, 'genre_choices': Review.GENRE_CHOICES,})


def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if request.method == 'POST':
        review.delete()
        return redirect('review-list')

    return render(request, 'reviews/review_delete.html', {'review': review})