from django import forms
from .models import Theme
import zipfile


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = '__all__'  # Inclui todos os campos do modelo no formulário

    def clean_upload(self):
        # Verifica se o arquivo de upload existe e é válido
        file = self.cleaned_data.get('upload')
        
        if file:
            # Limita o tamanho do arquivo para 10MB
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("O arquivo é muito grande. Tente um arquivo menor.")
            
            # Verifica se o arquivo é um arquivo ZIP válido
            if not zipfile.is_zipfile(file):
                raise forms.ValidationError("O arquivo não é um arquivo ZIP válido.")
        
        return file
