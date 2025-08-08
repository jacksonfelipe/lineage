from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, UserProfile, Hashtag, Report, ModerationAction, ContentFilter
from django.contrib.auth import get_user_model


class PostForm(forms.ModelForm):
    """Formulário para criação de posts"""
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('O que você está pensando?'),
            'maxlength': 1000,
            'required': 'required'
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
            # Verificar se é um novo upload (tem content_type) ou arquivo existente
            if hasattr(image, 'content_type'):
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
            # Verificar se é um novo upload (tem content_type) ou arquivo existente
            if hasattr(video, 'content_type'):
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
            # Verificar se é um novo upload (tem content_type) ou arquivo existente
            if hasattr(image, 'content_type'):
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

    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'cover_image', 'website', 'location',
            'birth_date', 'phone', 'gender', 'interests',
            'is_private', 'show_email', 'show_phone', 'allow_messages'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Conte um pouco sobre você...'),
                'maxlength': 500
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://seusite.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Sua cidade, país')
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Seu telefone')
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'interests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Seus hobbies e interesses...')
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_phone': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_messages': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'bio': _('Máximo 500 caracteres'),
            'avatar': _('Foto de perfil (JPG, PNG)'),
            'cover_image': _('Imagem de capa (JPG, PNG)'),
            'website': _('Link para seu site pessoal'),
            'interests': _('Conte sobre seus interesses'),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Verificar se é um novo upload (tem content_type) ou arquivo existente
            if hasattr(avatar, 'content_type'):
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
            # Verificar se é um novo upload (tem content_type) ou arquivo existente
            if hasattr(cover_image, 'content_type'):
                # Verificar tamanho do arquivo (máximo 5MB)
                if cover_image.size > 5 * 1024 * 1024:
                    raise forms.ValidationError(_('A imagem de capa deve ter no máximo 5MB.'))

                # Verificar formato
                allowed_formats = ['image/jpeg', 'image/png']
                if cover_image.content_type not in allowed_formats:
                    raise forms.ValidationError(_('Formato de imagem não suportado. Use JPG ou PNG.'))

        return cover_image


class SearchForm(forms.Form):
    """Formulário de busca"""
    q = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Buscar usuários, posts...'),
            'aria-label': _('Buscar')
        }),
        label=_('Buscar'),
        required=False
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
            name = name.strip().lstrip('#')
            # Validar formato
            if not name.replace('_', '').replace('-', '').isalnum():
                raise forms.ValidationError(_('Nome da hashtag deve conter apenas letras, números, hífens e underscores.'))
        return name


# ============================================================================
# FORMULÁRIOS DE MODERAÇÃO
# ============================================================================

class ReportForm(forms.ModelForm):
    """Formulário para criação de denúncias"""
    report_type = forms.ChoiceField(
        choices=Report.REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'report-type'
        }),
        label=_('Tipo de Denúncia')
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Descreva o problema encontrado...'),
            'maxlength': 1000
        }),
        max_length=1000,
        label=_('Descrição'),
        help_text=_('Máximo 1000 caracteres')
    )

    class Meta:
        model = Report
        fields = ['report_type', 'description']
        exclude = [
            'reporter', 'status', 'reported_post', 'reported_comment',
            'reported_user', 'assigned_moderator', 'moderator_notes',
            'resolved_at', 'priority', 'similar_reports_count'
        ]

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise forms.ValidationError(_('A descrição é obrigatória.'))
        return description.strip()


class ModerationActionForm(forms.ModelForm):
    """Formulário para ações de moderação"""
    action_type = forms.ChoiceField(
        choices=ModerationAction.ACTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'action-type'
        }),
        label=_('Tipo de Ação')
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Justificativa para a ação...'),
            'maxlength': 500
        }),
        max_length=500,
        label=_('Motivo'),
        help_text=_('Máximo 500 caracteres')
    )

    # Campos condicionais para suspensões
    suspension_duration = forms.DurationField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1 day, 2 hours, 30 minutes',
            'id': 'suspension-duration'
        }),
        label=_('Duração da Suspensão'),
        help_text=_('Ex: 1 day, 2 hours, 30 minutes')
    )
    suspension_type = forms.ChoiceField(
        choices=ModerationAction.SUSPENSION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'suspension-type'
        }),
        label=_('Tipo de Suspensão')
    )

    # Notificação
    notify_user = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'notify-user'
        }),
        label=_('Notificar Usuário')
    )
    notification_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Mensagem personalizada para o usuário...'),
            'maxlength': 500,
            'id': 'notification-message'
        }),
        max_length=500,
        label=_('Mensagem de Notificação'),
        help_text=_('Mensagem opcional para o usuário (máx. 500 caracteres)')
    )

    class Meta:
        model = ModerationAction
        fields = [
            'action_type', 'reason', 'suspension_duration', 'suspension_type',
            'notify_user', 'notification_message'
        ]
        exclude = [
            'moderator', 'target_post', 'target_comment', 'target_user',
            'suspension_end_date', 'is_active', 'expires_at'
        ]

    def clean(self):
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        suspension_duration = cleaned_data.get('suspension_duration')
        suspension_type = cleaned_data.get('suspension_type')

        # Validar campos de suspensão
        if action_type in ['suspend_user', 'restrict_user']:
            if not suspension_duration:
                raise forms.ValidationError(_('Duração da suspensão é obrigatória para este tipo de ação.'))
            if not suspension_type:
                raise forms.ValidationError(_('Tipo de suspensão é obrigatório para este tipo de ação.'))

        return cleaned_data


class ContentFilterForm(forms.ModelForm):
    """Formulário para filtros de conteúdo"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome do filtro')
        }),
        label=_('Nome do Filtro')
    )
    filter_type = forms.ChoiceField(
        choices=ContentFilter.FILTER_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filter-type'
        }),
        label=_('Tipo de Filtro')
    )
    pattern = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Padrão a ser filtrado...'),
            'id': 'filter-pattern'
        }),
        label=_('Padrão'),
        help_text=_('Palavra-chave, regex ou padrão a ser filtrado')
    )
    action = forms.ChoiceField(
        choices=ContentFilter.ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filter-action'
        }),
        label=_('Ação')
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Descrição do filtro...')
        }),
        label=_('Descrição')
    )

    # Campos de controle
    case_sensitive = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Sensível a Maiúsculas/Minúsculas')
    )
    apply_to_posts = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Aplicar a Posts')
    )
    apply_to_comments = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Aplicar a Comentários')
    )
    apply_to_usernames = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Aplicar a Nomes de Usuário')
    )

    class Meta:
        model = ContentFilter
        fields = [
            'name', 'filter_type', 'pattern', 'action', 'description',
            'case_sensitive', 'apply_to_posts', 'apply_to_comments', 'apply_to_usernames'
        ]
        exclude = ['is_active', 'matches_count', 'last_matched']

    def clean_pattern(self):
        pattern = self.cleaned_data.get('pattern')
        filter_type = self.cleaned_data.get('filter_type')

        if not pattern or pattern.strip() == '':
            raise forms.ValidationError(_('O padrão é obrigatório.'))

        # Validar regex se for do tipo regex
        if filter_type == 'regex':
            import re
            try:
                re.compile(pattern)
            except re.error as e:
                raise forms.ValidationError(_(f'Expressão regular inválida: {e}'))

        return pattern.strip()

    def clean(self):
        cleaned_data = super().clean()
        apply_to_posts = cleaned_data.get('apply_to_posts')
        apply_to_comments = cleaned_data.get('apply_to_comments')
        apply_to_usernames = cleaned_data.get('apply_to_usernames')

        # Pelo menos um tipo de conteúdo deve ser selecionado
        if not any([apply_to_posts, apply_to_comments, apply_to_usernames]):
            raise forms.ValidationError(_('Selecione pelo menos um tipo de conteúdo para aplicar o filtro.'))

        return cleaned_data


class SearchReportForm(forms.Form):
    """Formulário para busca de denúncias"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Buscar denúncias...'),
            'autocomplete': 'off'
        }),
        label=_('Buscar')
    )
    report_type = forms.ChoiceField(
        choices=[('', _('Todos os tipos'))] + Report.REPORT_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Tipo de Denúncia')
    )
    status = forms.ChoiceField(
        choices=[('', _('Todos os status'))] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Status')
    )
    priority = forms.ChoiceField(
        choices=[
            ('', _('Todas as prioridades')),
            ('low', _('Baixa')),
            ('medium', _('Média')),
            ('high', _('Alta')),
            ('urgent', _('Urgente')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Prioridade')
    )
    assigned_moderator = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(is_staff=True),
        required=False,
        empty_label=_('Todos os moderadores'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Moderador Responsável')
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('Data Inicial')
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('Data Final')
    )


class BulkModerationForm(forms.Form):
    """Formulário para ações em massa de moderação"""
    action_type = forms.ChoiceField(
        choices=[
            ('', _('Selecione uma ação')),
            ('hide_content', _('Ocultar Conteúdo')),
            ('delete_content', _('Deletar Conteúdo')),
            ('warn', _('Enviar Advertência')),
            ('assign_moderator', _('Atribuir Moderador')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'bulk-action-type'
        }),
        label=_('Ação em Massa')
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Motivo para a ação em massa...'),
            'maxlength': 500
        }),
        max_length=500,
        label=_('Motivo'),
        help_text=_('Motivo opcional para a ação (máx. 500 caracteres)')
    )
    assigned_moderator = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(is_staff=True),
        required=False,
        empty_label=_('Selecione um moderador'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Atribuir a Moderador')
    )

    def clean(self):
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        assigned_moderator = cleaned_data.get('assigned_moderator')

        if action_type == 'assign_moderator' and not assigned_moderator:
            raise forms.ValidationError(_('Selecione um moderador para atribuir.'))

        return cleaned_data
