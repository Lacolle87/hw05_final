from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow, Comment
from .forms import PostForm, CommentForm


def paginator(posts, request):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    page_obj = paginator(posts, request)
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    page_obj = paginator(posts, request)
    context = {
        'posts': page_obj,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()
    author_posts = author.posts.all()
    page_obj = paginator(author_posts, request)
    context = {
        'posts': page_obj,
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    context = {
        'post': post,
        'form': comment_form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    edit_form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if edit_post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if edit_form.is_valid():
        edit_form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': edit_form,
        'post': edit_post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        if post.author == request.user:
            confirm = request.POST.get('confirm') == 'True'
            if confirm:
                post.delete()
                return redirect('posts:profile', post.author.username)
            else:
                return redirect('posts:post_detail', post.id)
    return render(request, 'posts/post_delete.html', {'post': post})


@login_required
def add_comment(request, post_id):
    comment_post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = comment_post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author == request.user:
        comment.delete()
    return redirect('posts:post_detail', post_id=comment.post.pk)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(posts, request)
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect('posts:profile', username=username)
