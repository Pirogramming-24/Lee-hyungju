from django.shortcuts import render, get_object_or_404
from .services import fetch_popular_movies, fetch_movie_detail, fetch_movie_credits, map_genre_by_id
from .models import Movie
# Create your views here.

# def popular_movies(request):
#     count = int(request.GET.get("count", "30"))  # 20~40
#     count = max(20, min(40, count))

#     movies = fetch_popular_movies(count=count)
#     for m in movies:
#         m["poster_url"] = poster_url(m.get("poster_path"))

#     return render(request, "tmdb_api/popular_movies.html", {"movies": movies, "count": count})

def movie_list(request):
    try:
        page = int(request.GET.get("page", "1"))
    except ValueError:
        page = 1
    if page < 1:
        page = 1

    data = fetch_popular_movies(page=page, language="ko-KR")

    page_info = {
        "page": data["page"],
        "total_pages": data["total_pages"],
        "has_prev": data["page"] > 1,
        "has_next": data["page"] < data["total_pages"],
        "prev_page": data["page"] - 1,
        "next_page": data["page"] + 1,
    }

    return render(request, "tmdb_api/movie_list.html", {
        "movies": data["movies"],
        "page_info": page_info,
    })

def movie_detail(request, tmdb_id):
    detail = fetch_movie_detail(tmdb_id, language="ko-KR")
    director, lead_actor = fetch_movie_credits(tmdb_id)

    # DB 기록/갱신
    movie_obj, _ = Movie.objects.update_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "title": detail.get("title") or "",
            "overview": detail.get("overview") or "",
            "release_date": detail.get("release_date") or None,  # 모델이 DateField(null=True)여야 함
            "poster_path": detail.get("poster_url") or "",       # 지금 URLField로 쓰는 중
            "runningTime": detail.get("runtime") or None,
            "genre": map_genre_by_id(detail),
            "director": director,
            "leadActor": lead_actor,
        }
    )

    # 화면은 TMDB 응답 + credits 합친 걸로 렌더링 (즉시 반영)
    detail["director"] = director
    detail["leadActor"] = lead_actor
    detail["runningTime"] = detail.get("runtime")
    detail["genre_display"] = movie_obj.get_genre_display() if movie_obj.genre else None

    return render(request, "tmdb_api/movie_detail.html", {"movie": detail, "movie_obj": movie_obj})