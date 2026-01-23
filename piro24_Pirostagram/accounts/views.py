# accounts/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import User, Follow
from posts.models import Post  # 프로필에서 게시글 그리드 보여주기
from .forms import SignupForm, LoginForm, ProfileUpdateForm

def signup(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("posts:feed")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("posts:feed")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("accounts:profile", request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})

@login_required
def user_search(request):
    q = (request.GET.get("q") or "").strip()
    print(f"search/q:{q}")
    users = User.objects.none()
    following_ids = set()
    if q:
        # username or name 검색
        users = (
            User.objects.filter(Q(username__icontains=q) | Q(name__icontains=q))
            .annotate(
                follower_count=Count("follower_relations", distinct=True),
                following_count=Count("following_relations", distinct=True),
            )
            .order_by("username")[:50]
        )
        following_ids = set(
            Follow.objects.filter(follower=request.user)
            .values_list("following_id", flat=True)
        )
        print(f"search/users:{users}")
        
    context = {
        "following_ids": following_ids,
        "q": q, 
        "users": users
    }
    return render(request, "accounts/search.html", context)


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # 팔로우 여부
    is_following = False
    if request.user.id != profile_user.id:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    posts = (
        Post.objects.filter(author=profile_user)
        .prefetch_related("images")
        .order_by("-created_at")
    )

    ctx = {
        "profile_user": profile_user,
        "is_following": is_following,
        "follower_count": follower_count,
        "following_count": following_count,
        "post_count": posts.count(),
        "posts": posts,
    }
    return render(request, "accounts/profile.html", ctx)


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)

    if target.id == request.user.id:
        return HttpResponseBadRequest("본인은 팔로우할 수 없습니다.")

    obj = Follow.objects.filter(follower=request.user, following=target)
    if obj.exists():
        obj.delete()
    else:
        Follow.objects.create(follower=request.user, following=target)

    return redirect("accounts:profile", username=target.username)


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile", request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})
