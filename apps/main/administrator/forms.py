from django import forms
from django.core.exceptions import ValidationError
from .models import Theme


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = '__all__'

    def clean_upload(self):
        upload = self.cleaned_data.get('upload')
        if upload:
            temp_theme = Theme(upload=upload)
            return temp_theme.clean_upload()
        return upload

    def clean(self):
        cleaned_data = super().clean()
        ativo = cleaned_data.get('ativo')

        if ativo:
            active_themes = Theme.objects.filter(ativo=True)
            if self.instance.pk:
                active_themes = active_themes.exclude(pk=self.instance.pk)

            if active_themes.exists():
                raise ValidationError("Já existe um tema ativo. Desative o tema atual antes de ativar outro.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.upload:
            instance.processar_upload()

        if commit:
            instance.save()

        return instance
