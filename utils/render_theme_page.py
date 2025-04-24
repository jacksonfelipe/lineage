import os
from django.conf import settings
from django.shortcuts import render


def render_theme_page(request, base_path, template_name, context=None):
    """
    Função para renderizar a página do tema, verificando se o arquivo existe no tema ativo.
    Se o arquivo não existir, será utilizado o fallback.
    """
    theme_slug = request.META.get('theme_slug', '')
    theme_files = request.META.get('theme_files', {})

    if theme_slug:
        theme_path = os.path.join(settings.BASE_DIR, 'templates', 'installed', theme_slug)
        
        # Verificar se o arquivo específico (ex: index.html) existe no diretório do tema
        theme_file_path = os.path.join(theme_path, template_name)

        if os.path.isfile(theme_file_path):
            # Se o arquivo existir, renderiza o template do tema
            return render(request, f"installed/{theme_slug}/{template_name}", context)
    
    # Se o arquivo não existir, utilizar o template fallback padrão
    return render(request, f"{base_path}/{template_name}", context)
