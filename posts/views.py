from django.shortcuts import render, get_object_or_404, redirect
from django. contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from yatube.settings import TEN_POSTS


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, TEN_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, TEN_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page}
    return render(request, 'group.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    profile_posts = profile.posts.all()
    # paginator = Paginator(profile_posts, TEN_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = profile.following.filter(user__username=request.user)
    context = {
        'page': page,
        'profile': profile,
        'profile_posts': profile_posts,
        # 'paginator': paginator,
        'profile': profile,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = Comment.objects.filter(post__id=post_id)
    following = profile.following.filter(user__username=request.user)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    context = {
        'author': post.author,
        'post': post,
        'comments': comments,
        'form': form,
        'profile': profile,
        'following': following,
    }
    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = Comment.objects.filter(post__id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username, post_id)

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'includes/comments.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    group = post.group

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=post.author.username, post_id=post.id)

    context = {
        'post': post,
        'group': group,
        'form': form
    }
    return render(request, 'post_edit.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')

    context = {'form': form}
    return render(request, 'new_post.html', context)


# view-функции для подписки
@login_required
def follow_index(request):
    user = request.user
    followings = user.follower.all()
    posts = []
    if followings:
        for following in followings:
            posts += Post.objects.filter(author=following.author)
    page_number = request.GET.get('page')
    paginator = Paginator(posts, TEN_POSTS)
    page = paginator.get_page(page_number)
    context = {
        'user': user,
        'followings': followings,
        'page': page,
        'paginator': paginator
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        user = request.user
        following = User.objects.get(username=username)
        if not Follow.objects.filter(user=user, author=following):
            Follow.objects.create(user=user, author=following)
    return redirect('index')


@login_required
def profile_unfollow(request, username):
    user = request.user
    following = User.objects.get(username=username)
    Follow.objects.get(user=user, author=following).delete()
    return redirect('index')


# views для страниц с ошибками
def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        status=500
    )
