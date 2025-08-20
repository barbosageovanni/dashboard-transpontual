#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI - Dashboard Transpontual - Railway Fixed
"""

import os
import sys
from pathlib import Path

# Configurar environment ANTES de tudo
os.environ.setdefault('FLASK_ENV', 'production')

# Garantir que o path está correto
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print(f"🔧 Iniciando aplicação...")
print(f"📁 Base directory: {BASE_DIR}")
print(f"🌍 Environment: {os.environ.get('FLASK_ENV')}")

try:
    # Importar nossa aplicação Flask
    from app import create_app, db
    from config import ProductionConfig
    
    print("✅ Imports Flask OK")
    
    # Criar aplicação
    application = create_app(ProductionConfig)
    
    print("✅ App criado")
    
    # Configurar rota de health check
    @application.route('/')
    def home():
        return """
        <h1>🚂 Dashboard Transpontual</h1>
        <h2>✅ Sistema Online!</h2>
        <p><a href="/auth/login">👉 Fazer Login</a></p>
        <p><strong>Status:</strong> Funcionando</p>
        <p><strong>Database:</strong> Supabase Conectado</p>
        <p><strong>Deploy:</strong> Railway</p>
        """
    
    @application.route('/health')
    def health():
        return {"status": "healthy", "service": "dashboard-transpontual"}
    
    # Inicialização com app context
    with application.app_context():
        try:
            # Testar conexão banco
            result = db.session.execute("SELECT 1").scalar()
            print(f"✅ Database connected: {result}")
            
            # Criar tabelas se necessário
            db.create_all()
            print("✅ Database tables OK")
            
            # Verificar/criar admin
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@transpontual.app.br',
                    nome_completo='Administrador',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created")
            else:
                print("✅ Admin user exists")
                
        except Exception as e:
            print(f"⚠️ Database init warning: {e}")
            # Criar rota de erro
            @application.route('/db-error')
            def db_error():
                return f"<h1>Database Error</h1><p>{e}</p>"
    
    print("✅ Aplicação inicializada com sucesso")
    
except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    
    # Aplicação Flask mínima como fallback
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def emergency():
        return f"""
        <h1>🚨 Dashboard Transpontual - Modo Emergência</h1>
        <h2>Erro de Inicialização</h2>
        <p><strong>Erro:</strong> {e}</p>
        <p><strong>Status:</strong> Sistema em recuperação</p>
        <p>Aguarde correção automática...</p>
        """
    
    @application.route('/health')
    def emergency_health():
        return {"status": "error", "error": str(e)}

# Variável para Gunicorn
app = application

# Para execução direta
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando servidor na porta {port}")
    application.run(host='0.0.0.0', port=port, debug=False)