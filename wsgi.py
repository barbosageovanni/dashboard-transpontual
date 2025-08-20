#!/usr/bin/env python3
import os
import sys

os.environ.setdefault('FLASK_ENV', 'production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from config import ProductionConfig
    
    application = create_app(ProductionConfig)
    
    with application.app_context():
        try:
            db.session.execute("SELECT 1")
            print("✅ Database OK")
            db.create_all()
            
            from app.models.user import User
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@transpontual.app.br',
                    nome_completo='Admin',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin created")
        except Exception as e:
            print(f"Init: {e}")
            
except Exception as e:
    print(f"Error: {e}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def home():
        return f"<h1>Dashboard Transpontual</h1><p>Loading...</p>"

app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
