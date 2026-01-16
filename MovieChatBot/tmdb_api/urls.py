from django.urls import path
from . import views

app_name = "tmdb_api"

urlpatterns = [
    path("test/movies/", views.popular_movies, name="popular_movies"),
]
