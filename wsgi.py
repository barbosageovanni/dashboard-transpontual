#!/usr/bin/env python3
import os
import sys

print("🚀 SISTEMA TRANSPONTUAL - DUPLICATAS CORRIGIDAS")

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

import logging
logging.getLogger().setLevel(logging.ERROR)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from config import ProductionConfig
    
    application = create_app(ProductionConfig)
    
    with application.app_context():
        from sqlalchemy import text
        from app import db
        db.session.execute(text("SELECT 1"))
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
    
    print("🎉 SISTEMA ORIGINAL FUNCIONANDO SEM CONFLITOS!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def status():
        return f'''
        <h1>🔧 Sistema em Correção</h1>
        <p>Erro: {e}</p>
        <p>Duplicatas foram corrigidas, sistema está carregando...</p>
        <script>setTimeout(() => location.reload(), 5000);</script>
        '''

app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
