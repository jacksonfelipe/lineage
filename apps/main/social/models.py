from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from utils.media_validators import (
    validate_social_media_image, validate_social_media_video, 
    validate_avatar_image, process_image_for_social_media,
    process_avatar_image, create_image_thumbnail
)
import os

User = get_user_model()


class Post(BaseModel):
    """Modelo para posts da rede social"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_posts',
        verbose_name=_('Autor')
    )
    content = models.TextField(
        verbose_name=_('Conteúdo'),
        help_text=_('Conteúdo do post')
    )
    image = models.ImageField(
        upload_to='social/posts/',
        blank=True,
        null=True,
        verbose_name=_('Imagem'),
        help_text=_('Imagem opcional para o post (máx. 10MB, 1920x1080px)'),
        validators=[validate_social_media_image]
    )
    # Novos campos para melhorar a rede social
    video = models.FileField(
        upload_to='social/videos/',
        blank=True,
        null=True,
        verbose_name=_('Vídeo'),
        help_text=_('Vídeo opcional para o post (máx. 100MB, 5min, MP4/MOV/AVI/WEBM)'),
        validators=[validate_social_media_video]
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Link'),
        help_text=_('Link opcional para o post')
    )
    link_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Título do link'),
        help_text=_('Título para o link compartilhado')
    )
    link_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição do link'),
        help_text=_('Descrição para o link compartilhado')
    )
    link_image = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Imagem do link'),
        help_text=_('URL da imagem do link compartilhado')
    )
    # Campos de engajamento
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de visualizações')
    )
    shares_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de compartilhamentos')
    )
    # Campos de privacidade e moderação
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Público'),
        help_text=_('Se marcado, o post será visível para todos')
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name=_('Fixado'),
        help_text=_('Se marcado, o post ficará fixado no topo do perfil')
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_('Editado'),
        help_text=_('Indica se o post foi editado')
    )
    edited_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data da última edição')
    )
    # Contadores
    likes_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de curtidas')
    )
    comments_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de comentários')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Data de atualização')
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"Post de {self.author.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def update_counts(self):
        """Atualiza contadores de likes, comentários e compartilhamentos"""
        self.likes_count = self.likes.count()
        self.comments_count = self.comments.count()
        self.shares_count = self.shares.count()
        self.save(update_fields=['likes_count', 'comments_count', 'shares_count'])

    def increment_views(self):
        """Incrementa o contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def mark_as_edited(self):
        """Marca o post como editado"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['is_edited', 'edited_at'])

    @property
    def engagement_rate(self):
        """Calcula a taxa de engajamento do post"""
        total_interactions = self.likes_count + self.comments_count + self.shares_count
        if self.views_count > 0:
            return (total_interactions / self.views_count) * 100
        return 0

    @property
    def has_media(self):
        """Verifica se o post tem mídia (imagem ou vídeo)"""
        return bool(self.image or self.video)

    @property
    def has_link(self):
        """Verifica se o post tem link"""
        return bool(self.link)
    
    def is_liked_by(self, user):
        """Verifica se um usuário específico deu like no post"""
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def save(self, *args, **kwargs):
        """Override save para processar mídia automaticamente"""
        # Processar imagem se foi alterada
        if self.image and hasattr(self.image, 'file'):
            try:
                # Processar imagem para otimização
                processed_path = process_image_for_social_media(
                    self.image.path if hasattr(self.image, 'path') else self.image.file,
                    max_width=1920,
                    max_height=1080,
                    quality=85
                )
            except Exception:
                pass  # Se falhar, manter imagem original
        
        super().save(*args, **kwargs)


class Comment(BaseModel):
    """Modelo para comentários nos posts"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Post')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_comments',
        verbose_name=_('Autor')
    )
    content = models.TextField(
        verbose_name=_('Conteúdo'),
        help_text=_('Conteúdo do comentário')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='replies',
        verbose_name=_('Comentário pai'),
        help_text=_('Para respostas a outros comentários')
    )
    # Novos campos para comentários
    image = models.ImageField(
        upload_to='social/comments/',
        blank=True,
        null=True,
        verbose_name=_('Imagem'),
        help_text=_('Imagem opcional no comentário (máx. 5MB)'),
        validators=[validate_social_media_image]
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de curtidas')
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_('Editado')
    )
    edited_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data da edição')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.author.username} em {self.post}"

    def update_likes_count(self):
        """Atualiza contador de likes do comentário"""
        self.likes_count = self.comment_likes.count()
        self.save(update_fields=['likes_count'])

    def mark_as_edited(self):
        """Marca o comentário como editado"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['is_edited', 'edited_at'])


class CommentLike(BaseModel):
    """Modelo para curtidas nos comentários"""
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='comment_likes',
        verbose_name=_('Comentário')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_comment_likes',
        verbose_name=_('Usuário')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Curtida de Comentário')
        verbose_name_plural = _('Curtidas de Comentários')
        unique_together = ['comment', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Curtida de {self.user.username} em comentário de {self.comment.author.username}"


class Like(BaseModel):
    """Modelo para curtidas nos posts"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('Post')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_likes',
        verbose_name=_('Usuário')
    )
    # Novo campo para tipos de reação
    reaction_type = models.CharField(
        max_length=20,
        choices=[
            ('like', '👍 Curtir'),
            ('love', '❤️ Amar'),
            ('haha', '😂 Haha'),
            ('wow', '😮 Uau'),
            ('sad', '😢 Triste'),
            ('angry', '😠 Bravo'),
        ],
        default='like',
        verbose_name=_('Tipo de reação')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Curtida')
        verbose_name_plural = _('Curtidas')
        unique_together = ['post', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_reaction_type_display()} de {self.user.username} em {self.post}"


class Share(BaseModel):
    """Modelo para compartilhamentos de posts"""
    original_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name=_('Post original')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_shares',
        verbose_name=_('Usuário que compartilhou')
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Comentário no compartilhamento'),
        help_text=_('Comentário opcional ao compartilhar')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Compartilhamento')
        verbose_name_plural = _('Compartilhamentos')
        ordering = ['-created_at']

    def __str__(self):
        return f"Compartilhamento de {self.user.username} do post de {self.original_post.author.username}"


class Follow(BaseModel):
    """Modelo para seguir usuários"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Seguidor')
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name=_('Seguindo')
    )
    # Novo campo para notificações
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Notificações ativadas'),
        help_text=_('Receber notificações de posts deste usuário')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Seguir')
        verbose_name_plural = _('Seguir')
        unique_together = ['follower', 'following']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} segue {self.following.username}"


class UserProfile(BaseModel):
    """Perfil estendido do usuário para rede social"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='social_profile',
        verbose_name=_('Usuário')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Biografia'),
        help_text=_('Breve descrição sobre você')
    )
    avatar = models.ImageField(
        upload_to='social/avatars/',
        blank=True,
        null=True,
        verbose_name=_('Avatar'),
        help_text=_('Foto de perfil (máx. 5MB, será redimensionada para 400x400px)'),
        validators=[validate_avatar_image]
    )
    cover_image = models.ImageField(
        upload_to='social/covers/',
        blank=True,
        null=True,
        verbose_name=_('Imagem de capa'),
        help_text=_('Imagem de capa do perfil (máx. 10MB, recomendado: 1200x400px)'),
        validators=[validate_social_media_image]
    )
    website = models.URLField(
        blank=True,
        verbose_name=_('Website'),
        help_text=_('Link para seu site pessoal')
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Localização'),
        help_text=_('Sua cidade/país')
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Data de nascimento')
    )
    # Novos campos para melhorar o perfil
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Telefone'),
        help_text=_('Seu número de telefone')
    )
    gender = models.CharField(
        max_length=10,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Feminino'),
            ('O', 'Outro'),
            ('P', 'Prefiro não informar'),
        ],
        blank=True,
        verbose_name=_('Gênero')
    )
    interests = models.TextField(
        blank=True,
        verbose_name=_('Interesses'),
        help_text=_('Seus hobbies e interesses')
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Links sociais'),
        help_text=_('Links para redes sociais (JSON)')
    )
    # Configurações de privacidade
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('Perfil privado'),
        help_text=_('Se marcado, apenas seguidores aprovados podem ver seus posts')
    )
    show_email = models.BooleanField(
        default=False,
        verbose_name=_('Mostrar email'),
        help_text=_('Se marcado, seu email será visível no perfil')
    )
    show_phone = models.BooleanField(
        default=False,
        verbose_name=_('Mostrar telefone'),
        help_text=_('Se marcado, seu telefone será visível no perfil')
    )
    allow_messages = models.BooleanField(
        default=True,
        verbose_name=_('Permitir mensagens'),
        help_text=_('Se marcado, outros usuários podem te enviar mensagens')
    )
    # Estatísticas
    total_posts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total de posts')
    )
    total_likes_received = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total de curtidas recebidas')
    )
    total_comments_received = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total de comentários recebidos')
    )

    class Meta:
        verbose_name = _('Perfil Social')
        verbose_name_plural = _('Perfis Sociais')

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()

    @property
    def posts_count(self):
        return self.user.social_posts.count()


    def update_statistics(self):
        """Atualiza estatísticas do perfil"""
        self.total_posts = self.user.social_posts.count()
        self.total_likes_received = sum(post.likes_count for post in self.user.social_posts.all())
        self.total_comments_received = sum(post.comments_count for post in self.user.social_posts.all())
        self.save(update_fields=['total_posts', 'total_likes_received', 'total_comments_received'])
    
    def save(self, *args, **kwargs):
        """Override save para processar mídia automaticamente"""
        # Processar avatar se foi alterado
        if self.avatar and hasattr(self.avatar, 'file'):
            try:
                processed_path = process_avatar_image(
                    self.avatar.path if hasattr(self.avatar, 'path') else self.avatar.file,
                    size=400
                )
            except Exception:
                pass  # Se falhar, manter avatar original
        
        # Processar imagem de capa se foi alterada
        if self.cover_image and hasattr(self.cover_image, 'file'):
            try:
                processed_path = process_image_for_social_media(
                    self.cover_image.path if hasattr(self.cover_image, 'path') else self.cover_image.file,
                    max_width=1200,
                    max_height=400,
                    quality=90
                )
            except Exception:
                pass  # Se falhar, manter imagem original
        
        super().save(*args, **kwargs)


class Hashtag(BaseModel):
    """Modelo para hashtags nos posts"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Nome'),
        help_text=_('Nome da hashtag (sem #)')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descrição'),
        help_text=_('Descrição da hashtag')
    )
    posts_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de posts')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Hashtag')
        verbose_name_plural = _('Hashtags')
        ordering = ['-posts_count', '-created_at']

    def __str__(self):
        return f"#{self.name}"

    def update_posts_count(self):
        """Atualiza contador de posts da hashtag"""
        self.posts_count = self.posts.count()
        self.save(update_fields=['posts_count'])


class PostHashtag(BaseModel):
    """Modelo para relacionar posts com hashtags"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='hashtags',
        verbose_name=_('Post')
    )
    hashtag = models.ForeignKey(
        Hashtag,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Hashtag')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de criação')
    )

    class Meta:
        verbose_name = _('Hashtag do Post')
        verbose_name_plural = _('Hashtags dos Posts')
        unique_together = ['post', 'hashtag']
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.hashtag.name} em {self.post}"


# ============================================================================
# SISTEMA DE MODERAÇÃO
# ============================================================================

class Report(BaseModel):
    """Modelo para denúncias de conteúdo ou usuários"""
    REPORT_TYPES = [
        ('spam', _('Spam')),
        ('inappropriate', _('Conteúdo Inapropriado')),
        ('harassment', _('Assédio')),
        ('violence', _('Violência')),
        ('hate_speech', _('Discurso de Ódio')),
        ('fake_news', _('Fake News')),
        ('copyright', _('Violação de Direitos Autorais')),
        ('other', _('Outro')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('reviewing', _('Em Revisão')),
        ('resolved', _('Resolvido')),
        ('dismissed', _('Descartado')),
    ]
    
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_made',
        verbose_name=_('Denunciante')
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        verbose_name=_('Tipo de Denúncia')
    )
    description = models.TextField(
        verbose_name=_('Descrição'),
        help_text=_('Detalhes sobre a denúncia')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Conteúdo reportado (pode ser post, comentário ou usuário)
    reported_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports',
        verbose_name=_('Post Reportado')
    )
    reported_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports',
        verbose_name=_('Comentário Reportado')
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reports_received',
        verbose_name=_('Usuário Reportado')
    )
    
    # Campos de moderação
    assigned_moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reports_assigned',
        verbose_name=_('Moderador Responsável')
    )
    moderator_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notas do Moderador')
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data de Resolução')
    )
    
    # Prioridade baseada no tipo e quantidade de denúncias
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', _('Baixa')),
            ('medium', _('Média')),
            ('high', _('Alta')),
            ('urgent', _('Urgente')),
        ],
        default='medium',
        verbose_name=_('Prioridade')
    )
    
    # Contadores
    similar_reports_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Denúncias Similares')
    )
    
    class Meta:
        verbose_name = _('Denúncia')
        verbose_name_plural = _('Denúncias')
        ordering = ['-priority', '-created_at']
        permissions = [
            ("can_moderate_reports", _("Pode moderar denúncias")),
            ("can_view_reports", _("Pode visualizar denúncias")),
        ]

    def __str__(self):
        content = self.get_reported_content()
        return f"{self.get_report_type_display()} - {content}"

    def get_reported_content(self):
        """Retorna uma descrição do conteúdo reportado"""
        if self.reported_post:
            return f"Post: {self.reported_post.content[:50]}..."
        elif self.reported_comment:
            return f"Comentário: {self.reported_comment.content[:50]}..."
        elif self.reported_user:
            return f"Usuário: {self.reported_user.username}"
        return "Conteúdo não especificado"

    def save(self, *args, **kwargs):
        # Atualizar prioridade baseada no tipo de denúncia
        if self.report_type in ['violence', 'hate_speech']:
            self.priority = 'urgent'
        elif self.report_type in ['harassment', 'inappropriate']:
            self.priority = 'high'
        elif self.report_type == 'spam':
            self.priority = 'medium'
        else:
            self.priority = 'low'
        
        super().save(*args, **kwargs)

    def resolve(self, moderator, action_taken, notes=""):
        """Resolve a denúncia"""
        self.status = 'resolved'
        self.assigned_moderator = moderator
        self.moderator_notes = notes
        self.resolved_at = timezone.now()
        self.save()
        
        # Criar log da ação
        ModerationLog.objects.create(
            moderator=moderator,
            action_type='resolve_report',
            target_type='report',
            target_id=self.id,
            description=f"Denúncia resolvida: {action_taken}",
            details=notes
        )


class ModerationAction(BaseModel):
    """Modelo para ações de moderação tomadas"""
    ACTION_TYPES = [
        ('warn', _('Advertência')),
        ('hide_content', _('Ocultar Conteúdo')),
        ('delete_content', _('Deletar Conteúdo')),
        ('suspend_user', _('Suspender Usuário')),
        ('ban_user', _('Banir Usuário')),
        ('restrict_user', _('Restringir Usuário')),
        ('approve_content', _('Aprovar Conteúdo')),
        ('feature_content', _('Destacar Conteúdo')),
    ]
    
    SUSPENSION_TYPES = [
        ('temporary', _('Temporária')),
        ('permanent', _('Permanente')),
    ]
    
    moderator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='moderation_actions',
        verbose_name=_('Moderador')
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name=_('Tipo de Ação')
    )
    reason = models.TextField(
        verbose_name=_('Motivo'),
        help_text=_('Justificativa para a ação')
    )
    
    # Conteúdo ou usuário alvo da ação
    target_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='moderation_actions',
        verbose_name=_('Post Alvo')
    )
    target_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='moderation_actions',
        verbose_name=_('Comentário Alvo')
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='moderation_actions_received',
        verbose_name=_('Usuário Alvo')
    )
    
    # Campos específicos para suspensões
    suspension_duration = models.DurationField(
        blank=True,
        null=True,
        verbose_name=_('Duração da Suspensão')
    )
    suspension_type = models.CharField(
        max_length=20,
        choices=SUSPENSION_TYPES,
        blank=True,
        null=True,
        verbose_name=_('Tipo de Suspensão')
    )
    suspension_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data de Fim da Suspensão')
    )
    
    # Campos de controle
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativa'),
        help_text=_('Se a ação ainda está em vigor')
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Data de Expiração')
    )
    
    # Notificação ao usuário
    notify_user = models.BooleanField(
        default=True,
        verbose_name=_('Notificar Usuário')
    )
    notification_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Mensagem de Notificação')
    )

    class Meta:
        verbose_name = _('Ação de Moderação')
        verbose_name_plural = _('Ações de Moderação')
        ordering = ['-created_at']
        permissions = [
            ("can_take_moderation_actions", _("Pode tomar ações de moderação")),
            ("can_view_moderation_actions", _("Pode visualizar ações de moderação")),
        ]

    def __str__(self):
        target = self.get_target_description()
        return f"{self.get_action_type_display()} - {target}"

    def get_target_description(self):
        """Retorna descrição do alvo da ação"""
        if self.target_post:
            return f"Post: {self.target_post.content[:50]}..."
        elif self.target_comment:
            return f"Comentário: {self.target_comment.content[:50]}..."
        elif self.target_user:
            return f"Usuário: {self.target_user.username}"
        return "Alvo não especificado"

    def save(self, *args, **kwargs):
        # Definir data de expiração para ações temporárias
        if self.action_type in ['suspend_user', 'restrict_user'] and self.suspension_duration:
            self.suspension_end_date = timezone.now() + self.suspension_duration
            self.expires_at = self.suspension_end_date
        
        super().save(*args, **kwargs)

    def apply_action(self):
        """Aplica a ação de moderação"""
        if self.action_type == 'hide_content':
            if self.target_post:
                self.target_post.is_public = False
                self.target_post.save()
            elif self.target_comment:
                # Marcar comentário como oculto (adicionar campo se necessário)
                pass
        
        elif self.action_type == 'delete_content':
            if self.target_post:
                self.target_post.delete()
            elif self.target_comment:
                self.target_comment.delete()
        
        elif self.action_type in ['suspend_user', 'ban_user']:
            if self.target_user:
                self.target_user.is_active = False
                self.target_user.save()
        
        # Criar log da ação
        ModerationLog.objects.create(
            moderator=self.moderator,
            action_type=self.action_type,
            target_type=self.get_target_type(),
            target_id=self.get_target_id(),
            description=f"Ação aplicada: {self.get_action_type_display()}",
            details=self.reason
        )

    def get_target_type(self):
        """Retorna o tipo do alvo"""
        if self.target_post:
            return 'post'
        elif self.target_comment:
            return 'comment'
        elif self.target_user:
            return 'user'
        return 'unknown'

    def get_target_id(self):
        """Retorna o ID do alvo"""
        if self.target_post:
            return self.target_post.id
        elif self.target_comment:
            return self.target_comment.id
        elif self.target_user:
            return self.target_user.id
        return None


class ContentFilter(BaseModel):
    """Modelo para filtros automáticos de conteúdo"""
    FILTER_TYPES = [
        ('keyword', _('Palavra-chave')),
        ('regex', _('Expressão Regular')),
        ('spam_pattern', _('Padrão de Spam')),
        ('url_pattern', _('Padrão de URL')),
    ]
    
    ACTION_CHOICES = [
        ('flag', _('Marcar para Revisão')),
        ('auto_hide', _('Ocultar Automaticamente')),
        ('auto_delete', _('Deletar Automaticamente')),
        ('notify_moderator', _('Notificar Moderador')),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nome do Filtro')
    )
    filter_type = models.CharField(
        max_length=20,
        choices=FILTER_TYPES,
        verbose_name=_('Tipo de Filtro')
    )
    pattern = models.TextField(
        verbose_name=_('Padrão'),
        help_text=_('Palavra-chave, regex ou padrão a ser filtrado')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('Ação')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    
    # Campos de controle
    case_sensitive = models.BooleanField(
        default=False,
        verbose_name=_('Sensível a Maiúsculas/Minúsculas')
    )
    apply_to_posts = models.BooleanField(
        default=True,
        verbose_name=_('Aplicar a Posts')
    )
    apply_to_comments = models.BooleanField(
        default=True,
        verbose_name=_('Aplicar a Comentários')
    )
    apply_to_usernames = models.BooleanField(
        default=False,
        verbose_name=_('Aplicar a Nomes de Usuário')
    )
    
    # Estatísticas
    matches_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Número de Correspondências')
    )
    last_matched = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Última Correspondência')
    )

    class Meta:
        verbose_name = _('Filtro de Conteúdo')
        verbose_name_plural = _('Filtros de Conteúdo')
        ordering = ['-is_active', 'name']

        def __str__(self):
        return f"{self.name} ({self.get_filter_type_display()})"

    def matches_content(self, content):
        """Verifica se o conteúdo corresponde ao filtro"""
        if not self.is_active:
            return False
        
        if not content:
            return False
        
        if self.case_sensitive:
            text = content
        else:
            text = content.lower()
            pattern = self.pattern.lower()
        
        if self.filter_type == 'keyword':
            return pattern in text
        elif self.filter_type == 'regex':
            import re
            try:
                return bool(re.search(pattern, text))
            except re.error:
                return False
        elif self.filter_type == 'spam_pattern':
            # Padrões comuns de spam
            spam_patterns = [
                r'\b(buy|sell|cheap|discount|free|money|earn|rich)\b',
                r'\b(viagra|cialis|casino|poker|lottery)\b',
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            ]
            import re
            for spam_pattern in spam_patterns:
                if re.search(spam_pattern, text, re.IGNORECASE):
                    return True
            return False
        
        return False

    def apply_action_to_content(self, content, content_type, content_id):
        """Aplica a ação do filtro ao conteúdo"""
        if self.action == 'flag':
            # Criar denúncia automática
            Report.objects.create(
                reporter=None,  # Sistema
                report_type='spam' if self.filter_type == 'spam_pattern' else 'inappropriate',
                description=f"Conteúdo filtrado automaticamente: {self.name}",
                status='pending',
                priority='medium'
            )
        
        elif self.action == 'auto_hide':
            if content_type == 'post':
                post = Post.objects.get(id=content_id)
                post.is_public = False
                post.save()
            elif content_type == 'comment':
                comment = Comment.objects.get(id=content_id)
                # Marcar como oculto (implementar se necessário)
                pass
        
        elif self.action == 'auto_delete':
            if content_type == 'post':
                Post.objects.filter(id=content_id).delete()
            elif content_type == 'comment':
                Comment.objects.filter(id=content_id).delete()
        
        # Atualizar estatísticas
        self.matches_count += 1
        self.last_matched = timezone.now()
        self.save()


class ModerationLog(BaseModel):
    """Modelo para logs de ações de moderação"""
    LOG_TYPES = [
        ('report_created', _('Denúncia Criada')),
        ('report_resolved', _('Denúncia Resolvida')),
        ('report_status_changed', _('Status da Denúncia Alterado')),
        ('report_assigned', _('Denúncia Atribuída')),
        ('content_hidden', _('Conteúdo Ocultado')),
        ('content_deleted', _('Conteúdo Deletado')),
        ('user_suspended', _('Usuário Suspenso')),
        ('user_banned', _('Usuário Banido')),
        ('filter_triggered', _('Filtro Acionado')),
        ('warning_sent', _('Advertência Enviada')),
    ]
    
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moderation_logs',
        verbose_name=_('Moderador')
    )
    action_type = models.CharField(
        max_length=30,
        choices=LOG_TYPES,
        verbose_name=_('Tipo de Ação')
    )
    target_type = models.CharField(
        max_length=20,
        verbose_name=_('Tipo do Alvo'),
        help_text=_('post, comment, user, report, etc.')
    )
    target_id = models.IntegerField(
        verbose_name=_('ID do Alvo')
    )
    description = models.TextField(
        verbose_name=_('Descrição')
    )
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Detalhes Adicionais')
    )
    
    # Campos de contexto
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('Endereço IP')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('User Agent')
    )

    class Meta:
        verbose_name = _('Log de Moderação')
        verbose_name_plural = _('Logs de Moderação')
        ordering = ['-created_at']
        permissions = [
            ("can_view_moderation_logs", _("Pode visualizar logs de moderação")),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.description[:50]}"

    @classmethod
    def log_action(cls, moderator, action_type, target_type, target_id, description, details=None, request=None):
        """Método de classe para facilitar a criação de logs"""
        log = cls.objects.create(
            moderator=moderator,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            details=details
        )
        
        if request:
            log.ip_address = request.META.get('REMOTE_ADDR')
            log.user_agent = request.META.get('HTTP_USER_AGENT')
            log.save()
        
        return log