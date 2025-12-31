from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    # path('', views.test, name="test")
    path('', views.reviews_list, name="reviews_list"),
    path('<int:pk>/', views.reviews_read, name="read"),
    path('create/', views.reviews_create, name="create"),
    path('<int:pk>/update/', views.reviews_update, name="update"),
    path('<int:pk>/delete/', views.reviews_delete, name="delete"),
]