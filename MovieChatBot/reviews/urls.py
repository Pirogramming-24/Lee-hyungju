from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    # path('', views.test, name="test")
    path('', views.review_list, name="review_list"),
    # path('', views.index, name="review_list"),
    path('<int:pk>/', views.review_detail, name="detail"),
    
    path('create/', views.review_create, name="create"),
    path('create/search/', views.review_create_search, name="create_search"),
    
    path('<int:pk>/update/', views.review_update, name="update"),
    path('<int:pk>/delete/', views.review_delete, name="delete"),
]