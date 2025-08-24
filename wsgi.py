#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point - Dashboard Baker Flask
Arquivo principal para deploy em produção
"""

import os
import sys
from app import create_app, db

# Configurar environment para produção
os.environ.setdefault('FLASK_ENV', 'production')

# Criar aplicação
application = create_app()

# Healthcheck endpoint simples
@application.route('/health')
def health_check():
    """Endpoint de healthcheck para monitoramento"""
    try:
        # Testar conexão com banco
        with application.app_context():
            db.engine.execute('SELECT 1')
        return {'status': 'healthy', 'service': 'dashboard-baker'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

@application.route('/ping')
def ping():
    """Endpoint simples de ping"""
    return {'status': 'pong', 'timestamp': str(db.func.current_timestamp())}, 200

if __name__ == "__main__":
    # Para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
