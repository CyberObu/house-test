from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Category


def post_list(request):
    posts = Post.objects.filter(is_published=True).select_related('author', 'category')
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    paginator = Paginator(posts, 9)
    page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()
    recent = Post.objects.filter(is_published=True)[:5]
    return render(request, 'blog/list.html', {
        'page_obj': page,
        'categories': categories,
        'recent': recent,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    post.views_count += 1
    post.save(update_fields=['views_count'])
    recent = Post.objects.filter(is_published=True).exclude(pk=post.pk)[:4]
    categories = Category.objects.all()
    return render(request, 'blog/detail.html', {
        'post': post,
        'recent': recent,
        'categories': categories,
    })
