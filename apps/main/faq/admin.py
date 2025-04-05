from django import forms
from django.contrib import admin
from .models import FAQ
from core.admin import BaseModelAdmin

class FAQAdminForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = '__all__'
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pergunta'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Resposta'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ordem'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

@admin.register(FAQ)
class FAQAdmin(BaseModelAdmin):
    form = FAQAdminForm
    list_display = ('question', 'order', 'is_public')
    ordering = ('order',)
    list_filter = ('is_public',)
    search_fields = ('question',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pergunta'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Resposta'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ordem'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Ensure is_public field is included
        }
        return super().get_form(request, obj, **kwargs)
