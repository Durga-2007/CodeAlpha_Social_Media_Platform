from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Comment, Like, Follow, Notification, Profile
from .forms import RegisterForm, PostForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.db.models import Count, Q

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'social/register.html', {'form': form})

@login_required
def feed(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(content__icontains=query) | Q(user__username__icontains=query)
        ).order_by('-timestamp')
    else:
        posts = Post.objects.all().order_by('-timestamp')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    
    for post in posts:
        post.is_liked = Like.objects.filter(post=post, user=request.user).exists()
        
    notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Suggested creators (excluding self and already followed)
    followed_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    suggested_creators = User.objects.exclude(id=request.user.id).exclude(id__in=followed_ids).annotate(post_count=Count('posts')).order_by('-post_count')[:5]

    context = {
        'posts': posts, 
        'form': form, 
        'unread_notifications': notifications, 
        'query': query,
        'suggested_creators': suggested_creators
    }
    return render(request, 'social/feed.html', context)

@login_required
def settings_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your artistic profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'social/settings.html', context)

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    user_posts = Post.objects.filter(user=user)
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    follower_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    context = {
        'profile_user': user,
        'posts': user_posts,
        'is_following': is_following,
        'follower_count': follower_count,
        'following_count': following_count,
    }
    return render(request, 'social/profile.html', context)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_qs = Like.objects.filter(post=post, user=request.user)
    if like_qs.exists():
        like_qs.delete()
    else:
        Like.objects.create(post=post, user=request.user)
        if post.user != request.user:
            Notification.objects.create(user=post.user, sender=request.user, post=post, notification_type='LIKE')
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        follow_qs = Follow.objects.filter(follower=request.user, following=user_to_follow)
        if follow_qs.exists():
            follow_qs.delete()
        else:
            Follow.objects.create(follower=request.user, following=user_to_follow)
            Notification.objects.create(user=user_to_follow, sender=request.user, notification_type='FOLLOW')
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            if post.user != request.user:
                Notification.objects.create(user=post.user, sender=request.user, post=post, notification_type='COMMENT')
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('feed')
    else:
        form = PostForm(instance=post)
    return render(request, 'social/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return redirect('feed')

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    return render(request, 'social/notifications.html', {'notifications': notifications})
