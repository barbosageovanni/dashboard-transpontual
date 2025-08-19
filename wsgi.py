#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para deploy em produção - Dashboard Baker
"""

import os
from app import create_app, db
from config import ProductionConfig

# Configurar variáveis de ambiente para produção
os.environ.setdefault('FLASK_ENV', 'production')

# Criar aplicação
app = create_app(ProductionConfig)

def init_app():
    """Inicializar aplicação para produção"""
    with app.app_context():
        try:
            # Testar conexão
            db.engine.execute('SELECT 1')
            print("✅ Conectado ao Supabase em produção")
            
            # Criar tabelas se necessário
            db.create_all()
            
            # Criar usuário admin se não existir
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@dashboardbaker.com',
                    nome_completo='Administrador do Sistema',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin criado")
                
        except Exception as e:
            print(f"⚠️ Aviso na inicialização: {e}")

# Executar inicialização
init_app()

if __name__ == "__main__":
    app.run()