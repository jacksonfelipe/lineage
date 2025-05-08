from django import forms
from apps.lineage.games.models import *


class BoxTypeForm(forms.ModelForm):
    class Meta:
        model = BoxType
        fields = [
            'name',
            'price',
            'boosters_amount',
            'chance_common',
            'chance_rare',
            'chance_epic',
            'chance_legendary',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'boosters_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'chance_common': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_rare': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_epic': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_legendary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
        labels = {
            'name': 'Nome da Caixa',
            'price': 'Preço (R$)',
            'boosters_amount': 'Quantidade de Boosters',
            'chance_common': 'Chance Comum (%)',
            'chance_rare': 'Chance Rara (%)',
            'chance_epic': 'Chance Épica (%)',
            'chance_legendary': 'Chance Lendária (%)',
        }


class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['user', 'box_type']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'box_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'Usuário',
            'box_type': 'Tipo de Caixa',
        }


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'enchant', 'item_id', 'image', 'description', 'rarity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'enchant': forms.NumberInput(attrs={'class': 'form-control'}),
            'item_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rarity': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nome do Item',
            'enchant': 'Enchant',
            'item_id': 'ID do Item',
            'image': 'Imagem',
            'description': 'Descrição',
            'rarity': 'Raridade',
        }
