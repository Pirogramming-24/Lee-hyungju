from django.db import models
# from tmdb_api.models import Movie

class Review(models.Model) :
    SOURCE_CHOICES = [
        ("TMDB", "TMDB에서 작성"),
        ("MANUAL", "직접 작성"),
    ]

    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default="MANUAL",
    )

    movie = models.ForeignKey(
        "tmdb_api.Movie", 
        on_delete=models.CASCADE, 
        related_name="reviews",
        blank=True, null= True,
    )
    title = models.CharField(max_length=50)
    rating = models.FloatField(
        default=0
        # validators= [MinV]
    )
    content = models.TextField()
