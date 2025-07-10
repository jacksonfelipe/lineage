#!/usr/bin/env python3
"""
Script para testar TODOS os endpoints da API - Lineage 2 PDL
"""

import requests
import json
import time
from typing import Dict, List, Any

class CompleteAPITester:
    def __init__(self, base_url: str = "http://127.0.0.1:80"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
        # Todos os endpoints da API
        self.endpoints = [
            # Endpoints já testados (tops)
            ('/api/v1/server/players-online/', 'Players Online', {}),
            ('/api/v1/server/top-pvp/', 'Top PvP', {}),
            ('/api/v1/server/top-pk/', 'Top PK', {}),
            ('/api/v1/server/top-clan/', 'Top Clan', {}),
            ('/api/v1/server/top-rich/', 'Top Rich', {}),
            ('/api/v1/server/top-online/', 'Top Online', {}),
            ('/api/v1/server/top-level/', 'Top Level', {}),
            
            # Novos endpoints (olympiad)
            ('/api/v1/server/olympiad-ranking/', 'Olympiad Ranking', {}),
            ('/api/v1/server/olympiad-heroes/', 'Olympiad All Heroes', {}),
            ('/api/v1/server/olympiad-current-heroes/', 'Olympiad Current Heroes', {}),
            
            # Endpoints de boss e siege
            ('/api/v1/server/grandboss-status/', 'Grand Boss Status', {}),
            ('/api/v1/server/siege/', 'Siege Status', {}),
            ('/api/v1/server/siege-participants/1/', 'Siege Participants (Castle 1)', {}),
            ('/api/v1/server/siege-participants/2/', 'Siege Participants (Castle 2)', {}),
            ('/api/v1/server/siege-participants/3/', 'Siege Participants (Castle 3)', {}),
            ('/api/v1/server/siege-participants/4/', 'Siege Participants (Castle 4)', {}),
            ('/api/v1/server/siege-participants/5/', 'Siege Participants (Castle 5)', {}),
            ('/api/v1/server/siege-participants/6/', 'Siege Participants (Castle 6)', {}),
            ('/api/v1/server/siege-participants/7/', 'Siege Participants (Castle 7)', {}),
            ('/api/v1/server/siege-participants/8/', 'Siege Participants (Castle 8)', {}),
            ('/api/v1/server/siege-participants/9/', 'Siege Participants (Castle 9)', {}),
            
            # Endpoint de boss jewels (com parâmetros)
            ('/api/v1/server/boss-jewel-locations/?ids=6656,6657', 'Boss Jewel Locations (IDs 6656,6657)', {}),
            ('/api/v1/server/boss-jewel-locations/?ids=6658,6659,6660', 'Boss Jewel Locations (IDs 6658,6659,6660)', {}),
            ('/api/v1/server/boss-jewel-locations/?ids=6661,8191', 'Boss Jewel Locations (IDs 6661,8191)', {}),
        ]
    
    def test_endpoint(self, endpoint: str, description: str, params: Dict) -> Dict[str, Any]:
        """Testa um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"🔍 Testando: {description}")
        print(f"   URL: {url}")
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            
            result = {
                "endpoint": endpoint,
                "description": description,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200,
                "error": None,
                "data_info": {}
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["data_info"] = {
                        "type": type(data).__name__,
                        "length": len(data) if isinstance(data, (list, dict)) else None,
                        "sample_keys": list(data.keys()) if isinstance(data, dict) and data else None,
                        "first_item_keys": list(data[0].keys()) if isinstance(data, list) and data else None
                    }
                    print(f"   ✅ Status: {response.status_code} | Tipo: {result['data_info']['type']} | Tempo: {result['response_time']:.2f}s")
                    
                    # Mostra exemplo de dados se disponível
                    if isinstance(data, list) and data:
                        print(f"   📊 Items: {len(data)} | Exemplo: {list(data[0].keys()) if data[0] else 'N/A'}")
                    elif isinstance(data, dict) and data:
                        print(f"   📊 Keys: {list(data.keys())}")
                        
                except json.JSONDecodeError:
                    result["error"] = "Resposta não é JSON válido"
                    print(f"   ⚠️ Status: {response.status_code} | Erro: Resposta não é JSON válido")
                    
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    result["error"] = error_data.get('error', 'Bad Request')
                    print(f"   ❌ Status: {response.status_code} | Erro: {result['error']}")
                except:
                    result["error"] = "Bad Request"
                    print(f"   ❌ Status: {response.status_code} | Erro: Bad Request")
                    
            elif response.status_code == 404:
                result["error"] = "Endpoint não encontrado"
                print(f"   ❌ Status: {response.status_code} | Erro: Endpoint não encontrado")
                
            elif response.status_code == 500:
                result["error"] = "Erro interno do servidor"
                print(f"   ❌ Status: {response.status_code} | Erro: Erro interno do servidor")
                
            else:
                result["error"] = f"Status code {response.status_code}"
                print(f"   ❌ Status: {response.status_code} | Erro: Status code inesperado")
                
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
            print(f"   ❌ Timeout: Requisição demorou mais de 15 segundos")
            
        except requests.exceptions.ConnectionError:
            result["error"] = "Erro de conexão"
            print(f"   ❌ Erro: Não foi possível conectar ao servidor")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Erro: {str(e)}")
        
        return result
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Executa todos os testes"""
        print("🚀 Iniciando teste completo de todos os endpoints da API")
        print("=" * 80)
        
        for endpoint, description, params in self.endpoints:
            result = self.test_endpoint(endpoint, description, params)
            self.results.append(result)
            
            # Pequena pausa entre requisições
            time.sleep(0.5)
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo dos testes"""
        total_endpoints = len(self.results)
        successful_endpoints = sum(1 for r in self.results if r['success'])
        failed_endpoints = total_endpoints - successful_endpoints
        
        # Agrupa por categoria
        categories = {
            'tops': [],
            'olympiad': [],
            'boss_siege': [],
            'boss_jewels': []
        }
        
        for result in self.results:
            endpoint = result['endpoint']
            if 'top-' in endpoint or 'players-online' in endpoint:
                categories['tops'].append(result)
            elif 'olympiad' in endpoint:
                categories['olympiad'].append(result)
            elif 'boss-jewel' in endpoint:
                categories['boss_jewels'].append(result)
            else:
                categories['boss_siege'].append(result)
        
        # Estatísticas por categoria
        category_stats = {}
        for category, results in categories.items():
            total = len(results)
            successful = sum(1 for r in results if r['success'])
            category_stats[category] = {
                'total': total,
                'successful': successful,
                'failed': total - successful,
                'success_rate': (successful / total * 100) if total > 0 else 0
            }
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_endpoints': total_endpoints,
                'successful_endpoints': successful_endpoints,
                'failed_endpoints': failed_endpoints,
                'success_rate': (successful_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
            },
            'category_stats': category_stats,
            'results': self.results,
            'failed_endpoints': [r for r in self.results if not r['success']],
            'successful_endpoints': [r for r in self.results if r['success']]
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Imprime relatório formatado"""
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO COMPLETO - TODOS OS ENDPOINTS DA API")
        print("=" * 80)
        
        summary = report['summary']
        print(f"\n📊 RESUMO GERAL:")
        print(f"   Total de endpoints: {summary['total_endpoints']}")
        print(f"   Endpoints funcionando: {summary['successful_endpoints']}")
        print(f"   Endpoints com falha: {summary['failed_endpoints']}")
        print(f"   Taxa de sucesso: {summary['success_rate']:.1f}%")
        
        print(f"\n📈 ESTATÍSTICAS POR CATEGORIA:")
        for category, stats in report['category_stats'].items():
            category_name = {
                'tops': '🏆 Rankings (Tops)',
                'olympiad': '🏅 Olimpíada',
                'boss_siege': '👹 Bosses e Sieges',
                'boss_jewels': '💎 Boss Jewels'
            }.get(category, category.title())
            
            print(f"   {category_name}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        if report['failed_endpoints']:
            print(f"\n❌ ENDPOINTS COM FALHA:")
            for result in report['failed_endpoints']:
                print(f"   • {result['description']}: {result.get('error', 'Erro desconhecido')}")
        
        print(f"\n✅ ENDPOINTS FUNCIONANDO:")
        for result in report['successful_endpoints']:
            data_info = result['data_info']
            print(f"   • {result['description']}: {data_info.get('type', 'N/A')} ({data_info.get('length', 'N/A')} items)")
        
        print(f"\n💡 RECOMENDAÇÕES:")
        if summary['success_rate'] == 100:
            print("   🎉 TODAS AS APIS ESTÃO FUNCIONANDO PERFEITAMENTE!")
        elif summary['success_rate'] >= 80:
            print("   ✅ A maioria das APIs está funcionando bem")
            print("   🔧 Verifique os endpoints com falha")
        else:
            print("   ⚠️ Muitos endpoints com problemas")
            print("   🔧 Verifique a configuração do servidor")
            print("   🔧 Confirme se todos os módulos estão habilitados")
        
        # Salva relatório
        filename = f"complete_api_test_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório completo salvo em: {filename}")

def main():
    """Função principal"""
    print("🔧 Teste Completo de TODOS os Endpoints da API - Lineage 2 PDL")
    print("=" * 80)
    
    # Solicita URL base
    base_url = input("Digite a URL base do servidor (padrão: http://127.0.0.1:80): ").strip()
    if not base_url:
        base_url = "http://127.0.0.1:80"
    
    # Cria tester e executa testes
    tester = CompleteAPITester(base_url)
    results = tester.run_all_tests()
    
    # Gera e exibe relatório
    report = tester.generate_report()
    tester.print_report(report)

if __name__ == "__main__":
    main()
