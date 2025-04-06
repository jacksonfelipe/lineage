from django import forms
from .models import News
from django_ckeditor_5.widgets import CKEditor5Widget

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'slug', 'content', 'image', 'is_published', 'is_private', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }
