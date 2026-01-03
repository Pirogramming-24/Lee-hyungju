from django.contrib import admin
from .models import Idea,DevTool

# Register your models here.
@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("id","title")
    search_fields = ["title",]

@admin.register(DevTool)
class DevToolAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ["title",]