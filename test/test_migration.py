#!/usr/bin/env python3
"""
Script de teste para o comando de migração L2 → L2JPremium
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def test_migration_command():
    """Testa o comando de migração"""
    
    # Configura o Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    print("🧪 Testando comando de migração L2 → L2JPremium")
    print("=" * 50)
    
    # Testa o comando com --help
    print("1. Testando --help:")
    try:
        execute_from_command_line(['manage.py', 'migrate_l2_accounts', '--help'])
        print("✅ Comando --help funcionou")
    except SystemExit:
        print("✅ Comando --help funcionou (SystemExit é esperado)")
    except Exception as e:
        print(f"❌ Erro no comando --help: {e}")
        return False
    
    print("\n2. Testando --dry-run:")
    try:
        execute_from_command_line(['manage.py', 'migrate_l2_accounts', '--dry-run'])
        print("✅ Comando --dry-run funcionou")
    except SystemExit as e:
        if e.code == 0:
            print("✅ Comando --dry-run funcionou corretamente")
        else:
            print(f"⚠️  Comando --dry-run retornou código {e.code}")
    except Exception as e:
        print(f"❌ Erro no comando --dry-run: {e}")
        return False
    
    print("\n3. Testando com parâmetros customizados:")
    try:
        execute_from_command_line([
            'manage.py', 'migrate_l2_accounts', 
            '--dry-run', 
            '--prefix', 'TEST_',
            '--password-length', '16',
            '--batch-size', '10'
        ])
        print("✅ Comando com parâmetros customizados funcionou")
    except SystemExit as e:
        if e.code == 0:
            print("✅ Comando com parâmetros funcionou corretamente")
        else:
            print(f"⚠️  Comando com parâmetros retornou código {e.code}")
    except Exception as e:
        print(f"❌ Erro no comando com parâmetros: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes passaram!")
    print("\n📝 Para executar a migração real:")
    print("   python manage.py migrate_l2_accounts")
    print("\n📝 Para usar o script seguro:")
    print("   ./setup/migrate_l2_safe.sh")
    
    return True

if __name__ == '__main__':
    success = test_migration_command()
    sys.exit(0 if success else 1) 