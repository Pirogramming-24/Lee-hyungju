from django.shortcuts import render, redirect
from .models import Review

def test(request):
    return render(request, "base.html")


def reviews_list(request, *args, **kwargs):
    sort = request.GET.get("sort","")
    reviews = Review.objects.all()
    if sort == "latest":
        reviews = reviews.order_by("-releaseYear")
    elif sort =="rating":
        reviews = reviews.order_by("-rating")
    elif sort =="runtime":
        reviews = reviews.order_by("-runningTime")
    context = { 
        "reviews" : reviews,
        "sort" : sort
    }
    return render(request, "reviews_list.html", context)

def reviews_read(request, pk):
    review = Review.objects.get(id=pk)
    context = {
        "review" : review,
        "genre_choices": Review.GENRE_CHOICES
    }
    return render(request, "reviews_read.html", context)


def reviews_create(request):
    if request.method == 'POST':
        Review.objects.create(
            title = request.POST["title"],
            director = request.POST["director"],
            leadActor = request.POST["leadActor"],
            genre = request.POST["genre"],
            rating =float(request.POST["rating"]),
            runningTime = int(request.POST["runningTime"]),
            releaseYear = int(request.POST["releaseYear"]),
            content = request.POST["content"],
            imageURL = request.POST["imageURL"],
        )
        return redirect("reviews:reviews_list")
    return render(request, "reviews_create.html", {
        "genre_choices": Review.GENRE_CHOICES
    })

def reviews_update(request,pk):
    review = Review.objects.get(id=pk)
    if request.method == "POST":
        review.title = request.POST["title"]
        review.director = request.POST["director"]
        review.leadActor = request.POST["leadActor"]
        review.genre = request.POST["genre"]
        review.rating = float(request.POST["rating"])
        review.runningTime = int(request.POST["runningTime"])
        review.releaseYear = int(request.POST["releaseYear"])
        review.content = request.POST["content"]
        review.image_url = request.POST["imageURL"]
        review.save()
        return redirect("reviews:read", pk=review.id)
    context = { "review" : review }
    return render(request, "reviews_update.html", {
        "review": review,
        "genre_choices": Review.GENRE_CHOICES
    })

def reviews_delete(request,pk):
    if request.method == "POST":
        review = Review.objects.get(id=pk)
        review.delete()
    return redirect("reviews:reviews_list")

