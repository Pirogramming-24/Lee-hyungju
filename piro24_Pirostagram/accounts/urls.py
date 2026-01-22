# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("search/", views.user_search, name="search"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("edit/", views.profile_edit, name="profile_edit"),  
]
