# posts/urls.py
from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("", views.feed, name="feed"),

    path("create/", views.post_create, name="post_create"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    path("<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("images/<int:image_id>/delete/", views.post_image_delete, name="post_image_delete"),
    
    path("<int:post_id>/like/", views.post_like_toggle, name="post_like_toggle"),

    path("comments/<int:comment_id>/edit/", views.comment_edit, name="comment_edit"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),

    path("stories/", views.story_list, name="story_list"),
    path("stories/create/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/", views.story_detail, name="story_detail"),
    path("stories/items/<int:item_id>/delete/", views.story_item_delete, name="story_item_delete"),

]
