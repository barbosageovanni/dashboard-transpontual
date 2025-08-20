#!/bin/bash
# 🚀 DEPLOY AUTOMÁTICO - DASHBOARD TRANSPONTUAL
# Execute este script na pasta raiz do seu projeto

echo "🚀 INICIANDO DEPLOY DASHBOARD TRANSPONTUAL"
echo "=========================================="

# Verificar se está na pasta correta
if [ ! -d "app" ] || [ ! -f "iniciar.py" ]; then
    echo "❌ Execute este script na pasta raiz do projeto!"
    echo "💡 A pasta deve conter 'app/' e 'iniciar.py'"
    exit 1
fi

# 1. Criar requirements.txt
echo "📦 Criando requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==2.3.3
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
Werkzeug==2.3.7
EOF

# 2. Criar wsgi.py
echo "🐍 Criando wsgi.py..."
cat > wsgi.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para deploy em produção - Dashboard Transpontual
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
                    email='admin@transpontual.app.br',
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
EOF

# 3. Criar Procfile
echo "🔧 Criando Procfile..."
cat > Procfile << 'EOF'
web: gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
EOF

# 4. Criar render.yaml
echo "☁️ Criando render.yaml..."
cat > render.yaml << 'EOF'
services:
  - type: web
    name: dashboard-transpontual
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
        value: postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres
EOF

# 5. Criar .gitignore
echo "🙈 Criando .gitignore..."
cat > .gitignore << 'EOF'
__pycache__/
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
*.log
EOF

echo "✅ Todos os arquivos criados com sucesso!"
echo ""
echo "🔄 PRÓXIMOS PASSOS:"
echo "=================="
echo "1️⃣ Criar repositório no GitHub:"
echo "   https://github.com/new"
echo "   Nome: dashboard-transpontual"
echo ""
echo "2️⃣ Executar comandos Git:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Setup deploy transpontual'"
echo "   git remote add origin https://github.com/SEU_USUARIO/dashboard-transpontual.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣ Configurar Render:"
echo "   https://render.com → New → Web Service"
echo "   Conectar repositório dashboard-transpontual"
echo ""
echo "4️⃣ Configurar DNS no Registro.br:"
echo "   Tipo: CNAME"
echo "   Nome: dashboard"  
echo "   Valor: dashboard-transpontual.onrender.com"
echo ""
echo "🎯 URLs finais:"
echo "   https://dashboard-transpontual.onrender.com"
echo "   https://dashboard.transpontual.app.br"
echo ""
echo "🚀 Boa sorte com o deploy!"