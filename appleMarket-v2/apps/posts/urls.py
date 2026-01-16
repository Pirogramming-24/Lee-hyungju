from django.urls import path
from .views import *
from . import views_api

app_name = 'posts'

urlpatterns = [
    path('', main, name='main'),
    path('create', create, name='create'),
    path('detail/<int:pk>', detail, name='detail'),
    path('update/<int:pk>', update, name='update'),
    path('delete/<int:pk>', delete, name='delete'),
    path("api/nutrition-ocr/", views_api.nutrition_ocr_create),
    path("api/nutrition-ocr/<int:job_id>/", views_api.nutrition_ocr_status),
]