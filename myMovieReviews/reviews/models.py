from django.db import models

class Review(models.Model) :
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

    title = models.CharField(max_length=50)
    director = models.CharField(max_length=50)
    leadActor = models.CharField(max_length=50)
    genre = models.CharField(max_length=32, choices=GENRE_CHOICES)
    rating = models.FloatField(
        default=0
        # validators= [MinV]
    )
    runningTime = models.IntegerField()
    releaseYear = models.IntegerField()
    content = models.TextField()
    imageURL = models.URLField(blank=True)


