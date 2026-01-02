from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "ideas"

urlpatterns = [
    path("", views.ideas_list, name="ideas_list"),
    # path("idea/", views.idea_list, name="idea_list"),

    path("idea/create/", views.idea_create, name="idea_create"),
    path("idea/<int:pk>/", views.idea_detail, name="idea_detail"),
    path("idea/<int:pk>/update/", views.idea_update, name="idea_update"),
    path("idea/<int:pk>/delete/", views.idea_delete, name="idea_delete"),

    path("devtool/", views.devtool_list, name="devtool_list"),
    path("devtool/create/", views.devtool_create, name="devtool_create"),
    path("devtool/<int:pk>/", views.devtool_detail, name="devtool_detail"),
    path("devtool/<int:pk>/update/", views.devtool_update, name="devtool_update"),
    path("devtool/<int:pk>/delete/", views.devtool_delete, name="devtool_delete"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )