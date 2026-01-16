from django.urls import path
from . import views

app_name = "tmdb_api"

urlpatterns = [
    # path("movies/", views.popular_movies, name="popular_movies"),
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/<int:tmdb_id>/",views.movie_detail, name="movie_detail")
]
