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
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Público'),
        help_text=_('Se marcado, o post será visível para todos')
    )
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
        ordering = ['-created_at']

    def __str__(self):
        return f"Post de {self.author.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def update_counts(self):
        """Atualiza contadores de likes e comentários"""
        self.likes_count = self.likes.count()
        self.comments_count = self.comments.count()
        self.save(update_fields=['likes_count', 'comments_count'])


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
        return f"Curtida de {self.user.username} em {self.post}"


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
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('Perfil privado'),
        help_text=_('Se marcado, apenas seguidores aprovados podem ver seus posts')
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
