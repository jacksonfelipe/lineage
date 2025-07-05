"""
Testes para as funções de verificação de status do servidor
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from utils.server_status import (
    ServerStatusChecker,
    check_server_status,
    is_game_server_online,
    is_login_server_online,
    check_port
)


def test_server_status_checker():
    """Testa a classe ServerStatusChecker"""
    print("=== Testando ServerStatusChecker ===")
    
    checker = ServerStatusChecker()
    
    # Testar verificação de porta
    print("1. Testando verificação de porta...")
    result = checker.check_port_connection("google.com", 80, timeout=2)
    print(f"   Google.com:80 -> {'Online' if result else 'Offline'}")
    
    # Testar status do servidor de jogo
    print("2. Testando status do servidor de jogo...")
    game_status = checker.get_game_server_status()
    print(f"   Status: {game_status['status']}")
    print(f"   Forçado: {game_status['forced']}")
    print(f"   Mensagem: {game_status['message']}")
    
    # Testar status do servidor de login
    print("3. Testando status do servidor de login...")
    login_status = checker.get_login_server_status()
    print(f"   Status: {login_status['status']}")
    print(f"   Forçado: {login_status['forced']}")
    print(f"   Mensagem: {login_status['message']}")
    
    # Testar resumo completo
    print("4. Testando resumo completo...")
    summary = checker.get_server_status_summary()
    print(f"   Status Geral: {summary['overall_status']}")
    print(f"   IP: {summary['server_ip']}")
    print(f"   Verificado em: {summary['checked_at']}")


def test_utility_functions():
    """Testa as funções utilitárias"""
    print("\n=== Testando Funções Utilitárias ===")
    
    # Testar check_server_status
    print("1. Testando check_server_status()...")
    status = check_server_status()
    print(f"   Status retornado: {type(status)}")
    print(f"   Chaves disponíveis: {list(status.keys())}")
    
    # Testar is_game_server_online
    print("2. Testando is_game_server_online()...")
    game_online = is_game_server_online()
    print(f"   Servidor de jogo online: {game_online}")
    
    # Testar is_login_server_online
    print("3. Testando is_login_server_online()...")
    login_online = is_login_server_online()
    print(f"   Servidor de login online: {login_online}")
    
    # Testar check_port
    print("4. Testando check_port()...")
    port_open = check_port("google.com", 80, timeout=2)
    print(f"   Google.com:80 aberta: {port_open}")


def test_configuration():
    """Testa se as configurações estão sendo lidas corretamente"""
    print("\n=== Testando Configurações ===")
    
    from django.conf import settings
    
    print(f"1. GAME_SERVER_IP: {getattr(settings, 'GAME_SERVER_IP', 'Não configurado')}")
    print(f"2. GAME_SERVER_PORT: {getattr(settings, 'GAME_SERVER_PORT', 'Não configurado')}")
    print(f"3. LOGIN_SERVER_PORT: {getattr(settings, 'LOGIN_SERVER_PORT', 'Não configurado')}")
    print(f"4. SERVER_STATUS_TIMEOUT: {getattr(settings, 'SERVER_STATUS_TIMEOUT', 'Não configurado')}")
    print(f"5. FORCE_GAME_SERVER_STATUS: {getattr(settings, 'FORCE_GAME_SERVER_STATUS', 'Não configurado')}")
    print(f"6. FORCE_LOGIN_SERVER_STATUS: {getattr(settings, 'FORCE_LOGIN_SERVER_STATUS', 'Não configurado')}")


def test_error_handling():
    """Testa o tratamento de erros"""
    print("\n=== Testando Tratamento de Erros ===")
    
    checker = ServerStatusChecker()
    
    # Testar com host inválido
    print("1. Testando com host inválido...")
    try:
        result = checker.check_port_connection("host_invalido_12345", 80, timeout=1)
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Erro capturado: {e}")
    
    # Testar com porta inválida
    print("2. Testando com porta inválida...")
    try:
        result = checker.check_port_connection("google.com", 99999, timeout=1)
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Erro capturado: {e}")


def main():
    """Função principal para executar todos os testes"""
    print("🚀 Iniciando testes de verificação de status do servidor...\n")
    
    try:
        test_configuration()
        test_server_status_checker()
        test_utility_functions()
        test_error_handling()
        
        print("\n✅ Todos os testes foram executados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 