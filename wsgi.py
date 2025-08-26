#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point - Dashboard Baker Flask
Arquivo principal para deploy em produção
"""

import os
import sys
from app import create_app, db
from sqlalchemy import text

# Configurar environment para produção
os.environ.setdefault('FLASK_ENV', 'production')

# Criar aplicação
application = create_app()

# Healthcheck endpoint corrigido para SQLAlchemy 2.0+
@application.route('/health')
def health_check():
    """Endpoint de healthcheck para monitoramento"""
    try:
        # Testar conexão com banco - CORRIGIDO para SQLAlchemy 2.0+
        with application.app_context():
            result = db.session.execute(text('SELECT 1 as test')).fetchone()
            if result[0] != 1:
                raise Exception("Database test failed")
                
        return {
            'status': 'healthy', 
            'service': 'dashboard-baker',
            'database': 'connected'
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy', 
            'error': str(e),
            'service': 'dashboard-baker'
        }, 500

@application.route('/ping')
def ping():
    """Endpoint simples de ping"""
    return {
        'status': 'pong', 
        'service': 'dashboard-baker'
    }, 200

if __name__ == "__main__":
    # Para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)