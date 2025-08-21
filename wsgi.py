#!/usr/bin/env python3
import os
import sys

# DESABILITAR LOGS COMPLETAMENTE
import logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from config import ProductionConfig
    
    # Criar aplicação
    application = create_app(ProductionConfig)
    
    # Inicializar banco SEM LOGS
    with application.app_context():
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            # SEM PRINT - estava causando logs excessivos
            
            db.create_all()
            
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@transpontual.app.br',
                    nome_completo='Administrador Transpontual',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
            
        except Exception as e:
            pass  # SEM LOGS
            
except Exception as e:
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def erro():
        return f"<h1>⚠️ Sistema Transpontual</h1><p>Configurando...</p>"

# Exportar app
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
