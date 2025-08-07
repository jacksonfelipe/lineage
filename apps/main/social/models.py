from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel

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
        help_text=_('Imagem opcional para o post')
    )
    # Novos campos para melhorar a rede social
    video = models.FileField(
        upload_to='social/videos/',
        blank=True,
        null=True,
        verbose_name=_('Vídeo'),
        help_text=_('Vídeo opcional para o post (MP4, AVI, MOV)')
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
        """Atualiza contadores de likes e comentários"""
        self.likes_count = self.likes.count()
        self.comments_count = self.comments.count()
        self.save(update_fields=['likes_count', 'comments_count'])

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
        help_text=_('Imagem opcional no comentário')
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
        help_text=_('Foto de perfil')
    )
    cover_image = models.ImageField(
        upload_to='social/covers/',
        blank=True,
        null=True,
        verbose_name=_('Imagem de capa'),
        help_text=_('Imagem de capa do perfil')
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
