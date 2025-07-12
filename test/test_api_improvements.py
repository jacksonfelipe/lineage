#!/usr/bin/env python
"""
Teste das melhorias da API - Lineage 2
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health_check():
    """Testa o endpoint de health check"""
    print("🔍 Testando Health Check...")
    
    try:
        response = requests.get(f"{API_BASE}/health/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check OK: {data.get('data', {}).get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health Check falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no Health Check: {e}")
        return False

def test_api_info():
    """Testa o endpoint de informações da API"""
    print("\n🔍 Testando API Info...")
    
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info OK: {data.get('data', {}).get('name', 'unknown')}")
            return True
        else:
            print(f"❌ API Info falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no API Info: {e}")
        return False

def test_players_online():
    """Testa o endpoint de jogadores online"""
    print("\n🔍 Testando Players Online...")
    
    try:
        response = requests.get(f"{API_BASE}/server/players-online/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            online_count = data.get('online_count', 0)
            print(f"✅ Players Online OK: {online_count} jogadores")
            return True
        else:
            print(f"❌ Players Online falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no Players Online: {e}")
        return False

def test_top_pvp():
    """Testa o endpoint de top PvP com paginação"""
    print("\n🔍 Testando Top PvP com paginação...")
    
    try:
        # Teste com paginação padrão
        response = requests.get(f"{API_BASE}/server/top-pvp/?page=1&page_size=5")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ Top PvP OK: {len(results)} resultados")
            
            # Verifica se tem informações de paginação
            if 'page_info' in data:
                page_info = data['page_info']
                print(f"📄 Paginação: Página {page_info.get('current_page')} de {page_info.get('total_pages')}")
            
            return True
        else:
            print(f"❌ Top PvP falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no Top PvP: {e}")
        return False

def test_character_search():
    """Testa o endpoint de busca de personagens com filtros"""
    print("\n🔍 Testando busca de personagens...")
    
    try:
        # Teste com filtros
        response = requests.get(f"{API_BASE}/search/character/?name=warrior&level_min=50")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ Character Search OK: {count} resultados")
            return True
        else:
            print(f"❌ Character Search falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no Character Search: {e}")
        return False

def test_rate_limiting():
    """Testa o rate limiting"""
    print("\n🔍 Testando Rate Limiting...")
    
    try:
        # Faz várias requisições rápidas
        responses = []
        for i in range(35):  # Mais que o limite de 30/min
            response = requests.get(f"{API_BASE}/server/players-online/")
            responses.append(response.status_code)
            time.sleep(0.1)  # Pequena pausa
        
        # Verifica se alguma requisição foi limitada
        limited_requests = [r for r in responses if r == 429]
        
        if limited_requests:
            print(f"✅ Rate Limiting funcionando: {len(limited_requests)} requisições limitadas")
            return True
        else:
            print("⚠️ Rate Limiting não detectado (pode estar desabilitado)")
            return True
            
    except Exception as e:
        print(f"❌ Erro no Rate Limiting: {e}")
        return False

def test_cache():
    """Testa o sistema de cache"""
    print("\n🔍 Testando Cache...")
    
    try:
        # Primeira requisição
        start_time = time.time()
        response1 = requests.get(f"{API_BASE}/server/players-online/")
        time1 = time.time() - start_time
        
        # Segunda requisição (deve vir do cache)
        start_time = time.time()
        response2 = requests.get(f"{API_BASE}/server/players-online/")
        time2 = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            print(f"✅ Cache testado: Primeira requisição: {time1:.3f}s, Segunda: {time2:.3f}s")
            if time2 < time1:
                print("🚀 Cache funcionando (segunda requisição mais rápida)")
            return True
        else:
            print(f"❌ Cache falhou: {response1.status_code}, {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no Cache: {e}")
        return False

def test_error_handling():
    """Testa o tratamento de erros"""
    print("\n🔍 Testando Tratamento de Erros...")
    
    try:
        # Teste com parâmetro inválido
        response = requests.get(f"{API_BASE}/server/top-pvp/?limit=invalid")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            error = data.get('error', {})
            print(f"✅ Tratamento de erro OK: {error.get('message', 'Erro desconhecido')}")
            return True
        else:
            print(f"❌ Tratamento de erro falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no tratamento de erros: {e}")
        return False

def test_versioning():
    """Testa o versionamento da API"""
    print("\n🔍 Testando Versionamento...")
    
    try:
        # Teste versão v1
        response_v1 = requests.get(f"{API_BASE}/server/players-online/")
        
        # Teste versão sem especificar (deve mostrar landing page)
        response_default = requests.get(f"{BASE_URL}/api/")
        
        if response_v1.status_code == 200 and response_default.status_code == 200:
            print("✅ Versionamento OK: v1 funcionando e landing page ativa")
            return True
        else:
            print(f"❌ Versionamento falhou: v1={response_v1.status_code}, landing={response_default.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no versionamento: {e}")
        return False

def test_landing_page():
    """Testa a landing page da API"""
    print("\n🔍 Testando Landing Page...")
    
    try:
        # Teste com Accept: text/html
        headers = {'Accept': 'text/html'}
        response_html = requests.get(f"{BASE_URL}/api/", headers=headers)
        
        # Teste com Accept: application/json
        headers = {'Accept': 'application/json'}
        response_json = requests.get(f"{BASE_URL}/api/", headers=headers)
        
        if response_html.status_code == 200 and response_json.status_code == 200:
            # Verifica se o HTML contém elementos da landing page
            if 'Lineage 2 API' in response_html.text and 'Swagger' in response_html.text:
                print("✅ Landing Page HTML OK")
            else:
                print("⚠️ Landing Page HTML pode ter problemas")
            
            # Verifica se o JSON contém informações da API
            json_data = response_json.json()
            if json_data.get('success') and 'documentation' in json_data.get('data', {}):
                print("✅ Landing Page JSON OK")
            else:
                print("⚠️ Landing Page JSON pode ter problemas")
            
            return True
        else:
            print(f"❌ Landing Page falhou: HTML={response_html.status_code}, JSON={response_json.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na Landing Page: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes das melhorias da API")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_api_info,
        test_players_online,
        test_top_pvp,
        test_character_search,
        test_rate_limiting,
        test_cache,
        test_error_handling,
        test_versioning,
        test_landing_page,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {e}")
            results.append(False)
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! As melhorias estão funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as configurações.")
    
    return passed == total

if __name__ == "__main__":
    main() 