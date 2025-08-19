#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Baker Flask - Aplicação Principal
Versão compatível com Flask 2.3+
"""

import os
from flask_migrate import upgrade
from app import create_app, db
from app.models.cte import CTE
from app.models.user import User

def deploy():
    """Função para deploy em produção"""
    app = create_app()
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        # Executar migrations
        try:
            upgrade()
        except Exception as e:
            print(f"Aviso migrations: {e}")

# Criar app
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Contexto do shell Flask"""
    return {
        'db': db, 
        'CTE': CTE, 
        'User': User
    }

@app.before_request
def create_tables_if_needed():
    """Cria tabelas se necessário (substitui before_first_request)"""
    if not hasattr(app, '_tables_created'):
        try:
            with app.app_context():
                db.create_all()
                app._tables_created = True
                print("✅ Tabelas verificadas/criadas")
        except Exception as e:
            print(f"⚠️ Aviso ao verificar tabelas: {e}")

if __name__ == '__main__':
    # Verificar se é primeira execução
    if not os.path.exists('.env'):
        print("❌ Execute primeiro: python setup_dashboard.py")
        exit(1)
    
    print("🚀 Iniciando Dashboard Baker Flask...")
    print("📊 Acesse: http://localhost:5000")
    print("👤 Login: admin / senha: senha123")
    print("=" * 50)
    
    # Executar aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)