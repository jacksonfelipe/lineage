from django import forms
from .models import ShopItem, ShopPackage, PromotionCode


class ShopItemForm(forms.ModelForm):
    class Meta:
        model = ShopItem
        fields = ['nome', 'item_id', 'preco', 'quantidade', 'ativo']


class ShopPackageForm(forms.ModelForm):
    class Meta:
        model = ShopPackage
        fields = ['nome', 'preco_total', 'itens', 'ativo', 'promocao']


class PromotionCodeForm(forms.ModelForm):
    class Meta:
        model = PromotionCode
        fields = ['codigo', 'desconto_percentual', 'validade', 'ativo']
