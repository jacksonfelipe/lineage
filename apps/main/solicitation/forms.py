from django import forms
from .models import Solicitation


class SolicitationForm(forms.ModelForm):
    class Meta:
        model = Solicitation
        fields = []  # Nenhum campo visível, o usuário será atribuído automaticamente
