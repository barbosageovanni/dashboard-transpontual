#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Setup para Deploy - Dashboard Baker
Automatiza criação dos arquivos necessários
"""

import os
import sys
from pathlib import Path

def criar_arquivo(nome, conteudo):
    """Cria arquivo com conteúdo"""
    try:
        with open(nome, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"✅ {nome} criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar {nome}: {e}")
        return False

def main():
    print("🚀 SETUP DEPLOY - DASHBOARD BAKER")
    print("=" * 50)
    
    # Verificar se está na pasta do projeto
    if not os.path.exists('app') or not os.path.exists('iniciar.py'):
        print("❌ Execute este script na pasta raiz do projeto!")
        print("💡 Deve conter as pastas 'app' e arquivo 'iniciar.py'")
        sys.exit(1)
    
    # Nome do repositório
    nome_repo = input("📝 Nome do novo repositório (padrão: dashboard-transpontual): ").strip()
    if not nome_repo:
        nome_repo = "dashboard-transpontual"
    
    print(f"📦 Configurando para repositório: {nome_repo}")
    
    # 1. Requirements.txt
    requirements = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.3
psycopg2-binary==2.9.7
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2
python-dotenv==1.0.0
gspread==5.10.0
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