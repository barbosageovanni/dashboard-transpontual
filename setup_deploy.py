#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup de Deploy COMPLETO - Dashboard Baker Flask
Prepara o projeto para deploy em Railway, Render ou Heroku
VERSÃO FINAL COM TODAS AS CORREÇÕES
"""

import os
import sys
import shutil
import glob
from datetime import datetime
from pathlib import Path

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
    print("\n2. � Criando wsgi.py otimizado...")
    
    wsgi_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point - Dashboard Baker Flask
Otimizado para Railway, Render e Heroku
VERSÃO FINAL COM TODAS AS CORREÇÕES
"""

import os
import sys
from datetime import datetime

# Adicionar pasta do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db

# Configurar ambiente de produção
os.environ.setdefault('FLASK_ENV', 'production')

# Criar aplicação
application = create_app()

# Para compatibilidade
app = application

@application.route('/health')
def health_check():
    """Health check para deploy"""
    try:
        # Testar conexão com banco
        from app.models.cte import CTE
        total = CTE.query.count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "total_ctes": total,
            "version": "3.0",
            "features": ["importacao", "exportacao", "dashboard_responsivo"]
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

# Configurações específicas para produção
if application.config.get('ENV') == 'production':
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar tabelas se necessário
    with application.app_context():
        try:
            db.create_all()
            application.logger.info("✅ Tabelas do banco verificadas/criadas")
        except Exception as e:
            application.logger.error(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=False)
'''
    
    criar_arquivo("wsgi.py", wsgi_content)
    
    # 3. RUNTIME.TXT
    print("\n3. 🐍 Criando runtime.txt...")
    criar_arquivo("runtime.txt", "python-3.11.5\\n")
    
    # 4. RAILWAY.TOML COMPLETO
    print("\n4. 🚂 Criando railway.toml...")
    
    railway_content = '''[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
startCommand = "gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120"

[env]
PYTHONUNBUFFERED = "1"
FLASK_ENV = "production"
WEB_CONCURRENCY = "4"
'''
    
    criar_arquivo("railway.toml", railway_content)
    
    # 5. RENDER.YAML
    print("\n5. 🎨 Criando render.yaml...")
    
    render_content = '''services:
  - type: web
    name: dashboard-baker-flask
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 4"
    plan: free
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: DATABASE_URL
        fromDatabase:
          name: dashboard-baker-db
          property: connectionString
    healthCheckPath: /health
    autoDeploy: true

databases:
  - name: dashboard-baker-db
    plan: free
    databaseName: dashboard_baker
    user: dashboard_user
'''
    
    criar_arquivo("render.yaml", render_content)
    
    # 6. DOCKERFILE (OPCIONAL)
    print("\n6. 🐳 Criando Dockerfile...")
    
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Porta
EXPOSE $PORT

# Comando para iniciar a aplicação
CMD gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 4
'''
    
    criar_arquivo("Dockerfile", dockerfile_content)
oauth2client==4.1.3
plotly==5.15.0
gunicorn==21.2.0
Werkzeug==2.3.7"""
    
    # 2. WSGI
    wsgi = '''#!/usr/bin/env python3
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
    app.run()'''
    
    # 3. Procfile
    procfile = f"web: gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120"
    
    # 4. Render.yaml
    render_yaml = f"""services:
  - type: web
    name: {nome_repo}
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT wsgi:app"
    plan: free
    autoDeploy: false
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        value: postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres"""
    
    # 5. .gitignore
    gitignore = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
instance/
.pytest_cache/
.coverage
htmlcov/
.DS_Store
uploads/
*.log"""
    
    print("\n📁 Criando arquivos...")
    
    # Criar arquivos
    arquivos = [
        ('requirements.txt', requirements),
        ('wsgi.py', wsgi),
        ('Procfile', procfile),
        ('render.yaml', render_yaml),
        ('.gitignore', gitignore)
    ]
    
    sucesso = 0
    for nome, conteudo in arquivos:
        if criar_arquivo(nome, conteudo):
            sucesso += 1
    
    print(f"\n✅ {sucesso}/{len(arquivos)} arquivos criados com sucesso!")
    
    # Comandos Git
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("=" * 30)
    print("1️⃣ Criar repositório no GitHub:")
    print(f"   https://github.com/new")
    print(f"   Nome: {nome_repo}")
    print()
    print("2️⃣ Executar comandos Git:")
    print(f"   git init")
    print(f"   git add .")
    print(f"   git commit -m 'Setup para deploy'")
    print(f"   git remote add origin https://github.com/SEU_USUARIO/{nome_repo}.git")
    print(f"   git branch -M main")
    print(f"   git push -u origin main")
    print()
    print("3️⃣ Configurar Render:")
    print("   https://render.com")
    print("   New > Web Service > Connect GitHub")
    print(f"   Selecionar: {nome_repo}")
    print()
    print("4️⃣ Variáveis de ambiente no Render:")
    print("   FLASK_ENV=production")
    print("   DATABASE_URL=sua_url_supabase")
    print()
    print("🎯 URL final será:")
    print(f"   https://{nome_repo}.onrender.com")
    print("\n🚀 Boa sorte com o deploy!")

if __name__ == '__main__':
    main()