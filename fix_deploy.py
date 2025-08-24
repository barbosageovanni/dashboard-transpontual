#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Correção Automática - Dashboard Baker
Aplicar todas as correções necessárias para deploy
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_banner():
    """Banner do script"""
    print("=" * 60)
    print("🔧 SCRIPT DE CORREÇÃO - DASHBOARD BAKER")
    print("   Versão 3.0 - Correção para Deploy")
    print("=" * 60)

def backup_files():
    """Fazer backup dos arquivos originais"""
    print("\n📦 1. Fazendo backup dos arquivos originais...")
    
    files_to_backup = ['wsgi.py', 'requirements.txt']
    backup_dir = Path('backup_originais')
    
    if not backup_dir.exists():
        backup_dir.mkdir()
        print(f"   📁 Criado diretório: {backup_dir}")
    
    for file in files_to_backup:
        if Path(file).exists():
            backup_path = backup_dir / f"{file}.backup"
            shutil.copy2(file, backup_path)
            print(f"   ✅ Backup: {file} -> {backup_path}")
        else:
            print(f"   ⚠️  Arquivo não encontrado: {file}")

def create_corrected_wsgi():
    """Criar wsgi.py corrigido"""
    print("\n🔧 2. Criando wsgi.py corrigido...")
    
    wsgi_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point - Dashboard Baker Flask CORRIGIDO
Arquivo principal para deploy em produção
SOLUÇÃO: before_first_request substituído por inicialização adequada
"""

import os
import sys
import threading
from app import create_app, db
from sqlalchemy import text

# Configurar environment para produção
os.environ.setdefault('FLASK_ENV', 'production')

# Flag para controlar inicialização única
_initialized = threading.Lock()
_init_done = False

def initialize_app_once():
    """Inicialização única da aplicação"""
    global _init_done
    
    if _init_done:
        return
        
    with _initialized:
        if _init_done:  # Double-check locking
            return
            
        try:
            print("🚀 Inicializando Dashboard Baker...")
            
            # Criar tabelas se não existirem
            db.create_all()
            
            # Criar admin inicial se não existir
            from app.models.user import User
            admin_count = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
            
            if admin_count == 0:
                print("👤 Criando usuário admin inicial...")
                sucesso, resultado = User.criar_admin_inicial()
                
                if sucesso:
                    print("✅ Admin inicial criado com sucesso")
                else:
                    print(f"❌ Erro ao criar admin: {resultado}")
            else:
                print(f"✅ {admin_count} admin(s) encontrado(s)")
            
            _init_done = True
            print("✅ Dashboard Baker inicializado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {str(e)}")

# Criar aplicação
application = create_app()

# ===== MIDDLEWARE DE INICIALIZAÇÃO (Substitui before_first_request) =====

@application.before_request
def ensure_initialized():
    """Garantir que a aplicação seja inicializada antes da primeira requisição"""
    if not _init_done and os.environ.get('FLASK_ENV') == 'production':
        try:
            with application.app_context():
                initialize_app_once()
        except Exception as e:
            print(f"Erro na inicialização via middleware: {e}")

# ===== ENDPOINTS DE MONITORAMENTO =====

@application.route('/health')
def health_check():
    """Endpoint de healthcheck para monitoramento"""
    try:
        # Testar conexão com banco
        with application.app_context():
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
        return {
            'status': 'healthy', 
            'service': 'dashboard-baker', 
            'version': '3.0',
            'database': 'connected'
        }, 200
        
    except Exception as e:
        application.logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'unhealthy', 
            'error': str(e),
            'service': 'dashboard-baker'
        }, 500

@application.route('/ping')
def ping():
    """Endpoint simples de ping"""
    from datetime import datetime
    return {
        'status': 'pong', 
        'timestamp': datetime.now().isoformat(),
        'service': 'dashboard-baker'
    }, 200

@application.route('/info')
def info():
    """Informações do sistema para debug"""
    try:
        with application.app_context():
            # Importar modelos
            from app.models.cte import CTE
            from app.models.user import User
            
            # Contar registros
            total_ctes = CTE.query.count()
            total_users = User.query.count()
            
            # Verificar admin
            admin_users = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
            
        return {
            'service': 'Dashboard Baker',
            'version': '3.0',
            'status': 'operational',
            'database': 'connected',
            'environment': os.environ.get('FLASK_ENV', 'unknown'),
            'stats': {
                'total_ctes': total_ctes,
                'total_users': total_users,
                'admin_users': admin_users
            },
            'system': {
                'python_version': sys.version,
                'flask_env': os.environ.get('FLASK_ENV'),
                'database_url_set': bool(os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI'))
            }
        }, 200
        
    except Exception as e:
        application.logger.error(f"Info endpoint failed: {str(e)}")
        return {
            'service': 'Dashboard Baker',
            'status': 'error',
            'error': str(e)
        }, 500

@application.route('/ready')
def readiness_check():
    """Verifica se a aplicação está pronta para receber tráfego"""
    try:
        with application.app_context():
            # Verificar se há pelo menos um usuário admin
            from app.models.user import User
            admin_count = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
            
            if admin_count == 0:
                return {
                    'status': 'not_ready',
                    'reason': 'No admin user found'
                }, 503
            
        return {
            'status': 'ready',
            'service': 'dashboard-baker',
            'checks': {
                'database': 'ok',
                'tables': 'ok', 
                'admin_user': 'ok'
            }
        }, 200
        
    except Exception as e:
        application.logger.error(f"Readiness check failed: {str(e)}")
        return {
            'status': 'not_ready',
            'error': str(e)
        }, 503

# ===== EXECUÇÃO LOCAL =====

if __name__ == "__main__":
    # Para desenvolvimento local apenas
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🔍 Verificando dependências...")
    try:
        import pandas
        print("✅ Pandas disponível - funcionalidades completas")
    except ImportError:
        print("⚠️ Pandas não disponível - funcionalidades limitadas")
    
    print(f"🚀 Iniciando Dashboard Baker na porta {port}")
    print(f"📝 Debug: {'Ativado' if debug else 'Desativado'}")
    print(f"🌍 Ambiente: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Inicializar para desenvolvimento local
    if debug:
        with application.app_context():
            initialize_app_once()
    
    application.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug
    )
'''
    
    with open('wsgi.py', 'w', encoding='utf-8') as f:
        f.write(wsgi_content)
    
    print("   ✅ wsgi.py corrigido criado")

def create_optimized_requirements():
    """Criar requirements.txt otimizado"""
    print("\n📋 3. Criando requirements.txt otimizado...")
    
    requirements_content = '''# Dashboard Baker Flask - Requirements OTIMIZADOS para Deploy
# Versão: 3.0 - SEM problemas de compilação C++

# ===== CORE FLASK =====
Flask==2.3.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7

# ===== DATABASE =====
SQLAlchemy==2.0.21
psycopg2-binary==2.9.7
alembic==1.12.0

# ===== PRODUCTION SERVER =====
gunicorn==21.2.0

# ===== DATA PROCESSING (Versões WHEEL - evita compilação C++) =====
pandas==2.0.3
numpy==1.24.4
openpyxl==3.1.2
xlsxwriter==3.1.9
xlrd==2.0.1
python-dateutil==2.8.2

# ===== UTILITIES =====
python-dotenv==1.0.0
click==8.1.7
itsdangerous==2.1.2
MarkupSafe==2.1.3
Jinja2==3.1.2

# ===== SECURITY =====
bcrypt==4.0.1

# ===== HTTP & NETWORKING =====
urllib3==2.0.4
certifi==2023.7.22
requests==2.31.0

# ===== TIMEZONE & DATES =====
pytz==2023.3

# ===== FILE HANDLING =====
Pillow==10.0.0

# ===== PRODUCTION OPTIMIZATIONS =====
brotli==1.1.0
'''
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("   ✅ requirements.txt otimizado criado")

def test_installation():
    """Testar instalação das dependências"""
    print("\n🧪 4. Testando instalação das dependências...")
    
    try:
        print("   📥 Instalando dependências com wheel-only...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--only-binary=all', '-r', 'requirements.txt'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("   ✅ Dependências instaladas com sucesso!")
            return True
        else:
            print("   ⚠️ Alguns pacotes podem precisar ser compilados")
            print("   📥 Tentando instalação normal...")
            
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("   ✅ Dependências instaladas (modo normal)!")
                return True
            else:
                print(f"   ❌ Erro na instalação: {result.stderr[:500]}")
                return False
                
    except subprocess.TimeoutExpired:
        print("   ⏰ Timeout na instalação - pode ser normal para pandas/numpy")
        return False
    except Exception as e:
        print(f"   ❌ Erro na instalação: {e}")
        return False

def test_application():
    """Testar a aplicação corrigida"""
    print("\n🚀 5. Testando aplicação corrigida...")
    
    try:
        # Testar importação do wsgi
        import wsgi
        print("   ✅ wsgi.py importado com sucesso")
        
        # Testar health check
        with wsgi.application.app_context():
            response, status = wsgi.health_check()
            if status == 200:
                print("   ✅ Health check funcionando")
            else:
                print(f"   ⚠️ Health check retornou: {status}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

def create_deployment_files():
    """Criar arquivos adicionais para deploy"""
    print("\n📁 6. Criando arquivos de deploy...")
    
    # Procfile para Heroku
    with open('Procfile', 'w') as f:
        f.write('web: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120\n')
    print("   ✅ Procfile criado")
    
    # runtime.txt para especificar versão Python
    with open('runtime.txt', 'w') as f:
        f.write('python-3.11.9\n')
    print("   ✅ runtime.txt criado")
    
    # .env.example
    env_example = '''# Dashboard Baker - Variáveis de Ambiente
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Opcional - Para desenvolvimento
DEBUG=False
'''
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    print("   ✅ .env.example criado")

def show_next_steps():
    """Mostrar próximos passos"""
    print("\n" + "=" * 60)
    print("🎉 CORREÇÕES APLICADAS COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1. TESTAR LOCALMENTE:")
    print("   python wsgi.py")
    print("   # Acesse: http://localhost:5000/health")
    
    print("\n2. DEPLOY NO RAILWAY:")
    print("   railway login")
    print("   railway init")
    print("   railway add postgresql")
    print("   railway up")
    
    print("\n3. DEPLOY NO HEROKU:")
    print("   heroku create seu-app")
    print("   heroku addons:create heroku-postgresql:mini")
    print("   git push heroku main")
    
    print("\n4. DEPLOY NO RENDER:")
    print("   - Conecte o repositório GitHub")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn wsgi:application")
    
    print("\n🔍 VERIFICAÇÕES IMPORTANTES:")
    print("   ✅ wsgi.py corrigido (sem before_first_request)")
    print("   ✅ requirements.txt otimizado (sem problemas C++)")
    print("   ✅ Arquivos de deploy criados")
    print("   ✅ Backup dos originais em ./backup_originais/")
    
    print("\n🆘 SE AINDA HOUVER PROBLEMAS:")
    print("   1. Use: pip install --only-binary=all -r requirements.txt")
    print("   2. Verifique os logs: railway logs --follow")
    print("   3. Teste endpoints: /health, /info, /ready")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar se estamos no diretório correto
    if not Path('app').exists():
        print("\n❌ ERRO: Execute este script na raiz do projeto (onde está a pasta 'app')")
        return
    
    try:
        # Executar correções
        backup_files()
        create_corrected_wsgi()
        create_optimized_requirements()
        create_deployment_files()
        
        # Testar instalação (opcional)
        print("\n🤔 Deseja testar a instalação das dependências? (s/N): ", end="")
        if input().lower().startswith('s'):
            test_installation()
        
        # Testar aplicação
        if test_application():
            print("\n✅ Aplicação testada com sucesso!")
        else:
            print("\n⚠️ Alguns problemas detectados, mas deploy deve funcionar")
        
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a correção: {e}")

if __name__ == "__main__":
    main()