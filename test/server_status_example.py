"""
Exemplo de uso das funções de verificação de status do servidor
"""

from ..utils.server_status import (
    ServerStatusChecker,
    check_server_status,
    is_game_server_online,
    is_login_server_online,
    check_port
)


def exemplo_uso_basico():
    """
    Exemplo básico de como usar as funções
    """
    print("=== Exemplo de Uso das Funções de Status do Servidor ===\n")
    
    # 1. Verificação simples se o servidor está online
    print("1. Verificação simples:")
    if is_game_server_online():
        print("   ✅ Servidor de jogo está ONLINE")
    else:
        print("   ❌ Servidor de jogo está OFFLINE")
    
    if is_login_server_online():
        print("   ✅ Servidor de login está ONLINE")
    else:
        print("   ❌ Servidor de login está OFFLINE")
    
    print()
    
    # 2. Verificação completa com detalhes
    print("2. Verificação completa:")
    status = check_server_status()
    print(f"   Status Geral: {status['overall_status']}")
    print(f"   IP do Servidor: {status['server_ip']}")
    print(f"   Verificado em: {status['checked_at']}")
    print()
    
    # 3. Detalhes do servidor de jogo
    print("3. Detalhes do Servidor de Jogo:")
    game_status = status['game_server']
    print(f"   Status: {game_status['status']}")
    print(f"   Porta: {game_status['port']}")
    print(f"   Forçado: {game_status['forced']}")
    print(f"   Mensagem: {game_status['message']}")
    print()
    
    # 4. Detalhes do servidor de login
    print("4. Detalhes do Servidor de Login:")
    login_status = status['login_server']
    print(f"   Status: {login_status['status']}")
    print(f"   Porta: {login_status['port']}")
    print(f"   Forçado: {login_status['forced']}")
    print(f"   Mensagem: {login_status['message']}")
    print()
    
    # 5. Verificação de porta específica
    print("5. Verificação de porta específica:")
    host = "127.0.0.1"
    port = 80
    if check_port(host, port):
        print(f"   ✅ Porta {port} em {host} está aberta")
    else:
        print(f"   ❌ Porta {port} em {host} está fechada")


def exemplo_uso_avancado():
    """
    Exemplo avançado usando a classe diretamente
    """
    print("=== Exemplo Avançado ===\n")
    
    # Criar instância do verificador
    checker = ServerStatusChecker()
    
    # Verificar apenas servidor de jogo
    game_status = checker.get_game_server_status()
    print(f"Status do Game Server: {game_status}")
    
    # Verificar apenas servidor de login
    login_status = checker.get_login_server_status()
    print(f"Status do Login Server: {login_status}")
    
    # Verificar porta personalizada
    custom_host = "google.com"
    custom_port = 80
    is_open = checker.check_port_connection(custom_host, custom_port, timeout=2)
    print(f"Porta {custom_port} em {custom_host}: {'Aberta' if is_open else 'Fechada'}")


def exemplo_uso_em_view():
    """
    Exemplo de como usar em uma view do Django
    """
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    
    @require_http_methods(["GET"])
    def api_server_status(request):
        """
        API endpoint para verificar status do servidor
        """
        try:
            status = check_server_status()
            return JsonResponse({
                'success': True,
                'data': status
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @require_http_methods(["GET"])
    def api_simple_status(request):
        """
        API endpoint simples para status
        """
        return JsonResponse({
            'game_server_online': is_game_server_online(),
            'login_server_online': is_login_server_online(),
            'overall_status': 'online' if (is_game_server_online() and is_login_server_online()) else 'offline'
        })


def exemplo_uso_em_template():
    """
    Exemplo de como usar em um template Django
    """
    # No context processor ou na view:
    def get_server_status_context():
        return {
            'server_status': check_server_status(),
            'is_game_online': is_game_server_online(),
            'is_login_online': is_login_server_online(),
        }
    
    # No template (exemplo):
    template_example = """
    {% if is_game_online %}
        <div class="server-status online">
            <span class="status-indicator"></span>
            <span class="status-text">Servidor Online</span>
        </div>
    {% else %}
        <div class="server-status offline">
            <span class="status-indicator"></span>
            <span class="status-text">Servidor Offline</span>
        </div>
    {% endif %}
    
    <div class="server-details">
        <p>IP: {{ server_status.server_ip }}</p>
        <p>Status Geral: {{ server_status.overall_status }}</p>
        <p>Verificado em: {{ server_status.checked_at }}</p>
    </div>
    """
    
    return template_example


if __name__ == "__main__":
    # Executar exemplos
    exemplo_uso_basico()
    print("\n" + "="*50 + "\n")
    exemplo_uso_avancado() 