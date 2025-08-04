#!/usr/bin/env python3
"""
Teste simples para verificar o sistema de captcha no login
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

class CaptchaLoginTest(TestCase):
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Limpa o cache antes de cada teste
        cache.clear()
    
    def test_login_without_captcha_initially(self):
        """Testa que o login não exige captcha inicialmente"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        
        # Verifica se o captcha não está no contexto
        self.assertNotIn('requires_captcha', response.context)
    
    def test_login_attempts_tracking(self):
        """Testa o rastreamento de tentativas de login"""
        from middlewares.login_attempts import LoginAttemptsMiddleware
        
        # Simula tentativas de login falhadas
        for i in range(3):
            response = self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            
            # Verifica se as tentativas estão sendo contadas
            attempts = LoginAttemptsMiddleware.get_login_attempts(self.client.request)
            self.assertEqual(attempts, i + 1)
    
    def test_captcha_required_after_max_attempts(self):
        """Testa que o captcha é exigido após o número máximo de tentativas"""
        from middlewares.login_attempts import LoginAttemptsMiddleware
        
        # Simula tentativas de login falhadas até o limite
        for i in range(3):
            self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Verifica se o captcha é necessário
        requires_captcha = LoginAttemptsMiddleware.requires_captcha(self.client.request)
        self.assertTrue(requires_captcha)
        
        # Verifica se o template mostra o captcha
        response = self.client.get('/login/')
        self.assertIn('requires_captcha', response.context)
        self.assertTrue(response.context['requires_captcha'])
    
    def test_login_success_resets_attempts(self):
        """Testa que o login bem-sucedido reseta as tentativas"""
        from middlewares.login_attempts import LoginAttemptsMiddleware
        
        # Simula algumas tentativas falhadas
        for i in range(2):
            self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Faz login com sucesso
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verifica se as tentativas foram resetadas
        attempts = LoginAttemptsMiddleware.get_login_attempts(self.client.request)
        self.assertEqual(attempts, 0)
    
    def test_captcha_validation(self):
        """Testa a validação do captcha"""
        from apps.main.home.views.accounts import verificar_hcaptcha
        
        # Testa com token inválido
        result = verificar_hcaptcha('invalid_token')
        self.assertFalse(result)
    
    def test_configurable_max_attempts(self):
        """Testa que o número máximo de tentativas é configurável"""
        from django.conf import settings
        
        # Verifica se a configuração existe
        self.assertTrue(hasattr(settings, 'LOGIN_MAX_ATTEMPTS'))
        self.assertIsInstance(settings.LOGIN_MAX_ATTEMPTS, int)
        self.assertGreater(settings.LOGIN_MAX_ATTEMPTS, 0)

if __name__ == '__main__':
    # Executa os testes
    import unittest
    unittest.main() 