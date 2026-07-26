from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
import tempfile
import os
from django.http import JsonResponse
from .services.ocr_service import analyze_nutrition_image
from .services.hashtag_service import detect_hashtags

# Create your views here.
def main(request):
    posts = Post.objects.all()

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    tag = request.GET.get('tag')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)  # 대소문자 구분 없이 검색

    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass  # 필터를 무시하되, 기존 검색 필터를 유지

    if tag:
        posts = posts.filter(hashtags__icontains=tag)

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
        'tag': tag,
    }
    return render(request, 'posts/list.html', context=context)

def create(request):
    if request.method == 'GET':
        form = PostForm()
        context = { 'form': form }
        return render(request, 'posts/create.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('/')

def detail(request, pk):
    target_post = Post.objects.get(id = pk)
    context = { 'post': target_post }
    return render(request, 'posts/detail.html', context=context)

def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = {
            'form': form, 
            'post': post
        }
        return render(request, 'posts/update.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:detail', pk=pk)

def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

def ocr_analyze(request):
    """비동기 OCR 분석 API. 영양성분 이미지 업로드 즉시 프론트에서 호출."""
    if request.method != 'POST' or 'nutrition_photo' not in request.FILES:
        return JsonResponse({'error': 'invalid request'}, status=400)

    image_file = request.FILES['nutrition_photo']
    suffix = os.path.splitext(image_file.name)[1] or '.jpg'

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        for chunk in image_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        result = analyze_nutrition_image(tmp_path)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        os.remove(tmp_path)

def hashtag_analyze(request):
    """비동기 해시태그 자동 감지 API. 상품 이미지 업로드 즉시 프론트에서 호출."""
    if request.method != 'POST' or 'photo' not in request.FILES:
        return JsonResponse({'error': 'invalid request'}, status=400)

    image_file = request.FILES['photo']
    suffix = os.path.splitext(image_file.name)[1] or '.jpg'

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        for chunk in image_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        hashtags = detect_hashtags(tmp_path)
        return JsonResponse({'hashtags': ' '.join(hashtags)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        os.remove(tmp_path)