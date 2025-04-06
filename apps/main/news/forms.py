from django import forms
from .models import News
from ckeditor.widgets import CKEditorWidget

class NewsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = News
        fields = ['title', 'slug', 'content', 'image', 'is_published', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
