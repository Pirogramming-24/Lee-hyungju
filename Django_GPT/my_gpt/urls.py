from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.main, name="main"),
    path("api/chat/", views.chat, name="chat"),

    path("login/", auth_views.LoginView.as_view(template_name="my_gpt/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
]