#!/usr/bin/env python3
import os
import sys

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Variável global para armazenar erros
app_error = None

try:
    from app import create_app, db
    from config import ProductionConfig
    
    # Criar aplicação Flask completa
    application = create_app(ProductionConfig)
    
    # Inicializar banco
    with application.app_context():
        try:
            db.session.execute("SELECT 1")
            print("✅ Supabase conectado")
            
            # Criar tabelas
            db.create_all()
            print("✅ Tabelas criadas")
            
            # Criar admin
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
                
        except Exception as init_error:
            print(f"⚠️ Init: {init_error}")
            
except Exception as error:
    print(f"❌ Erro crítico: {error}")
    app_error = str(error)
    
    # Fallback básico
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def home():
        return f'''
        <html>
        <head><title>Sistema Transpontual</title></head>
        <body style="font-family: Arial; padding: 40px; background: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h1>⚠️ Sistema em Configuração</h1>
                <p><strong>Status:</strong> Dependências sendo instaladas</p>
                <p><strong>Erro:</strong> {app_error}</p>
                <p><strong>Ação:</strong> Aguarde conclusão do deploy</p>
                <hr>
                <p><small>Dashboard Transpontual - Railway Deploy</small></p>
            </div>
        </body>
        </html>
        '''

# Exportar app para Gunicorn  
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
