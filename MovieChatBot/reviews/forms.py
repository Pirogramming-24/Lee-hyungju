from django import forms
from tmdb_api.models import Movie
from .models import Review

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ["title", "director", "leadActor", "genre", "runningTime", "release_date", "poster_path", "poster_img"]
        widgets = {
            "release_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "title": "영화 제목",
            "director": "감독",
            "leadActor": "주연 배우",
            "genre": "장르",
            "runningTime": "러닝타임(분)",
            "overview": "줄거리",
            "release_date": "개봉일",
            "poster_path": "포스터 URL",
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["title", "rating", "content"]
        labels = {
            "title": "리뷰 제목",
            "rating": "평점",
            "content": "리뷰 내용",
        }
