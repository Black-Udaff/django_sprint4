from .models import Post, User
from django.forms import ModelForm, TextInput, Textarea, DateInput, Select
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = "__all__"
        exclude = ('author',)
        widgets = {'pub_date': forms.DateInput(attrs={'type': 'date'})}