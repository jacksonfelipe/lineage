from django import forms
from .models import ShopItem, ShopPackage, PromotionCode


class ShopItemForm(forms.ModelForm):
    class Meta:
        model = ShopItem
        fields = ['nome', 'item_id', 'preco', 'quantidade', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do item'}),
            'item_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID do item'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ShopPackageForm(forms.ModelForm):
    class Meta:
        model = ShopPackage
        fields = ['nome', 'preco_total', 'ativo', 'promocao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do pacote'}),
            'preco_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço total'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocao': forms.Select(attrs={'class': 'form-control'}),
        }


class PromotionCodeForm(forms.ModelForm):
    validade = forms.DateTimeField(
        label="Validade",
        required=False,
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': 'Ex: 2025-04-30 18:00'
            }
        )
    )

    class Meta:
        model = PromotionCode
        fields = ['codigo', 'desconto_percentual', 'validade', 'ativo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código promocional'}),
            'desconto_percentual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Desconto (%)'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
