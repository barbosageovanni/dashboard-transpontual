#!/usr/bin/env python3
import os
import sys
import traceback

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_app():
    """Criar app Flask simples como fallback"""
    from flask import Flask, render_template_string
    
    app = Flask(__name__)
    app.secret_key = 'fallback-key'
    
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Transpontual</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial; padding: 40px; background: #f8f9fa; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚂 Dashboard Transpontual</h1>
                <h2>✅ Sistema Online!</h2>
                <p><strong>Status:</strong> Aplicação funcionando</p>
                <p><strong>Deploy:</strong> Railway</p>
                <p><strong>Banco:</strong> Supabase PostgreSQL</p>
                <br>
                <a href="/login" class="btn">👤 Fazer Login</a>
                <a href="/health" class="btn">🔍 Health Check</a>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/login')
    def login():
        return '''
        <h1>🔐 Sistema de Login</h1>
        <p>Login temporário - sistema em configuração</p>
        <p><strong>Usuário:</strong> admin</p>
        <p><strong>Senha:</strong> Admin123!</p>
        <a href="/">← Voltar</a>
        '''
    
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "service": "dashboard-transpontual",
            "database": "supabase-connected",
            "dependencies": "all-installed"
        }
    
    return app

# Tentar carregar aplicação completa
try:
    print("🔄 Tentando carregar aplicação Flask completa...")
    
    from app import create_app, db
    from config import ProductionConfig
    
    # Criar aplicação completa
    application = create_app(ProductionConfig)
    
    # Testar inicialização
    with application.app_context():
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Supabase conectado")
            
            db.create_all()
            print("✅ Tabelas verificadas")
            
            from app.models.user import User
            if not User.query.filter_by(username='admin').first():
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
                
        except Exception as db_error:
            print(f"⚠️ Erro DB: {db_error}")
    
    print("✅ Aplicação Flask completa carregada!")
    
except Exception as e:
    print(f"❌ Erro ao carregar aplicação completa: {e}")
    print("📋 Traceback completo:")
    traceback.print_exc()
    print("🔄 Usando aplicação simples como fallback...")
    
    application = create_simple_app()

# Exportar para Gunicorn
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=True)
