#!/usr/bin/env python3
import os
import sys

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Configurar logging para produção (REDUZIR LOGS)
import logging
logging.getLogger().setLevel(logging.WARNING)  # Apenas warnings e erros
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)  # Reduzir logs SQL

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from config import ProductionConfig
    
    # Criar aplicação
    application = create_app(ProductionConfig)
    
    # Inicializar banco SEM logs excessivos
    with application.app_context():
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Supabase conectado")
            
            db.create_all()
            
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
            
        except Exception as e:
            print(f"⚠️ Init: {e}")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def erro():
        return f"<h1>⚠️ Sistema em manutenção</h1><p>Erro: {e}</p>"

# Exportar app
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
