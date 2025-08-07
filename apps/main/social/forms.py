from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, UserProfile


class PostForm(forms.ModelForm):
    """Formulário para criação de posts"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('O que você está pensando?'),
            'maxlength': 1000
        }),
        max_length=1000,
        help_text=_('Máximo 1000 caracteres')
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_('Imagem opcional (JPG, PNG, GIF)')
    )

    class Meta:
        model = Post
        fields = ['content', 'image', 'is_public']
        widgets = {
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or content.strip() == '':
            raise forms.ValidationError(_('O conteúdo não pode estar vazio.'))
        return content.strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Verificar tamanho do arquivo (máximo 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('A imagem deve ter no máximo 5MB.'))
            
            # Verificar formato
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif']
            if image.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato de imagem não suportado. Use JPG, PNG ou GIF.'))
        
        return image


class CommentForm(forms.ModelForm):
    """Formulário para comentários"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Escreva um comentário...'),
            'maxlength': 500
        }),
        max_length=500,
        help_text=_('Máximo 500 caracteres')
    )

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or content.strip() == '':
            raise forms.ValidationError(_('O comentário não pode estar vazio.'))
        return content.strip()


class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil social"""
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Conte um pouco sobre você...'),
            'maxlength': 500
        }),
        max_length=500,
        required=False,
        help_text=_('Máximo 500 caracteres')
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_('Foto de perfil (JPG, PNG)')
    )
    cover_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_('Imagem de capa (JPG, PNG)')
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://seusite.com'
        }),
        help_text=_('Link para seu site pessoal')
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Sua cidade, país')
        })
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text=_('Data de nascimento (opcional)')
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'cover_image', 'website', 'location', 'birth_date', 'is_private']
        widgets = {
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError(_('A foto de perfil deve ter no máximo 2MB.'))
            
            allowed_formats = ['image/jpeg', 'image/png']
            if avatar.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato não suportado. Use JPG ou PNG.'))
        
        return avatar

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            if cover_image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(_('A imagem de capa deve ter no máximo 5MB.'))
            
            allowed_formats = ['image/jpeg', 'image/png']
            if cover_image.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato não suportado. Use JPG ou PNG.'))
        
        return cover_image


class SearchForm(forms.Form):
    """Formulário para busca de usuários e posts"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Buscar usuários ou posts...'),
            'autocomplete': 'off'
        })
    )
    search_type = forms.ChoiceField(
        choices=[
            ('all', _('Tudo')),
            ('users', _('Usuários')),
            ('posts', _('Posts'))
        ],
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
