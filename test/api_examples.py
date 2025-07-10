#!/usr/bin/env python3
"""
Exemplos de uso da API Lineage 2
Este arquivo demonstra como usar os endpoints da API
"""

import requests
import json
from datetime import datetime

# Configurações da API
BASE_URL = "http://localhost:80/api/v1"
API_KEY = None  # Para APIs que precisam de autenticação

class Lineage2API:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
    
    def set_auth_headers(self):
        """Define headers de autenticação"""
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
    
    def login(self, username, password):
        """Realiza login e obtém tokens JWT"""
        url = f"{self.base_url}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result.get('access')
            self.refresh_token = result.get('refresh')
            
            # Define headers para próximas requisições
            self.set_auth_headers()
            
            print(f"✅ Login realizado com sucesso para {username}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro no login: {e}")
            return None
    
    def refresh_access_token(self):
        """Atualiza o token de acesso"""
        if not self.refresh_token:
            print("❌ Nenhum refresh token disponível")
            return False
        
        url = f"{self.base_url}/auth/refresh/"
        data = {"refresh": self.refresh_token}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result.get('access')
            self.set_auth_headers()
            
            print("✅ Token atualizado com sucesso")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao atualizar token: {e}")
            return False
    
    def logout(self):
        """Realiza logout"""
        if not self.refresh_token:
            print("❌ Nenhum refresh token disponível")
            return False
        
        url = f"{self.base_url}/auth/logout/"
        data = {"refresh": self.refresh_token}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            # Limpa tokens
            self.access_token = None
            self.refresh_token = None
            self.session.headers.pop('Authorization', None)
            
            print("✅ Logout realizado com sucesso")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro no logout: {e}")
            return False
    
    def get_server_status(self):
        """Obtém status do servidor"""
        url = f"{self.base_url}/server/status/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter status do servidor: {e}")
            return None
    
    def get_players_online(self):
        """Obtém número de jogadores online"""
        url = f"{self.base_url}/server/players-online/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter jogadores online: {e}")
            return None
    
    def get_top_pvp(self, limit=10):
        """Obtém ranking PvP"""
        url = f"{self.base_url}/server/top-pvp/"
        params = {"limit": limit}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter ranking PvP: {e}")
            return None
    
    def search_character(self, query):
        """Busca personagens"""
        url = f"{self.base_url}/search/character/"
        params = {"q": query}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na busca de personagens: {e}")
            return None
    
    def search_item(self, query):
        """Busca itens"""
        url = f"{self.base_url}/search/item/"
        params = {"q": query}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na busca de itens: {e}")
            return None
    
    def get_clan_details(self, clan_name):
        """Obtém detalhes de um clã"""
        url = f"{self.base_url}/clan/{clan_name}/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter detalhes do clã: {e}")
            return None
    
    def get_auction_items(self, limit=20):
        """Obtém itens do leilão"""
        url = f"{self.base_url}/auction/items/"
        params = {"limit": limit}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter itens do leilão: {e}")
            return None
    
    def get_user_profile(self):
        """Obtém perfil do usuário logado"""
        if not self.access_token:
            print("❌ Usuário não autenticado")
            return None
        
        url = f"{self.base_url}/user/profile/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter perfil do usuário: {e}")
            return None
    
    def get_user_dashboard(self):
        """Obtém dashboard do usuário logado"""
        if not self.access_token:
            print("❌ Usuário não autenticado")
            return None
        
        url = f"{self.base_url}/user/dashboard/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter dashboard: {e}")
            return None


def print_json(data, title=""):
    """Imprime dados JSON formatados"""
    if title:
        print(f"\n{'='*50}")
        print(f"📋 {title}")
        print(f"{'='*50}")
    
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """Função principal com exemplos de uso"""
    print("🚀 Exemplos de uso da API Lineage 2")
    print("="*50)
    
    # Inicializa API
    api = Lineage2API()
    
    # 1. Status do servidor (público)
    print("\n1️⃣ Testando endpoints públicos...")
    
    status = api.get_server_status()
    if status:
        print_json(status, "Status do Servidor")
    
    players = api.get_players_online()
    if players:
        print_json(players, "Jogadores Online")
    
    top_pvp = api.get_top_pvp(limit=5)
    if top_pvp:
        print_json(top_pvp, "Top 5 PvP")
    
    # 2. Busca de dados (público)
    print("\n2️⃣ Testando busca de dados...")
    
    characters = api.search_character("Hero")
    if characters:
        print_json(characters, "Busca de Personagens")
    
    items = api.search_item("Sword")
    if items:
        print_json(items, "Busca de Itens")
    
    clan = api.get_clan_details("TestClan")
    if clan:
        print_json(clan, "Detalhes do Clã")
    
    auction = api.get_auction_items(limit=5)
    if auction:
        print_json(auction, "Itens do Leilão")
    
    # 3. Autenticação (exemplo)
    print("\n3️⃣ Testando autenticação...")
    print("⚠️  Para testar endpoints autenticados, descomente as linhas abaixo:")
    
    # Descomente para testar login (substitua com suas credenciais)
    # login_result = api.login("seu_usuario", "sua_senha")
    # if login_result:
    #     print_json(login_result, "Login Resultado")
    #     
    #     # Testa endpoints autenticados
    #     profile = api.get_user_profile()
    #     if profile:
    #         print_json(profile, "Perfil do Usuário")
    #     
    #     dashboard = api.get_user_dashboard()
    #     if dashboard:
    #         print_json(dashboard, "Dashboard do Usuário")
    #     
    #     # Logout
    #     api.logout()
    
    print("\n✅ Testes concluídos!")
    print("\n📖 Para mais informações, acesse:")
    print("   - Documentação: http://localhost:80/api/v1/schema/swagger/")
    print("   - ReDoc: http://localhost:80/api/v1/schema/redoc/")


if __name__ == "__main__":
    main() 
    