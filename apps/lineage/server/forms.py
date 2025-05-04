from django import forms
from .models import Apoiador


class ApoiadorForm(forms.ModelForm):
    class Meta:
        model = Apoiador
        fields = ['nome_publico', 'descricao', 'link_twitch', 'link_youtube', 'imagem']
