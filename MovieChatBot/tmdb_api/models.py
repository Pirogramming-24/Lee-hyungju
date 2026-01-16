from django.db import models

# Create your models here.
class Movie(models.Model):
    GENRE_CHOICES = [
        ("ACTION", "액션"),
        ("DRAMA", "드라마"),
        ("COMEDY", "코미디"),
        ("ROMANCE", "로맨스"),
        ("THRILLER", "스릴러"),
        ("HORROR", "공포"),
        ("SF", "SF"),
        ("FANTASY", "판타지"),
        ("ANIMATION", "애니메이션"),
        ("DOCUMENTARY", "다큐"),
    ]
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=64)

    overview = models.TextField(blank=True, default="")
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.URLField(blank=True)
    poster_img = models.ImageField(
        upload_to="posters/",
        null=True,
        blank=True,
    )

    director = models.CharField(max_length=50, null=True, blank=True)
    leadActor = models.CharField(max_length=50, null=True, blank=True)
    genre = models.CharField(max_length=32, choices=GENRE_CHOICES, null=True, blank=True)
    runningTime = models.IntegerField(null=True, blank=True,)
    