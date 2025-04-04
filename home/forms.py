from django.contrib.auth.forms import UserChangeForm
from django import forms
from .models import *


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'bio', 'cpf', 'gender')  # Incluindo o campo 'genero'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})
        for fieldname in ['first_name', 'last_name', 'email', 'bio', 'gender']:  # Incluindo 'genero' no loop
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
        self.fields['cpf'].widget.attrs.update({'class': 'form-control', 'id': 'cpf'})



class AddressUserForm(forms.ModelForm):
    class Meta:
        model = AddressUser
        fields = ['street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code']
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
