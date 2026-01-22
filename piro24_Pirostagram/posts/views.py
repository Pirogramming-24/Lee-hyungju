# posts/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import Follow
from .models import Post, PostImage, PostLike, Comment, Story, StoryItem
from .forms import PostForm, CommentForm


@login_required
def feed(request):

    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    author_ids = list(following_ids) + [request.user.id]
    sort = request.GET.get("sort") or "recent"   # recent/likes/comments
    posts_qs = (
        Post.objects.filter(author_id__in=author_ids)
        .select_related("author")
        .prefetch_related("images")
        .annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )
    )

    if sort == "likes":
        posts_qs = posts_qs.order_by("-like_count", "-created_at")
    elif sort == "comments":
        posts_qs = posts_qs.order_by("-comment_count", "-created_at")
    else:
        posts_qs = posts_qs.order_by("-created_at")

    # 내가 좋아요한 게시글 표시용
    liked_ids = set(
        PostLike.objects.filter(user=request.user, post__in=posts_qs)
        .values_list("post_id", flat=True)
    )
    posts = list(posts_qs)
    for p in posts:
        p.liked_by_me = (p.id in liked_ids)

    stories = (
        Story.objects.filter(author_id__in=author_ids, expires_at__gt=timezone.now())
        .select_related("author")
        .prefetch_related("items")
        .order_by("-created_at")
    )
    context = {
        "posts": posts, 
        "stories": stories,
        "sort": sort,
    }

    return render(request, "posts/feed.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request):
    if request.method == "GET":
        form = PostForm()
        return render(request, "posts/post_form.html", {"form": form, "mode": "게시글 작성"})

    form = PostForm(request.POST)
    images = request.FILES.getlist("images")

    if not form.is_valid():
        return render(request, "posts/post_form.html", {"form": form, "mode": "게시글 작성"})

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    for idx, img in enumerate(images):
        PostImage.objects.create(post=post, image=img, order=idx)

    return redirect("posts:post_detail", post_id=post.id)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related("images"),
        id=post_id
    )

    # 댓글 목록
    comments = (
        Comment.objects.filter(post=post)
        .select_related("author")
        .order_by("created_at")
    )

    # 좋아요 상태/개수
    liked = PostLike.objects.filter(user=request.user, post=post).exists()
    like_count = PostLike.objects.filter(post=post).count()

    # 댓글 작성 (POST는 여기서 처리)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.author = request.user
            c.save()
            return redirect("posts:post_detail", post_id=post.id)
    else:
        form = CommentForm()

    ctx = {
        "post": post,
        "comments": comments,
        "liked": liked,
        "like_count": like_count,
        "form": form,
    }
    return render(request, "posts/post_detail.html", ctx)


@login_required
@require_http_methods(["GET", "POST"])
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.prefetch_related("images"), id=post_id)
    if post.author_id != request.user.id:
        return HttpResponseForbidden("권한 없음")

    if request.method == "GET":
        form = PostForm(instance=post)
        return render(request, "posts/post_form.html", {"form": form, "post": post, "mode": "게시글 수정"})

    form = PostForm(request.POST, instance=post)
    images = request.FILES.getlist("images")
    if not form.is_valid():
        return render(request, "posts/post_form.html", {"form": form, "post": post, "mode": "게시글 수정"})

    form.save()

    max_order = post.images.aggregate(m=Max("order"))["m"]
    start = (max_order + 1) if max_order is not None else 0

    for offset, img in enumerate(images):
        PostImage.objects.create(post=post, image=img, order=start + offset)

    return redirect("posts:post_detail", post_id=post.id)


@login_required
@require_POST
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author_id != request.user.id:
        return HttpResponseForbidden("권한 없음")
    post.delete()
    return redirect("posts:feed")


@login_required
@require_POST
def post_like_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    like_count = PostLike.objects.filter(post=post).count()
    return JsonResponse({"liked": liked, "like_count": like_count})

@login_required
@require_POST
def post_image_delete(request, image_id):
    img = get_object_or_404(PostImage, id=image_id)

    if img.post.author_id != request.user.id:
        return HttpResponseForbidden("권한 없음")

    post_id = img.post_id
    img.delete()
    return redirect("posts:post_edit", post_id=post_id)

@login_required
@require_http_methods(["GET", "POST"])
def comment_edit(request, comment_id):
    c = get_object_or_404(Comment, id=comment_id)
    if c.author_id != request.user.id:
        return HttpResponseForbidden("권한 없음")

    if request.method == "GET":
        form = CommentForm(instance=c)
        return render(request, "posts/comment_edit.html", {"form": form, "comment": c})

    form = CommentForm(request.POST, instance=c)
    if not form.is_valid():
        return render(request, "posts/comment_edit.html", {"form": form, "comment": c})

    form.save()
    return redirect("posts:post_detail", post_id=c.post_id)


@login_required
@require_POST
def comment_delete(request, comment_id):
    c = get_object_or_404(Comment, id=comment_id)
    if c.author_id != request.user.id:
        return HttpResponseForbidden("권한 없음")
    post_id = c.post_id
    c.delete()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def story_list(request):
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    author_ids = list(following_ids) + [request.user.id]

    stories = (
        Story.objects.filter(author_id__in=author_ids, expires_at__gt=timezone.now())
        .select_related("author")
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(request, "posts/story_list.html", {"stories": stories})


@login_required
@require_http_methods(["GET", "POST"])
def story_create(request):
    if request.method == "GET":
        return render(request, "posts/story_form.html")

    images = request.FILES.getlist("images")
    if not images:
        return redirect("posts:story_create")

    now = timezone.now()

    # ✅ 만료 안 된 내 스토리 있으면 그걸 재사용
    story = Story.objects.filter(author=request.user, expires_at__gt=now).order_by("-created_at").first()
    if not story:
        story = Story.objects.create(author=request.user)

    start = story.items.count()
    for offset, img in enumerate(images):
        StoryItem.objects.create(story=story, image=img, order=start + offset)

    return redirect("posts:story_detail", story_id=story.id)


@login_required
def story_detail(request, story_id):
    story = get_object_or_404(
        Story.objects.select_related("author").prefetch_related("items"),
        id=story_id
    )
    stories = Story.objects.order_by("-created_at")
    next_story = stories.filter(created_at__lt=story.created_at).first()
    # print(next_story.id)
    # 만료 스토리는 접근 차단(원하면 404로)
    if story.expires_at <= timezone.now():
        return HttpResponseForbidden("만료된 스토리입니다.")
    return render(request, "posts/story_detail.html", {"story": story, "next_story": next_story})

@login_required
@require_POST
def story_item_delete(request, item_id):
    item = get_object_or_404(StoryItem.objects.select_related("story"), id=item_id)
    if item.story.author_id != request.user.id:
        return HttpResponseForbidden("권한 없음")

    story = item.story
    if request.method == "POST":
        item.delete()

    if not story.items.exists():
        story.delete()
        return redirect("posts:feed")

    return redirect("posts:story_detail", story_id=story.id)
