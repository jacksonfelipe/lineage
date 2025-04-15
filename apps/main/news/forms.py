from django import forms
from .models import News, NewsTranslation
from django_ckeditor_5.widgets import CKEditor5Widget


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['slug', 'image', 'is_published', 'is_private']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class NewsTranslationForm(forms.ModelForm):
    class Meta:
        model = NewsTranslation
        fields = ['language', 'title', 'content', 'summary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name="extends"),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        language = kwargs.pop('language', None)
        super(NewsTranslationForm, self).__init__(*args, **kwargs)
        if language:
            self.fields['language'].initial = language
