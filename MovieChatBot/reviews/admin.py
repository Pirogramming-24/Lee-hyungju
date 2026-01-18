# reviews/admin.py
from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "title")  # 목록에서 보이게
    # search_fields = ("")  # 있으면 편함
