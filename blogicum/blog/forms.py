from .models import Post
from django.forms import ModelForm, TextInput, Textarea, DateInput, Select


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "pub_date", "author"]
        widgets = {
            "title": TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите название',
                }
            ),
            "text": Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите описание',
                }
            ),
            "pub_date": DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            "author": Select(
                attrs={
                    'class': 'form-control',
                }
            ),
        }