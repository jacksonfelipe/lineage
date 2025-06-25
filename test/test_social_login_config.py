#!/usr/bin/env python3
"""
Script de teste para verificar as configurações de login social
"""

import os
import sys
import django
from pathlib import Path

# Adiciona o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

def test_social_login_config():
    """Testa as configurações de login social"""
    
    print("=== Teste de Configurações de Login Social ===\n")
    
    # Verifica se as configurações estão definidas
    configs = [
        'SOCIAL_LOGIN_ENABLED',
        'SOCIAL_LOGIN_SHOW_SECTION',
        'SOCIAL_LOGIN_GOOGLE_ENABLED',
        'SOCIAL_LOGIN_GITHUB_ENABLED',
        'SOCIAL_LOGIN_DISCORD_ENABLED',
    ]
    
    for config in configs:
        value = getattr(settings, config, None)
        print(f"{config}: {value}")
    
    print("\n=== Status dos Provedores ===")
    
    # Verifica se os provedores estão configurados
    providers = {
        'Google': ('GOOGLE_CLIENT_ID', 'GOOGLE_SECRET_KEY'),
        'GitHub': ('GITHUB_CLINET_ID', 'GITHUB_SECRET_KEY'),
        'Discord': ('DISCORD_CLIENT_ID', 'DISCORD_SECRET_KEY'),
    }
    
    for provider_name, (client_id_key, secret_key) in providers.items():
        client_id = getattr(settings, client_id_key, None)
        secret = getattr(settings, secret_key, None)
        
        has_client_id = bool(client_id and client_id != "")
        has_secret = bool(secret and secret != "")
        
        print(f"{provider_name}:")
        print(f"  - Client ID configurado: {has_client_id}")
        print(f"  - Secret configurado: {has_secret}")
        print(f"  - Habilitado: {getattr(settings, f'SOCIAL_LOGIN_{provider_name.upper()}_ENABLED', False)}")
        print()
    
    print("=== Recomendações ===")
    
    if not settings.SOCIAL_LOGIN_ENABLED:
        print("⚠️  Login social está desabilitado globalmente")
    
    if not settings.SOCIAL_LOGIN_SHOW_SECTION:
        print("⚠️  Seção de login social está oculta")
    
    enabled_providers = []
    for provider_name in providers.keys():
        if getattr(settings, f'SOCIAL_LOGIN_{provider_name.upper()}_ENABLED', False):
            enabled_providers.append(provider_name)
    
    if enabled_providers:
        print(f"✅ Provedores habilitados: {', '.join(enabled_providers)}")
    else:
        print("⚠️  Nenhum provedor está habilitado")

if __name__ == '__main__':
    test_social_login_config() 