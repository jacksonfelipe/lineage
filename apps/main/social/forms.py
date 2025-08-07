from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, UserProfile, Hashtag


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
    video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*'
        }),
        help_text=_('Vídeo opcional (MP4, AVI, MOV - máx. 50MB)')
    )
    link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://exemplo.com'
        }),
        help_text=_('Link opcional para compartilhar')
    )
    hashtags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '#hashtag1 #hashtag2'
        }),
        help_text=_('Hashtags separadas por espaço (ex: #tecnologia #programacao)')
    )

    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'link', 'is_public']
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

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            # Verificar tamanho do arquivo (máximo 50MB)
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError(_('O vídeo deve ter no máximo 50MB.'))
            
            # Verificar formato
            allowed_formats = ['video/mp4', 'video/avi', 'video/quicktime']
            if video.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato de vídeo não suportado. Use MP4, AVI ou MOV.'))
        
        return video

    def clean_hashtags(self):
        hashtags = self.cleaned_data.get('hashtags', '')
        if hashtags:
            # Processar hashtags
            hashtag_list = []
            for tag in hashtags.split():
                if tag.startswith('#'):
                    tag = tag[1:]  # Remover #
                if tag:
                    hashtag_list.append(tag.lower())
            return hashtag_list
        return []


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
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_('Imagem opcional no comentário')
    )

    class Meta:
        model = Comment
        fields = ['content', 'image']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or content.strip() == '':
            raise forms.ValidationError(_('O comentário não pode estar vazio.'))
        return content.strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Verificar tamanho do arquivo (máximo 2MB)
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError(_('A imagem deve ter no máximo 2MB.'))
            
            # Verificar formato
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif']
            if image.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato de imagem não suportado. Use JPG, PNG ou GIF.'))
        
        return image


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
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Seu telefone')
        })
    )
    interests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Seus hobbies e interesses...')
        }),
        help_text=_('Conte sobre seus interesses')
    )
    # Links sociais
    facebook = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://facebook.com/seuperfil'
        })
    )
    twitter = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://twitter.com/seuperfil'
        })
    )
    instagram = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://instagram.com/seuperfil'
        })
    )
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/seuperfil'
        })
    )
    youtube = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://youtube.com/@seucanal'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'cover_image', 'website', 'location', 
            'phone', 'gender', 'interests', 'birth_date',
            'is_private', 'show_email', 'show_phone', 'allow_messages'
        ]
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Verificar tamanho do arquivo (máximo 2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError(_('A foto de perfil deve ter no máximo 2MB.'))
            
            # Verificar formato
            allowed_formats = ['image/jpeg', 'image/png']
            if avatar.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato de imagem não suportado. Use JPG ou PNG.'))
        
        return avatar

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            # Verificar tamanho do arquivo (máximo 5MB)
            if cover_image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('A imagem de capa deve ter no máximo 5MB.'))
            
            # Verificar formato
            allowed_formats = ['image/jpeg', 'image/png']
            if cover_image.content_type not in allowed_formats:
                raise forms.ValidationError(_('Formato de imagem não suportado. Use JPG ou PNG.'))
        
        return cover_image

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Processar links sociais
        social_links = {}
        for field in ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']:
            value = self.cleaned_data.get(field)
            if value:
                social_links[field] = value
        
        instance.social_links = social_links
        
        if commit:
            instance.save()
        return instance


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
            ('posts', _('Posts')),
            ('hashtags', _('Hashtags')),
        ],
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    date_filter = forms.ChoiceField(
        choices=[
            ('all', _('Qualquer data')),
            ('today', _('Hoje')),
            ('week', _('Esta semana')),
            ('month', _('Este mês')),
            ('year', _('Este ano')),
        ],
        initial='all',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class ShareForm(forms.Form):
    """Formulário para compartilhamento de posts"""
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Adicione um comentário ao compartilhar...'),
            'maxlength': 500
        }),
        max_length=500,
        help_text=_('Comentário opcional (máx. 500 caracteres)')
    )
    is_public = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text=_('Compartilhar publicamente')
    )


class ReactionForm(forms.Form):
    """Formulário para reações em posts"""
    reaction_type = forms.ChoiceField(
        choices=[
            ('like', '👍 Curtir'),
            ('love', '❤️ Amar'),
            ('haha', '😂 Haha'),
            ('wow', '😮 Uau'),
            ('sad', '😢 Triste'),
            ('angry', '😠 Bravo'),
        ],
        initial='like',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class HashtagForm(forms.ModelForm):
    """Formulário para criação/edição de hashtags"""
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'nome_da_hashtag'
        }),
        help_text=_('Nome da hashtag (sem #)')
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Descrição da hashtag...')
        })
    )

    class Meta:
        model = Hashtag
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Remover # se presente
            if name.startswith('#'):
                name = name[1:]
            # Converter para minúsculas
            name = name.lower()
            # Remover espaços e caracteres especiais
            name = ''.join(c for c in name if c.isalnum() or c == '_')
        return name
