#!/usr/bin/env python3
import os
import sys
import traceback

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')

# URL Supabase - vamos testar diferentes formatos
SUPABASE_URLS = [
    'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres',
    'postgresql://postgres.lijtncazuwnbydeqtoyz:Mariaana953%407334@aws-0-sa-east-1.pooler.supabase.com:5432/postgres',
    'postgresql://postgres.lijtncazuwnbydeqtoyz:Mariaana953%407334@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'
]

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_supabase_connection():
    """Testar diferentes URLs Supabase"""
    import psycopg2
    
    for i, url in enumerate(SUPABASE_URLS):
        try:
            print(f"🔄 Testando URL {i+1}: {url[:50]}...")
            conn = psycopg2.connect(url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"✅ Conexão {i+1} OK: PostgreSQL {version[0][:30]}...")
            return url
        except Exception as e:
            print(f"❌ URL {i+1} falhou: {str(e)[:100]}")
    
    return None

def create_complete_app():
    """Carregar aplicação Flask completa original"""
    print("🔄 Carregando sistema Flask completo...")
    
    # Testar conexão primeiro
    working_url = test_supabase_connection()
    
    if not working_url:
        raise Exception("Nenhuma URL Supabase funciona")
    
    # Configurar URL que funciona
    os.environ['DATABASE_URL'] = working_url
    
    # Importar aplicação original
    from app import create_app, db
    from config import ProductionConfig
    
    # Criar app completa
    application = create_app(ProductionConfig)
    
    # Inicializar banco
    with application.app_context():
        print("🔄 Inicializando banco de dados...")
        
        # Criar tabelas
        db.create_all()
        print("✅ Tabelas criadas/verificadas")
        
        # Criar usuário admin
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
            print("✅ Admin já existe")
    
    print("✅ Sistema Flask completo carregado!")
    return application

def create_fallback_app():
    """App básica caso Supabase falhe"""
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return '''
        <h1>⚠️ Erro de Conexão Supabase</h1>
        <p>Todas as URLs testadas falharam:</p>
        <ul>''' + ''.join([f'<li>{url[:80]}...</li>' for url in SUPABASE_URLS]) + '''</ul>
        <p>Verifique:</p>
        <ol>
            <li>Projeto Supabase ativo</li>
            <li>Credenciais corretas</li>
            <li>URL connection string atualizada</li>
        </ol>
        '''
    
    return app

# Tentar carregar sistema completo
try:
    print("🚀 Iniciando Dashboard Baker - Sistema Completo")
    application = create_complete_app()
    print("🎉 SUCESSO: Sistema completo funcionando!")
    
except Exception as e:
    print(f"❌ Erro sistema completo: {e}")
    print("📋 Traceback:")
    traceback.print_exc()
    print("🔄 Carregando fallback...")
    application = create_fallback_app()

# Exportar para Gunicorn
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
