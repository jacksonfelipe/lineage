#!/usr/bin/env python
"""
Exemplo de teste do sistema de moderação
Este script demonstra como os filtros funcionam na prática
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.main.social.models import ContentFilter, Post, Report
from django.contrib.auth import get_user_model

User = get_user_model()

def test_content_filters():
    """Testa filtros de conteúdo com exemplos reais"""
    
    print("🧪 TESTANDO SISTEMA DE MODERAÇÃO")
    print("=" * 50)
    
    # Exemplos de conteúdo para testar
    test_cases = [
        # Spam comercial
        ("Ganhe dinheiro fácil! Clique aqui agora!", "SPAM_COMERCIAL"),
        
        # Palavrões em português
        ("Que merda de situação!", "PALAVRAO_MODERADO"),
        
        # Conteúdo pornográfico
        ("Vem ver minhas nudes no link", "CONTEUDO_ADULTO"),
        
        # URLs suspeitas
        ("Acesse bit.ly/link-suspeito para ganhar prêmio", "URL_SUSPEITA"),
        
        # Discurso de ódio
        ("Esses negros não prestam mesmo", "DISCURSO_ODIO"),
        
        # Fake news
        ("Vacina mata mais que cura, não tomem!", "FAKE_NEWS"),
        
        # Comportamento suspeito - CAPS
        ("ATENÇÃO URGENTE TODOS LEIAM AGORA MESMO", "CAPS_EXCESSIVO"),
        
        # Golpes brasileiros
        ("PIX grátis! Auxílio emergencial liberado", "GOLPE_BRASILEIRO"),
        
        # Conteúdo normal (não deve ser filtrado)
        ("Boa tarde pessoal! Como estão hoje?", "CONTEUDO_NORMAL"),
    ]
    
    # Obter filtros ativos
    active_filters = ContentFilter.objects.filter(is_active=True)
    print(f"📊 Filtros ativos: {active_filters.count()}")
    print()
    
    # Testar cada caso
    for content, category in test_cases:
        print(f"🔍 Testando: {category}")
        print(f"   Texto: \"{content}\"")
        
        matched_filters = []
        
        # Verificar contra todos os filtros
        for content_filter in active_filters:
            if content_filter.matches_content(content):
                matched_filters.append({
                    'name': content_filter.name,
                    'action': content_filter.action,
                    'type': content_filter.filter_type
                })
        
        if matched_filters:
            print(f"   ⚠️  FILTRADO! ({len(matched_filters)} filtros)")
            for match in matched_filters:
                print(f"      • {match['name']} ({match['type']}) → {match['action']}")
        else:
            print(f"   ✅ APROVADO")
        
        print()

def test_filter_performance():
    """Testa performance dos filtros"""
    import time
    
    print("⚡ TESTE DE PERFORMANCE")
    print("=" * 30)
    
    # Conteúdo de teste
    test_content = "Este é um texto normal para testar a velocidade dos filtros de moderação."
    
    active_filters = ContentFilter.objects.filter(is_active=True)
    
    # Teste de velocidade
    start_time = time.time()
    iterations = 1000
    
    for i in range(iterations):
        for content_filter in active_filters:
            content_filter.matches_content(test_content)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"📊 Resultados:")
    print(f"   • Filtros testados: {active_filters.count()}")
    print(f"   • Iterações: {iterations}")
    print(f"   • Tempo total: {total_time:.3f}s")
    print(f"   • Tempo por verificação: {(total_time / (iterations * active_filters.count()) * 1000):.2f}ms")
    print(f"   • Verificações por segundo: {int((iterations * active_filters.count()) / total_time)}")

def create_test_content():
    """Cria conteúdo de teste para demonstração"""
    
    print("📝 CRIANDO CONTEÚDO DE TESTE")
    print("=" * 35)
    
    # Criar usuário de teste se não existir
    test_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        print("✅ Usuário de teste criado")
    else:
        print("ℹ️  Usando usuário de teste existente")
    
    # Exemplos de posts que serão filtrados
    filtered_posts = [
        "Compre agora com desconto! Link: bit.ly/oferta",
        "Que porra é essa?",
        "Vem ver meu conteúdo adulto no link",
        "ATENÇÃO URGENTE! CLIQUE AQUI AGORA!",
    ]
    
    # Criar posts de teste
    for content in filtered_posts:
        post = Post.objects.create(
            author=test_user,
            content=content,
            is_public=True
        )
        print(f"📄 Post criado: ID {post.id}")
    
    print(f"\n✅ {len(filtered_posts)} posts de teste criados")

def generate_moderation_report():
    """Gera relatório de moderação"""
    
    print("📋 RELATÓRIO DE MODERAÇÃO")
    print("=" * 30)
    
    # Estatísticas gerais
    total_filters = ContentFilter.objects.count()
    active_filters = ContentFilter.objects.filter(is_active=True).count()
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='pending').count()
    
    print(f"📊 Estatísticas Gerais:")
    print(f"   • Total de filtros: {total_filters}")
    print(f"   • Filtros ativos: {active_filters}")
    print(f"   • Total de denúncias: {total_reports}")
    print(f"   • Denúncias pendentes: {pending_reports}")
    
    # Filtros por categoria
    print(f"\n🎯 Filtros por Tipo:")
    filter_types = ContentFilter.objects.filter(is_active=True).values_list('filter_type', flat=True)
    type_counts = {}
    for f_type in filter_types:
        type_counts[f_type] = type_counts.get(f_type, 0) + 1
    
    for f_type, count in type_counts.items():
        print(f"   • {f_type}: {count}")
    
    # Filtros por ação
    print(f"\n⚡ Filtros por Ação:")
    actions = ContentFilter.objects.filter(is_active=True).values_list('action', flat=True)
    action_counts = {}
    for action in actions:
        action_counts[action] = action_counts.get(action, 0) + 1
    
    for action, count in action_counts.items():
        print(f"   • {action}: {count}")

if __name__ == "__main__":
    print("🛡️  SISTEMA DE MODERAÇÃO - TESTE COMPLETO")
    print("=" * 60)
    print()
    
    try:
        # Executar testes
        test_content_filters()
        print()
        
        test_filter_performance()
        print()
        
        generate_moderation_report()
        print()
        
        # Oferecer criação de conteúdo de teste
        response = input("Deseja criar posts de teste? (y/N): ")
        if response.lower() in ['y', 'yes', 's', 'sim']:
            create_test_content()
        
        print("\n✅ Testes concluídos com sucesso!")
        print("\n📋 Próximos passos:")
        print("   1. Acesse /admin/social/contentfilter/ para gerenciar filtros")
        print("   2. Configure ações automáticas conforme necessário")
        print("   3. Monitore logs de moderação regularmente")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
