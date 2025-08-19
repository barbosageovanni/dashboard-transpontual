#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corretor de Conexão - Dashboard Baker Flask
Corrige problemas de string de conexão com caracteres especiais
"""

import os
from urllib.parse import quote_plus

def corrigir_conexao():
    """Corrige a configuração de conexão"""
    
    print("🔧 Corrigindo configuração de conexão...")
    
    # Configurações corretas
    config = {
        'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
        'port': '5432',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Mariaana953@7334'  # Senha original
    }
    
    # Criar .env corrigido
    env_content = f"""# Dashboard Baker Flask - Configurações CORRIGIDAS
SECRET_KEY={os.urandom(32).hex()}

# Database - Componentes separados
DB_HOST={config['host']}
DB_PORT={config['port']}
DB_NAME={config['database']}
DB_USER={config['user']}
DB_PASSWORD={config['password']}

# URL completa (com encoding)
DATABASE_URL=postgresql://{config['user']}:{quote_plus(config['password'])}@{config['host']}:{config['port']}/{config['database']}

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("   ✅ Arquivo .env corrigido")
    
    # Testar conexão
    testar_conexao_corrigida(config)

def testar_conexao_corrigida(config):
    """Testa a conexão corrigida"""
    try:
        import psycopg2
        
        print("🧪 Testando conexão corrigida...")
        
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
        total_ctes = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"   ✅ Conexão OK - {total_ctes} CTEs encontrados")
        
    except Exception as e:
        print(f"   ❌ Erro na conexão: {str(e)}")

if __name__ == "__main__":
    corrigir_conexao()