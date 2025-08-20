#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App.py - Entry point para Gunicorn - Dashboard Transpontual
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from config import ProductionConfig

# Configurar variáveis de ambiente
os.environ.setdefault('FLASK_ENV', 'production')

# Criar aplicação
app = create_app(ProductionConfig)

def init_app():
    """Inicializar aplicação para produção"""
    with app.app_context():
        try:
            # Testar conexão
            result = db.session.execute('SELECT 1').scalar()
            print("✅ Conectado ao Supabase em produção")
            
            # Criar tabelas se necessário
            db.create_all()
            
            # Criar usuário admin se não existir
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@transpontual.app.br',
                    nome_completo='Administrador do Sistema',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin criado")
            else:
                print("✅ Usuário admin já existe")
                
        except Exception as e:
            print(f"⚠️ Aviso na inicialização: {e}")

# Executar inicialização
try:
    init_app()
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
