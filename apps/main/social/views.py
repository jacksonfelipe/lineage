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

from .models import Post, Comment, Like, Follow, UserProfile
from .forms import PostForm, CommentForm, UserProfileForm, SearchForm

User = get_user_model()


@login_required
def feed(request):
    """Feed principal da rede social"""
    # Buscar posts de usuários que o usuário segue + posts públicos
    following_users = request.user.following.values_list('following_id', flat=True)
    
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(is_public=True)
    ).exclude(
        author=request.user  # Excluir posts próprios do feed principal
    ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
    
    # Paginação
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Formulário para criar novo post
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, _('Post criado com sucesso!'))
            return redirect('social:feed')
    else:
        form = PostForm()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'segment': 'feed',
        'parent': 'social',
    }
    return render(request, 'social/feed.html', context)


@login_required
def my_posts(request):
    """Posts do usuário logado"""
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
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
    
    # Formulário para comentários
    if request.method == 'POST':
        form = CommentForm(request.POST)
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
            return HttpResponseForbidden()
    
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        # Se já existe, remove a curtida
        like.delete()
        liked = False
    else:
        liked = True
    
    # Atualizar contador de likes
    post.update_counts()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })


@login_required
@require_POST
def follow_user(request, user_id):
    """Seguir/deixar de seguir um usuário"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if user_to_follow == request.user:
        return JsonResponse({'error': _('Você não pode seguir a si mesmo.')}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        # Se já existe, remove o follow
        follow.delete()
        following = False
    else:
        following = True
    
    return JsonResponse({
        'following': following,
        'followers_count': user_to_follow.followers.count()
    })


@login_required
def user_profile(request, username):
    """Perfil de um usuário"""
    user = get_object_or_404(User, username=username)
    
    # Verificar se o usuário pode ver o perfil
    if user.social_profile.is_private and user != request.user:
        if not Follow.objects.filter(follower=request.user, following=user).exists():
            messages.error(request, _('Este perfil é privado.'))
            return redirect('social:feed')
    
    # Buscar posts do usuário
    posts = Post.objects.filter(author=user).order_by('-created_at')
    
    # Verificar se o usuário logado segue este usuário
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
        'segment': 'user_profile',
        'parent': 'social',
    }
    return render(request, 'social/user_profile.html', context)


@login_required
def edit_profile(request):
    """Editar perfil social"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil atualizado com sucesso!'))
            return redirect('social:user_profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'segment': 'edit_profile',
        'parent': 'social',
    }
    return render(request, 'social/edit_profile.html', context)


@login_required
def search(request):
    """Busca de usuários e posts"""
    form = SearchForm(request.GET)
    results = []
    
    if form.is_valid() and form.cleaned_data.get('q'):
        query = form.cleaned_data['q']
        search_type = form.cleaned_data['search_type']
        
        if search_type in ['all', 'users']:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(id=request.user.id)[:10]
            results.extend([('user', user) for user in users])
        
        if search_type in ['all', 'posts']:
            posts = Post.objects.filter(
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            ).filter(is_public=True)[:10]
            results.extend([('post', post) for post in posts])
    
    context = {
        'form': form,
        'results': results,
        'segment': 'search',
        'parent': 'social',
    }
    return render(request, 'social/search.html', context)


@login_required
def followers_list(request, username):
    """Lista de seguidores de um usuário"""
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    
    context = {
        'profile_user': user,
        'followers': followers,
        'segment': 'followers',
        'parent': 'social',
    }
    return render(request, 'social/followers_list.html', context)


@login_required
def following_list(request, username):
    """Lista de usuários que um usuário segue"""
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    
    context = {
        'profile_user': user,
        'following': following,
        'segment': 'following',
        'parent': 'social',
    }
    return render(request, 'social/following_list.html', context)


# Views baseadas em classes para CRUD de posts
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_form.html'
    success_url = reverse_lazy('social:feed')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _('Post criado com sucesso!'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'create_post'
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
        messages.success(self.request, _('Post atualizado com sucesso!'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'edit_post'
        context['parent'] = 'social'
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'social/post_confirm_delete.html'
    success_url = reverse_lazy('social:my_posts')
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Post excluído com sucesso!'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'delete_post'
        context['parent'] = 'social'
        return context


@login_required
@require_POST
def delete_comment(request, comment_id):
    """Excluir um comentário"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Verificar se o usuário pode excluir o comentário
    if comment.author != request.user and comment.post.author != request.user:
        return HttpResponseForbidden()
    
    post_id = comment.post.id
    comment.delete()
    
    # Atualizar contador de comentários
    comment.post.update_counts()
    
    messages.success(request, _('Comentário excluído com sucesso!'))
    return redirect('social:post_detail', post_id=post_id)
