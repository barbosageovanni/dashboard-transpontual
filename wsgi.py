#!/usr/bin/env python3
import os
import sys

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
                
        except Exception as e:
            print(f"⚠️ Init: {e}")
            
except Exception as e:
    print(f"❌ Erro crítico: {e}")
    # Fallback básico
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def erro():
        return f"<h1>⚠️ Sistema em configuração</h1><p>Erro: {e}</p>"

# Exportar app para Gunicorn
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
