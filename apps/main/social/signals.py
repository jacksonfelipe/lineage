from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, Like, Comment, Post

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Criar perfil social automaticamente quando um usuário é criado"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salvar perfil social quando o usuário é salvo"""
    try:
        instance.social_profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Like)
@receiver(post_delete, sender=Like)
def update_profile_stats_on_like(sender, instance, **kwargs):
    """Atualizar estatísticas do perfil quando likes são criados/deletados"""
    if hasattr(instance, 'post') and instance.post.author:
        try:
            profile = instance.post.author.social_profile
            profile.update_statistics()
        except UserProfile.DoesNotExist:
            pass


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def update_profile_stats_on_comment(sender, instance, **kwargs):
    """Atualizar estatísticas do perfil quando comentários são criados/deletados"""
    if hasattr(instance, 'post') and instance.post.author:
        try:
            profile = instance.post.author.social_profile
            profile.update_statistics()
        except UserProfile.DoesNotExist:
            pass


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)  
def update_profile_stats_on_post(sender, instance, **kwargs):
    """Atualizar estatísticas do perfil quando posts são criados/deletados"""
    if instance.author:
        try:
            profile = instance.author.social_profile
            profile.update_statistics()
        except UserProfile.DoesNotExist:
            pass
