#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar o Dashboard Baker Flask localmente
Usa configuração adequada para desenvolvimento
"""

import os
import sys
from app import create_app, db

def run_local():
    """Executa a aplicação localmente"""
    
    # Configurar variáveis de ambiente para desenvolvimento local
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///dashboard_baker.db')
    os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Criar aplicação
    app = create_app()
    
    # Criar tabelas se necessário
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Banco de dados inicializado")
        except Exception as e:
            print(f"[WARNING] Aviso no banco de dados: {e}")
    
    # Executar aplicação
    print("[STARTUP] Iniciando Dashboard Baker Flask...")
    print("[INFO] Acesse: http://localhost:5000")
    print("[INFO] Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] Aplicacao encerrada pelo usuario")
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar aplicacao: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = run_local()
    sys.exit(0 if success else 1)
