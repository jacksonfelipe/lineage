from django import forms
from apps.lineage.games.models import *
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import FilteredSelectMultiple


class BoxTypeAdminForm(forms.ModelForm):
    class Meta:
        model = BoxType
        fields = '__all__'

    allowed_items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Itens Permitidos", is_stacked=False)
    )


class BoxTypeForm(forms.ModelForm):

    allowed_items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Itens Permitidos", is_stacked=False)
    )

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',),
        }
        js = ('/admin/jsi18n',)
        
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
            'max_epic_items',
            'max_legendary_items',
            'allowed_items',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'boosters_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'chance_common': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_rare': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_epic': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_legendary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'max_epic_items': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_legendary_items': forms.NumberInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'name': 'Nome da Caixa',
            'price': 'Preço (R$)',
            'boosters_amount': 'Quantidade de Boosters',
            'chance_common': 'Chance Comum (%)',
            'chance_rare': 'Chance Rara (%)',
            'chance_epic': 'Chance Épica (%)',
            'chance_legendary': 'Chance Lendária (%)',
            'max_epic_items': 'Máximo de Itens Épicos',
            'max_legendary_items': 'Máximo de Itens Lendários',
            'allowed_items': 'Itens Permitidos',
        }

    def clean(self):
        cleaned_data = super().clean()
        chance_common = cleaned_data.get('chance_common', 0)
        chance_rare = cleaned_data.get('chance_rare', 0)
        chance_epic = cleaned_data.get('chance_epic', 0)
        chance_legendary = cleaned_data.get('chance_legendary', 0)

        total_chance = chance_common + chance_rare + chance_epic + chance_legendary
        if total_chance != 100:
            raise ValidationError("A soma das chances deve ser exatamente 100%. Soma atual: {}".format(total_chance))

        return cleaned_data


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
        fields = ['name', 'enchant', 'item_id', 'image', 'description', 'rarity', 'can_be_populated']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'enchant': forms.NumberInput(attrs={'class': 'form-control'}),
            'item_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rarity': forms.Select(attrs={'class': 'form-control'}),
            'can_be_populated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nome do Item',
            'enchant': 'Enchant',
            'item_id': 'ID do Item',
            'image': 'Imagem',
            'description': 'Descrição',
            'rarity': 'Raridade',
            'can_be_populated': 'Pode ser populado em caixas',
        }
