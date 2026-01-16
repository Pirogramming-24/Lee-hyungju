from django.shortcuts import render
from .services import fetch_popular_movies, poster_url

# Create your views here.

from django.shortcuts import render
from .services import fetch_popular_movies, poster_url

def popular_movies(request):
    count = int(request.GET.get("count", "30"))  # 20~40
    count = max(20, min(40, count))

    movies = fetch_popular_movies(count=count)
    for m in movies:
        m["poster_url"] = poster_url(m.get("poster_path"))

    return render(request, "tmdb_api/popular_movies.html", {"movies": movies, "count": count})
