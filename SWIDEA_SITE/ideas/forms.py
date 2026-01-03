from django import forms
from .models import Idea, DevTool

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["title", "devtool", "image", "content",]
        labels = {
            "title": "제목",
            "devtool": "개발 도구",
            "image": "이미지",
            "content": "내용",
        }

class DevToolForm(forms.ModelForm):
    class Meta:
        model = DevTool
        fields = ["name", "kind", "content",]
        labels = {
            "name": "도구 이름",
            "kind": "분류",
            "content": "내용",
        }