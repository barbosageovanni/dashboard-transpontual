#!/usr/bin/env python3
import os
import sys

# URLs para testar (incluindo variações)
SUPABASE_URLS = [
    'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres',
    'postgresql://postgres.lijtncazuwnbydeqtoyz:Mariaana953%407334@aws-0-sa-east-1.pooler.supabase.com:5432/postgres',
    'postgresql://postgres.lijtncazuwnbydeqtoyz:Mariaana953%407334@aws-0-sa-east-1.pooler.supabase.com:6543/postgres',
    'postgresql://postgres.lijtncazuwnbydeqtoyz:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres'
]

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connections():
    """Testa todas as URLs para encontrar a que funciona"""
    import psycopg2
    
    print("🔄 Testando conexões Supabase...")
    
    for i, url in enumerate(SUPABASE_URLS, 1):
        try:
            print(f"🔄 Testando URL {i}: {url[:70]}...")
            
            conn = psycopg2.connect(url)
            cursor = conn.cursor()
            
            # Teste básico
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Verificar se nossas tabelas existem
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'cte';")
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM cte;")
                cte_count = cursor.fetchone()[0]
                print(f"✅ URL {i} FUNCIONOU! CTEs encontrados: {cte_count}")
            else:
                print(f"⚠️ URL {i} conectou mas tabela CTE não encontrada")
            
            cursor.close()
            conn.close()
            
            return url, table_exists
            
        except Exception as e:
            print(f"❌ URL {i} falhou: {str(e)[:100]}")
    
    return None, False

def create_app_with_database():
    """Cria app com banco funcionando"""
    working_url, has_tables = test_database_connections()
    
    if not working_url:
        raise Exception("Nenhuma URL Supabase funcionou")
    
    print(f"✅ Usando URL funcionando: {working_url[:50]}...")
    os.environ['DATABASE_URL'] = working_url
    
    from app import create_app, db
    from config import ProductionConfig
    
    application = create_app(ProductionConfig)
    
    with application.app_context():
        if has_tables:
            print("✅ Tabelas encontradas! Dados preservados!")
            
            # Verificar dados
            from app.models.cte import CTE
            total_ctes = CTE.query.count()
            print(f"✅ Total CTEs no banco: {total_ctes}")
            
            # Criar admin se necessário
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@transpontual.app.br',
                    nome_completo='Administrador Sistema',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin criado")
            else:
                print("✅ Admin existe")
        else:
            print("⚠️ Tabelas não encontradas - pode precisar recriar")
            db.create_all()
    
    return application

def create_offline_app():
    """App offline como fallback"""
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def status():
        return '''
        <h1>🔧 Diagnóstico de Conexão</h1>
        <p>Todas as URLs Supabase testadas falharam.</p>
        <h3>Verificar:</h3>
        <ol>
            <li>Projeto Supabase ativo: https://supabase.com/dashboard</li>
            <li>Status do projeto: Active ou Paused?</li>
            <li>Billing: Problemas de pagamento?</li>
            <li>Nova URL conexão: Settings → Database</li>
        </ol>
        <p><strong>Seus dados estão seguros no Supabase!</strong></p>
        '''
    
    return app

# Tentar recuperar conexão com banco
print("🔧 RECOVERY MODE: Tentando recuperar conexão Supabase...")

try:
    application = create_app_with_database()
    print("🎉 SUCESSO! Sistema com banco restaurado!")
    
except Exception as e:
    print(f"❌ Falha na recuperação: {e}")
    print("🔄 Iniciando modo diagnóstico...")
    application = create_offline_app()

# Exportar app
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
