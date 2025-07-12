#!/usr/bin/env python3
"""
Teste para a funcionalidade da APIConfigPanelView
"""

import requests
import json
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_config_panel():
    """Testa a funcionalidade da APIConfigPanelView"""
    
    base_url = "http://localhost:8000"  # Ajuste conforme necessário
    
    print("🧪 Testando APIConfigPanelView...")
    
    # Teste 1: Acesso sem autenticação (deve retornar 403)
    print("\n1. Testando acesso sem autenticação...")
    try:
        response = requests.get(f"{base_url}/api/v1/admin/config/panel/")
        if response.status_code == 403:
            print("✅ Acesso negado corretamente para usuários não autenticados")
        else:
            print(f"❌ Status code inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar acesso sem autenticação: {e}")
    
    # Teste 2: Verificar se a rota existe
    print("\n2. Verificando se a rota existe...")
    try:
        response = requests.get(f"{base_url}/api/v1/admin/config/")
        if response.status_code in [200, 403, 401]:
            print("✅ Rota da API de configuração existe")
        else:
            print(f"❌ Rota não encontrada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar rota: {e}")
    
    # Teste 3: Verificar documentação da API
    print("\n3. Verificando documentação da API...")
    try:
        response = requests.get(f"{base_url}/api/v1/schema/")
        if response.status_code == 200:
            print("✅ Documentação da API está disponível")
        else:
            print(f"❌ Documentação não encontrada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar documentação: {e}")
    
    # Teste 4: Verificar endpoints públicos
    print("\n4. Verificando endpoints públicos...")
    endpoints = [
        "/api/v1/server/players-online/",
        "/api/v1/server/top-pvp/",
        "/api/v1/server/top-clan/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code in [200, 503]:  # 503 se endpoint desabilitado
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Erro: {e}")
    
    print("\n🎯 Testes concluídos!")

def test_api_config_endpoints():
    """Testa os endpoints de configuração da API"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔧 Testando endpoints de configuração da API...")
    
    # Lista de endpoints para testar
    config_endpoints = [
        "/api/v1/admin/config/",
        "/api/v1/admin/config/panel/",
    ]
    
    for endpoint in config_endpoints:
        print(f"\nTestando: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 403:
                print("✅ Acesso negado corretamente (requer autenticação)")
            elif response.status_code == 200:
                print("✅ Endpoint acessível")
                try:
                    data = response.json()
                    print(f"Dados: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print("Resposta não é JSON (provavelmente HTML)")
            else:
                print(f"❌ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da APIConfigPanelView...")
    
    test_api_config_panel()
    test_api_config_endpoints()
    
    print("\n✨ Todos os testes foram executados!")
    print("\n📝 Para testar com autenticação, você precisará:")
    print("1. Fazer login como administrador")
    print("2. Acessar /api/v1/admin/config/panel/")
    print("3. Verificar se consegue alterar as configurações") 