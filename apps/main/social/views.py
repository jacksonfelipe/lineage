from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta
import re

from .models import Post, Comment, Like, Follow, UserProfile, Share, Hashtag, PostHashtag, CommentLike
from .forms import PostForm, CommentForm, UserProfileForm, SearchForm, ShareForm, ReactionForm, HashtagForm

User = get_user_model()


@login_required
def feed(request):
    """Feed principal da rede social"""
    # Buscar posts de usuários que o usuário segue + posts públicos + posts próprios
    following_users = request.user.following.values_list('following_id', flat=True)
    
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(is_public=True) | Q(author=request.user)
    ).select_related('author').prefetch_related(
        'likes', 'comments', 'hashtags'
    ).order_by('-created_at')
    
    # Anotar posts com informação se o usuário atual deu like
    for post in posts:
        post.is_liked_by_current_user = post.is_liked_by(request.user)
    
    # Paginação
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Buscar perfil do usuário
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Estatísticas do usuário
    user_stats = {
        'posts_count': Post.objects.filter(author=request.user).count(),
        'followers_count': request.user.followers.count(),
        'following_count': request.user.following.count(),
        'total_likes_received': profile.total_likes_received,
        'total_comments_received': profile.total_comments_received,
    }
    
    # Hashtags populares
    popular_hashtags = Hashtag.objects.filter(posts_count__gt=0).order_by('-posts_count')[:10]
    
    # Usuários sugeridos (não seguidos pelo usuário atual)
    following_users = request.user.following.values_list('following_id', flat=True)
    suggested_users = User.objects.exclude(
        id__in=list(following_users) + [request.user.id]
    ).annotate(
        posts_count=Count('social_posts')
    ).filter(posts_count__gt=0).order_by('-posts_count')[:10]
    
    # Estatísticas da rede
    from datetime import date
    today = date.today()
    network_stats = {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'posts_today': Post.objects.filter(created_at__date=today).count(),
    }
    
    # Formulário para criar novo post
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Processar hashtags
            hashtags = form.cleaned_data.get('hashtags', [])
            
            post.save()
            
            # Adicionar hashtags ao post
            for hashtag_name in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
                PostHashtag.objects.create(post=post, hashtag=hashtag)
                hashtag.update_posts_count()
            
            messages.success(request, _('Post criado com sucesso!'))
            return redirect('social:feed')
    else:
        form = PostForm()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'profile': profile,
        'user_stats': user_stats,
        'popular_hashtags': popular_hashtags,
        'suggested_users': suggested_users,
        'network_stats': network_stats,
        'segment': 'feed',
        'parent': 'social',
    }
    return render(request, 'social/feed.html', context)


@login_required
def my_posts(request):
    """Posts do usuário logado"""
    posts = Post.objects.filter(author=request.user).order_by('-is_pinned', '-created_at')
    
    # Anotar posts com informação se o usuário atual deu like
    for post in posts:
        post.is_liked_by_current_user = post.is_liked_by(request.user)
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'segment': 'my_posts',
        'parent': 'social',
    }
    return render(request, 'social/my_posts.html', context)


@login_required
def post_detail(request, post_id):
    """Detalhes de um post específico"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar se o usuário pode ver o post
    if not post.is_public and post.author != request.user:
        if not Follow.objects.filter(follower=request.user, following=post.author).exists():
            messages.error(request, _('Você não tem permissão para ver este post.'))
            return redirect('social:feed')
    
    # Incrementar visualizações
    post.increment_views()
    
    # Adicionar informação se o usuário atual deu like
    post.is_liked_by_current_user = post.is_liked_by(request.user)
    
    # Formulário para comentários
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Atualizar contador de comentários
            post.update_counts()
            
            messages.success(request, _('Comentário adicionado!'))
            return redirect('social:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    # Buscar comentários do post
    comments = post.comments.filter(parent=None).order_by('created_at')
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'segment': 'post_detail',
        'parent': 'social',
    }
    return render(request, 'social/post_detail.html', context)


@login_required
@require_POST
def like_post(request, post_id):
    """Curtir/descurtir um post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar se o usuário pode ver o post
    if not post.is_public and post.author != request.user:
        if not Follow.objects.filter(follower=request.user, following=post.author).exists():
            return JsonResponse({'error': _('Permissão negada')}, status=403)
    
    like, created = Like.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={'reaction_type': 'like'}
    )
    
    if not created:
        # Se já existe, remover a curtida
        like.delete()
        liked = False
    else:
        liked = True
    
    # Atualizar contador
    post.update_counts()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count,
        'reaction_type': like.reaction_type if liked else None
    })


@login_required
@require_POST
def react_to_post(request, post_id):
    """Reagir a um post com diferentes emojis"""
    post = get_object_or_404(Post, id=post_id)
    form = ReactionForm(request.POST)
    
    if form.is_valid():
        reaction_type = form.cleaned_data['reaction_type']
        
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            # Se já existe, atualizar o tipo de reação
            like.reaction_type = reaction_type
            like.save()
        
        # Atualizar contador
        post.update_counts()
        
        return JsonResponse({
            'success': True,
            'reaction_type': reaction_type,
            'likes_count': post.likes_count
        })
    
    return JsonResponse({'error': _('Dados inválidos')}, status=400)


@login_required
@require_POST
def like_comment(request, comment_id):
    """Curtir/descurtir um comentário"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    like, created = CommentLike.objects.get_or_create(
        comment=comment,
        user=request.user
    )
    
    if not created:
        # Se já existe, remover a curtida
        like.delete()
        liked = False
    else:
        liked = True
    
    # Atualizar contador
    comment.update_likes_count()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes_count
    })


@login_required
@require_POST
def share_post(request, post_id):
    """Compartilhar um post"""
    original_post = get_object_or_404(Post, id=post_id)
    form = ShareForm(request.POST)
    
    if form.is_valid():
        # Criar novo post como compartilhamento
        post = Post.objects.create(
            author=request.user,
            content=form.cleaned_data.get('comment', ''),
            is_public=form.cleaned_data.get('is_public', True),
            link=f"/social/post/{original_post.id}/"
        )
        
        # Criar registro de compartilhamento
        Share.objects.create(
            original_post=original_post,
            user=request.user,
            comment=form.cleaned_data.get('comment', '')
        )
        
        # Atualizar contador de compartilhamentos
        original_post.shares_count += 1
        original_post.save(update_fields=['shares_count'])
        
        messages.success(request, _('Post compartilhado com sucesso!'))
        return redirect('social:feed')
    
    messages.error(request, _('Erro ao compartilhar o post.'))
    return redirect('social:post_detail', post_id=post_id)


@login_required
@require_POST
def follow_user(request, user_id):
    """Seguir/deixar de seguir um usuário"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if user_to_follow == request.user:
        return JsonResponse({'error': _('Você não pode seguir a si mesmo')}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        # Se já existe, remover o follow
        follow.delete()
        following = False
    else:
        following = True
    
    return JsonResponse({
        'following': following,
        'followers_count': user_to_follow.followers.count(),
        'following_count': user_to_follow.following.count()
    })


@login_required
def user_profile(request, username):
    """Perfil de um usuário"""
    user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Verificar se o usuário pode ver o perfil
    if profile.is_private and user != request.user:
        if not Follow.objects.filter(follower=request.user, following=user).exists():
            messages.error(request, _('Este perfil é privado.'))
            return redirect('social:feed')
    
    # Buscar posts do usuário
    posts = Post.objects.filter(author=user).order_by('-is_pinned', '-created_at')
    
    # Anotar posts com informação se o usuário atual deu like
    for post in posts:
        post.is_liked_by_current_user = post.is_liked_by(request.user)
    
    # Verificar se o usuário logado segue este usuário
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'segment': 'user_profile',
        'parent': 'social',
    }
    return render(request, 'social/user_profile.html', context)


@login_required
def edit_profile(request):
    """Editar perfil do usuário logado"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil atualizado com sucesso!'))
            return redirect('social:user_profile', username=request.user.username)
    else:
        # Pré-preencher links sociais
        initial_data = {}
        for field in ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']:
            if field in profile.social_links:
                initial_data[field] = profile.social_links[field]
        
        form = UserProfileForm(instance=profile, initial=initial_data)
    
    context = {
        'form': form,
        'profile': profile,
        'segment': 'edit_profile',
        'parent': 'social',
    }
    return render(request, 'social/edit_profile.html', context)


@login_required
def search(request):
    """Buscar usuários e posts"""
    form = SearchForm(request.GET)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('q', '').strip()
        search_type = form.cleaned_data.get('search_type', 'all')
        date_filter = form.cleaned_data.get('date_filter', 'all')
        
        if query:
            # Aplicar filtro de data
            date_filter_obj = None
            if date_filter == 'today':
                date_filter_obj = timezone.now().date()
            elif date_filter == 'week':
                date_filter_obj = timezone.now() - timedelta(days=7)
            elif date_filter == 'month':
                date_filter_obj = timezone.now() - timedelta(days=30)
            elif date_filter == 'year':
                date_filter_obj = timezone.now() - timedelta(days=365)
            
            if search_type in ['all', 'users']:
                # Buscar usuários
                users = User.objects.filter(
                    Q(username__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(email__icontains=query)
                ).exclude(id=request.user.id)
                
                for user in users[:10]:  # Limitar a 10 resultados
                    results.append({
                        'type': 'user',
                        'object': user,
                        'profile': getattr(user, 'social_profile', None)
                    })
            
            if search_type in ['all', 'posts']:
                # Buscar posts
                posts_query = Post.objects.filter(
                    Q(content__icontains=query) |
                    Q(author__username__icontains=query)
                ).filter(is_public=True)
                
                if date_filter_obj:
                    if isinstance(date_filter_obj, datetime):
                        posts_query = posts_query.filter(created_at__gte=date_filter_obj)
                    else:
                        posts_query = posts_query.filter(created_at__date__gte=date_filter_obj)
                
                for post in posts_query[:10]:  # Limitar a 10 resultados
                    post.is_liked_by_current_user = post.is_liked_by(request.user)
                    results.append({
                        'type': 'post',
                        'object': post
                    })
            
            if search_type in ['all', 'hashtags']:
                # Buscar hashtags
                hashtags = Hashtag.objects.filter(name__icontains=query)
                
                for hashtag in hashtags[:5]:  # Limitar a 5 resultados
                    results.append({
                        'type': 'hashtag',
                        'object': hashtag
                    })
    
    context = {
        'form': form,
        'results': results,
        'segment': 'search',
        'parent': 'social',
    }
    return render(request, 'social/search.html', context)


@login_required
def hashtag_detail(request, hashtag_name):
    """Detalhes de uma hashtag"""
    hashtag = get_object_or_404(Hashtag, name=hashtag_name.lower())
    
    # Buscar posts com esta hashtag
    posts = Post.objects.filter(
        hashtags__hashtag=hashtag,
        is_public=True
    ).order_by('-created_at')
    
    # Anotar posts com informação se o usuário atual deu like
    for post in posts:
        post.is_liked_by_current_user = post.is_liked_by(request.user)
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hashtag': hashtag,
        'page_obj': page_obj,
        'segment': 'hashtag_detail',
        'parent': 'social',
    }
    return render(request, 'social/hashtag_detail.html', context)


@login_required
def followers_list(request, username):
    """Lista de seguidores de um usuário"""
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    
    paginator = Paginator(followers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'segment': 'followers_list',
        'parent': 'social',
    }
    return render(request, 'social/followers_list.html', context)


@login_required
def following_list(request, username):
    """Lista de usuários que um usuário segue"""
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    
    paginator = Paginator(following, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'segment': 'following_list',
        'parent': 'social',
    }
    return render(request, 'social/following_list.html', context)


@login_required
@require_POST
def pin_post(request, post_id):
    """Fixar/desfixar um post no perfil"""
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    post.is_pinned = not post.is_pinned
    post.save(update_fields=['is_pinned'])
    
    return JsonResponse({
        'pinned': post.is_pinned
    })


@login_required
@require_POST
def delete_comment(request, comment_id):
    """Deletar um comentário"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Verificar permissão
    if comment.author != request.user and comment.post.author != request.user:
        return JsonResponse({'error': _('Permissão negada')}, status=403)
    
    post = comment.post
    comment.delete()
    
    # Atualizar contador
    post.update_counts()
    
    return JsonResponse({'success': True})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_form.html'
    success_url = reverse_lazy('social:feed')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Processar hashtags
        hashtags = form.cleaned_data.get('hashtags', [])
        for hashtag_name in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            PostHashtag.objects.create(post=form.instance, hashtag=hashtag)
            hashtag.update_posts_count()
        
        messages.success(self.request, _('Post criado com sucesso!'))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'post_create'
        context['parent'] = 'social'
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('social:post_detail', kwargs={'post_id': self.object.id})

    def form_valid(self, form):
        # Marcar como editado
        self.object.mark_as_edited()
        
        # Processar hashtags
        hashtags = form.cleaned_data.get('hashtags', [])
        
        # Remover hashtags antigas
        self.object.hashtags.all().delete()
        
        response = super().form_valid(form)
        
        # Adicionar novas hashtags
        for hashtag_name in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            PostHashtag.objects.create(post=self.object, hashtag=hashtag)
            hashtag.update_posts_count()
        
        messages.success(self.request, _('Post atualizado com sucesso!'))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'post_edit'
        context['parent'] = 'social'
        
        # Pré-preencher hashtags
        if self.object:
            hashtags = [f"#{ph.hashtag.name}" for ph in self.object.hashtags.all()]
            context['form'].fields['hashtags'].initial = ' '.join(hashtags)
        
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'social/post_confirm_delete.html'
    success_url = reverse_lazy('social:my_posts')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Remover hashtags associadas
        post = self.get_object()
        post.hashtags.all().delete()
        
        messages.success(request, _('Post deletado com sucesso!'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'post_delete'
        context['parent'] = 'social'
        return context
