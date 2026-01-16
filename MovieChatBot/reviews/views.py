from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q

from tmdb_api.models import Movie
from tmdb_api.services import fetch_movie_detail, fetch_movie_credits, map_genre_by_id, search_movies

from .models import Review
from .forms import MovieForm, ReviewForm

def test(request):
    return render(request, "base.html")

def review_list(request):
    q = (request.GET.get("q") or "").strip()                 # 검색어
    sort = request.GET.get("sort") or "recent"              # 정렬: title/rating/year/recent
    source = request.GET.get("source") or "all"             # all/tmdb/manual

    qs = Review.objects.select_related("movie")

    # 검색: 리뷰 제목/내용 + 영화 제목/감독/주연
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(movie__title__icontains=q) |
            Q(movie__director__icontains=q) |
            Q(movie__leadActor__icontains=q)
        )

    # TMDB/직접 필터
    # Review.source 필드가 있다면 그걸 쓰는 게 가장 정확함
    if source == "tmdb":
        qs = qs.filter(source="TMDB")
    elif source == "manual":
        qs = qs.filter(source="MANUAL")

    # 정렬
    if sort == "title":
        qs = qs.order_by("movie__title", "title", "-id")   # 영화제목→리뷰제목
    elif sort == "rating":
        qs = qs.order_by("-rating", "-id")
    elif sort == "year":
        qs = qs.order_by("-movie__release_date", "-id")    # 최신 개봉일(=연도) 우선
    else:  # recent
        qs = qs.order_by("-id")

    reviews = qs.all()

    return render(request, "reviews/review_list.html", {
        "reviews": reviews,
        "q": q,
        "sort": sort,
        "source": source,
    })

def review_detail(request, pk):
    review = get_object_or_404(Review.objects.select_related("movie"), id=pk)
    context = {
        "review" : review,
    }
    return render(request, "reviews/review_detail.html", context)


def review_create(request):
    tmdb_id = request.GET.get("tmdb_id")  # 있을 수도, 없을 수도
    movie_instance = None

    if tmdb_id:
        movie_instance = Movie.objects.filter(tmdb_id=tmdb_id).first()

        if movie_instance is None:
            # TMDB에서 가져와서 Movie 생성
            detail = fetch_movie_detail(tmdb_id, language="ko-KR")
            director, lead_actor = fetch_movie_credits(tmdb_id)

            movie_instance = Movie.objects.create(
                tmdb_id=tmdb_id,
                title=detail.get("title") or "",
                overview=detail.get("overview") or "",
                release_date=detail.get("release_date") or None,
                poster_path=detail.get("poster_url") or "",
                runningTime=detail.get("runtime") or None,
                genre=map_genre_by_id(detail),
                director=director,
                leadActor=lead_actor,
            )

    if request.method == "POST":
        # POST로 tmdb_id도 다시 받기 (hidden input으로 넘길 거임)
        tmdb_id_post = request.POST.get("tmdb_id") or None
        if tmdb_id_post:
            movie_instance = get_object_or_404(Movie, tmdb_id=tmdb_id_post)

        movie_form = MovieForm(request.POST, request.FILES, instance=movie_instance)
        review_form = ReviewForm(request.POST)

        if movie_form.is_valid() and review_form.is_valid():
            movie = movie_form.save(commit=False)

            # TMDB로 들어온 케이스면 tmdb_id 유지 (없으면 null/0 금지면 모델 수정 필요)
            if tmdb_id_post:
                movie.tmdb_id = int(tmdb_id_post)

            # tmdb_id 없는 경우: tmdb_id가 필수(unique)라면 여기서 막힘
            # => 해결은 아래 "3) Movie 모델 수정" 참고
            movie.save()

            review = review_form.save(commit=False)
            review.movie = movie
            if movie_instance and movie_instance.tmdb_id:
                review.source = "TMDB"
            else:
                review.source = "MANUAL"
            review.save()

            return redirect("reviews:detail", review.id)

    else:
        movie_form = MovieForm(instance=movie_instance)
        review_form = ReviewForm(initial={"title": movie_instance.title} if movie_instance else None)
    
    context = {
        "movie_form": movie_form,
        "review_form": review_form,
        "tmdb_id": tmdb_id or "",
    }
    return render(request, "reviews/review_create.html", context)

def review_create_search(request):
    q = (request.GET.get("q") or "").strip()
    results = []
    if q:
        results = search_movies(q, language="ko-KR")  # TMDB 검색 결과 리스트

    return render(request, "reviews/review_create_search.html", {
        "q": q,
        "results": results,
    })


def review_update(request,pk):
    review = get_object_or_404(Review, id=pk)
    movie_instance = review.movie  # 없을 수도 있음

    if request.method == "POST":
        movie_form = MovieForm(request.POST, request.FILES, instance=movie_instance)
        review_form = ReviewForm(request.POST, instance=review)

        if movie_form.is_valid() and review_form.is_valid():
            movie = movie_form.save()  # tmdb_id는 폼에 없으니 기존 값 유지됨
            r = review_form.save(commit=False)
            r.movie = movie
            r.save()
            return redirect("reviews:detail", pk=review.id)
    else:
        movie_form = MovieForm(instance=movie_instance)
        review_form = ReviewForm(instance=review)

    return render(request, "reviews/review_update.html", {
        "movie_form": movie_form,
        "review_form": review_form,
        "review": review,
    })

def review_delete(request,pk):
    if request.method != "POST":
        return redirect("reviews:detail", pk=pk)

    review = get_object_or_404(Review, id=pk)
    review.delete()
    return redirect("reviews:review_list")

