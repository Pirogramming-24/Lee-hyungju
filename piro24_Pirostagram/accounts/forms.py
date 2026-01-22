# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import User

class SignupForm(UserCreationForm):
    name = forms.CharField(required=False, max_length=30)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("username", "name", "bio", "profile_pic")

class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(UserChangeForm):
    password = None  # 비밀번호 필드 제거

    class Meta:
        model = User
        fields = ("name", "bio", "profile_pic")
