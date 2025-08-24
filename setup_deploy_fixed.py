#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup de Deploy COMPLETO - Dashboard Baker Flask
Prepara o projeto para deploy em Railway, Render ou Heroku
VERSÃO CORRIGIDA
"""

import os
import sys
from datetime import datetime

def criar_arquivo(nome, conteudo):
    """Cria arquivo com conteúdo"""
    try:
        with open(nome, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"✅ {nome} criado/atualizado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar {nome}: {e}")
        return False

def setup_deploy_completo():
    """Configura o projeto completo para deploy em produção"""
    
    print("🚀 SETUP DE DEPLOY COMPLETO - DASHBOARD BAKER FLASK")
    print("=" * 70)
    
    # Verificar se está na pasta correta
    if not os.path.exists('app') or not os.path.exists('run.py'):
        print("❌ Execute este script na pasta raiz do projeto!")
        print("💡 Deve conter as pastas 'app' e arquivo 'run.py'")
        return False
    
    print("✅ Pasta do projeto detectada")
    
    # 1. PROCFILE OTIMIZADO
    print("\n1. 🔧 Criando Procfile otimizado...")
    
    procfile_content = """web: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --max-requests 1000
release: python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Banco inicializado')"
"""
    
    criar_arquivo("Procfile", procfile_content)
    
    # 2. WSGI.PY COMPLETO
    print("\n2. 🔧 Criando wsgi.py com healthcheck...")
    
    wsgi_content = '''#!/usr/bin/env python3
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
'''
    
    criar_arquivo("wsgi.py", wsgi_content)
    
    # 3. REQUIREMENTS.TXT ATUALIZADO
    print("\n3. 📦 Atualizando requirements.txt...")
    
    requirements_content = """# Dashboard Baker Flask - Requirements for Production Deploy
# Core Flask
Flask==2.3.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-WTF==1.1.1
WTForms==3.0.1

# Database
SQLAlchemy==2.0.21
psycopg2-binary==2.9.7

# Production Server
gunicorn==21.2.0
eventlet==0.33.3

# Data Processing
pandas==2.1.1
openpyxl==3.1.2
xlrd==2.0.1

# Utilities
python-dotenv==1.0.0
Werkzeug==2.3.7

# Security
cryptography==41.0.4

# Monitoring
psutil==5.9.5
"""
    
    criar_arquivo("requirements.txt", requirements_content)
    
    # 4. RUNTIME.TXT
    print("\n4. 🐍 Criando runtime.txt...")
    criar_arquivo("runtime.txt", "python-3.11.5")
    
    # 5. RAILWAY.TOML
    print("\n5. 🚂 Criando railway.toml...")
    
    railway_content = """[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PYTHONPATH = "/app"
FLASK_ENV = "production"
"""
    
    criar_arquivo("railway.toml", railway_content)
    
    # 6. RENDER.YAML
    print("\n6. 🎨 Criando render.yaml...")
    
    render_content = """services:
  - type: web
    name: dashboard-baker-flask
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn wsgi:application"
    healthCheckPath: "/health"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHONPATH
        value: /opt/render/project/src
"""
    
    criar_arquivo("render.yaml", render_content)
    
    # 7. DOCKERFILE
    print("\n7. 🐳 Criando Dockerfile...")
    
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
"""
    
    criar_arquivo("Dockerfile", dockerfile_content)
    
    # 8. .GITIGNORE ATUALIZADO
    print("\n8. 📝 Criando .gitignore...")
    
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Flask instance folder
instance/

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
*.tmp

# Production
.env.production
"""
    
    criar_arquivo(".gitignore", gitignore_content)
    
    # 9. VERIFICAR ESTRUTURA
    print("\n9. 🔍 Verificando estrutura do projeto...")
    
    estrutura_esperada = [
        'app/',
        'app/__init__.py',
        'app/models/',
        'app/routes/',
        'app/templates/',
        'app/static/',
        'run.py'
    ]
    
    missing = []
    for item in estrutura_esperada:
        if not os.path.exists(item):
            missing.append(item)
    
    if missing:
        print(f"⚠️  Itens faltando: {', '.join(missing)}")
    else:
        print("✅ Estrutura do projeto OK")
    
    # 10. INSTRUÇÕES FINAIS
    print("\n" + "="*70)
    print("🎉 SETUP DE DEPLOY CONCLUÍDO!")
    print("="*70)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1️⃣  RAILWAY DEPLOY:")
    print("   • Visite: https://railway.app")
    print("   • Conecte seu repositório GitHub")
    print("   • Configure as variáveis de ambiente:")
    print("     - DATABASE_URL (PostgreSQL)")
    print("     - SECRET_KEY (string aleatória)")
    print("     - FLASK_ENV=production")
    
    print("\n2️⃣  RENDER DEPLOY:")
    print("   • Visite: https://render.com")
    print("   • Crie novo Web Service")
    print("   • Configure:")
    print("     - Build Command: pip install -r requirements.txt")
    print("     - Start Command: gunicorn wsgi:application")
    print("     - Environment: Python")
    
    print("\n3️⃣  HEROKU DEPLOY:")
    print("   • Instale Heroku CLI")
    print("   • heroku create nome-do-app")
    print("   • heroku addons:create heroku-postgresql:hobby-dev")
    print("   • git push heroku main")
    
    print("\n🔧 VARIÁVEIS DE AMBIENTE NECESSÁRIAS:")
    print("   • DATABASE_URL - URL do PostgreSQL")
    print("   • SECRET_KEY - Chave secreta do Flask")
    print("   • FLASK_ENV=production")
    
    print("\n✅ Arquivos criados/atualizados:")
    arquivos = [
        "Procfile", "wsgi.py", "requirements.txt", "runtime.txt",
        "railway.toml", "render.yaml", "Dockerfile", ".gitignore"
    ]
    for arquivo in arquivos:
        status = "✅" if os.path.exists(arquivo) else "❌"
        print(f"   {status} {arquivo}")
    
    print("\n🚀 Sistema pronto para deploy em produção!")
    return True

if __name__ == "__main__":
    try:
        sucesso = setup_deploy_completo()
        if sucesso:
            print("\n🎊 Deploy setup finalizado com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Erro no setup de deploy")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico: {e}")
        sys.exit(1)
