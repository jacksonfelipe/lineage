from django import forms
from .models import ShopItem, ShopPackage, PromotionCode


class ShopItemForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do item'})
    )
    item_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID do item'})
    )
    preco = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço'})
    )
    quantidade = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade'})
    )
    ativo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = ShopItem
        fields = ['nome', 'item_id', 'preco', 'quantidade', 'ativo']


class ShopPackageForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do pacote'})
    )
    preco_total = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço total'})
    )
    itens = forms.ModelMultipleChoiceField(
        queryset=ShopItem.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    ativo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    promocao = forms.ModelChoiceField(
        queryset=PromotionCode.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ShopPackage
        fields = ['nome', 'preco_total', 'itens', 'ativo', 'promocao']


class PromotionCodeForm(forms.ModelForm):
    codigo = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código promocional'})
    )
    desconto_percentual = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Desconto (%)'})
    )
    validade = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'AAAA-MM-DD HH:MM'})
    )
    ativo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = PromotionCode
        fields = ['codigo', 'desconto_percentual', 'validade', 'ativo']
