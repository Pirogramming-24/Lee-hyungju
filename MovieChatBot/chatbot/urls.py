from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_page, name="page"),
    path("api/", views.chat_api, name="api"),
]
