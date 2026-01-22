# posts/forms.py
from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": "내용을 입력하세요"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(attrs={"placeholder": "댓글을 입력하세요"}),
        }

class StoryUploadForm(forms.Form):
    images = forms.ImageField(required=True) 
