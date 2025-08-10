from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def verified_badge(user, size="16px", show_tooltip=True):
    """
    Exibe o símbolo de verificação para usuários verificados
    
    Args:
        user: Usuário a ser verificado
        size: Tamanho do ícone (ex: "16px", "20px")
        show_tooltip: Se deve mostrar tooltip explicativo
    """
    if not user or not getattr(user, 'is_verified', False):
        return ""
    
    tooltip_attr = f'title="{_("Conta verificada")}"' if show_tooltip else ""
    
    html = f'''
    <svg xmlns="http://www.w3.org/2000/svg" 
         viewBox="0 0 24 24" 
         style="width: {size}; height: {size}; display: inline-block; vertical-align: middle; margin-left: 2px;"
         {tooltip_attr}
         class="verified-badge">
        <circle cx="12" cy="12" r="10" fill="#1DA1F2"/>
        <path d="M9 12l2 2 4-4" stroke="white" stroke-width="2.5"/>
    </svg>
    '''
    
    return mark_safe(html)


@register.simple_tag
def user_display_name(user, show_verified=True, size="16px"):
    """
    Exibe o nome do usuário com símbolo de verificação se aplicável
    
    Args:
        user: Usuário a ser exibido
        show_verified: Se deve mostrar o símbolo de verificação
        size: Tamanho do ícone de verificação
    """
    if not user:
        return ""
    
    name = user.username
    verified_icon = verified_badge(user, size, show_tooltip=True) if show_verified else ""
    
    return mark_safe(f'{name}{verified_icon}')


@register.filter
def is_verified(user):
    """
    Filtro para verificar se um usuário é verificado
    """
    return getattr(user, 'is_verified', False) if user else False
