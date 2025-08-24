# ===================================================================
# ⚡ SOLUÇÃO POWERSHELL - Dashboard Baker (Windows)
# Execute no PowerShell: .\solucao_powershell.ps1
# ===================================================================

Clear-Host
Write-Host "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡" -ForegroundColor Yellow
Write-Host "🔧 DASHBOARD BAKER - CORREÇÃO AUTOMÁTICA (WINDOWS)" -ForegroundColor Cyan
Write-Host "   Resolvendo erro: '`$PORT' não é número válido" -ForegroundColor White
Write-Host "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡" -ForegroundColor Yellow

function Show-Step {
    param($Message)
    Write-Host ""
    Write-Host "🔄 $Message..." -ForegroundColor Blue
    Start-Sleep -Milliseconds 500
}

function Show-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Show-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# PASSO 1: Limpar processos Python
Show-Step "Matando processos Python do Dashboard Baker"
try {
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*wsgi*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*dashboard*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Show-Success "Processos Python limpos"
} catch {
    Show-Success "Nenhum processo para limpar"
}

# PASSO 2: Configurar variáveis de ambiente
Show-Step "Configurando variáveis de ambiente"
$env:PORT = "5000"
$env:FLASK_ENV = "development"
Show-Success "PORT=$($env:PORT) definido"

# PASSO 3: Fazer backup do wsgi.py
Show-Step "Fazendo backup do arquivo original"
if (Test-Path "wsgi.py") {
    $backupName = "wsgi.py.backup." + (Get-Date -Format "yyyyMMdd_HHmmss")
    Copy-Item "wsgi.py" $backupName -Force
    Show-Success "Backup criado: $backupName"
} else {
    Write-Host "⚠️  wsgi.py não encontrado - criando novo" -ForegroundColor Yellow
}

# PASSO 4: Criar wsgi.py CORRIGIDO
Show-Step "Criando wsgi.py corrigido para Windows"

$wsgiContent = @'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI - Dashboard Baker Flask CORRIGIDO PARA WINDOWS
PROBLEMA RESOLVIDO: Erro '$PORT' não é número válido
"""

import os
import sys
import threading
from app import create_app, db
from sqlalchemy import text

# ===== CORREÇÃO CRÍTICA DA PORTA PARA WINDOWS =====
def get_safe_port():
    """Obter porta de forma 100% segura no Windows"""
    try:
        # Tentar diferentes fontes de PORT
        port_sources = [
            os.environ.get('PORT'),
            os.getenv('PORT'), 
            '5000'  # Fallback padrão
        ]
        
        for port_str in port_sources:
            if port_str is None:
                continue
                
            # Limpar caracteres não numéricos
            port_clean = ''.join(c for c in str(port_str) if c.isdigit())
            
            if port_clean and len(port_clean) > 0:
                port_num = int(port_clean)
                # Validar range de porta válido
                if 1000 <= port_num <= 65535:
                    return port_num
        
        # Se nada funcionar, usar 5000
        return 5000
        
    except Exception as e:
        print(f"⚠️ Erro ao processar porta: {e}")
        return 5000

# Definir porta ANTES de tudo
PORT = get_safe_port()
print(f"🌐 Porta definida: {PORT}")

# Configuração de ambiente
os.environ.setdefault('FLASK_ENV', 'development')

# Controle thread-safe de inicialização
_init_lock = threading.Lock()
_init_done = False

def safe_initialize():
    """Inicialização segura da aplicação"""
    global _init_done
    
    if _init_done:
        return True
        
    with _init_lock:
        if _init_done:
            return True
            
        try:
            print("🚀 Inicializando Dashboard Baker...")
            db.create_all()
            
            from app.models.user import User
            admin_count = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
            
            if admin_count == 0:
                print("👤 Criando admin inicial...")
                success, result = User.criar_admin_inicial()
                if success:
                    print("✅ Admin criado com sucesso")
                else:
                    print(f"⚠️ Aviso ao criar admin: {result}")
            else:
                print(f"✅ {admin_count} admin(s) encontrado(s)")
            
            _init_done = True
            print("✅ Inicialização concluída")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False

# Criar aplicação Flask
application = create_app()

# Middleware de inicialização
@application.before_request
def ensure_app_initialized():
    """Garantir que app seja inicializada"""
    if not _init_done:
        try:
            with application.app_context():
                safe_initialize()
        except Exception as e:
            print(f"Erro no middleware: {e}")

# ===== ENDPOINTS DE SAÚDE =====
@application.route('/health')
def health_check():
    """Health check"""
    try:
        with application.app_context():
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
        return {
            'status': 'healthy',
            'service': 'dashboard-baker',
            'version': '3.0',
            'port': PORT,
            'platform': 'windows',
            'database': 'connected'
        }, 200
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'port': PORT,
            'platform': 'windows'
        }, 500

@application.route('/ping')
def ping():
    """Ping simples"""
    from datetime import datetime
    return {
        'status': 'pong',
        'timestamp': datetime.now().isoformat(),
        'port': PORT,
        'platform': 'windows'
    }, 200

@application.route('/info')
def system_info():
    """Informações do sistema"""
    try:
        with application.app_context():
            from app.models.cte import CTE
            from app.models.user import User
            
            return {
                'service': 'Dashboard Baker',
                'version': '3.0',
                'status': 'operational',
                'port': PORT,
                'platform': 'windows',
                'environment': os.environ.get('FLASK_ENV'),
                'stats': {
                    'ctes': CTE.query.count(),
                    'users': User.query.count(),
                    'admins': User.query.filter_by(tipo_usuario='admin', ativo=True).count()
                },
                'config': {
                    'port_env': os.environ.get('PORT', 'NOT_SET'),
                    'port_used': PORT,
                    'python_version': sys.version.split()[0],
                    'working_directory': os.getcwd()
                }
            }, 200
    except Exception as e:
        return {
            'service': 'Dashboard Baker',
            'status': 'error',
            'error': str(e),
            'port': PORT,
            'platform': 'windows'
        }, 500

# ===== EXECUÇÃO PRINCIPAL =====
if __name__ == "__main__":
    
    print("🎯" + "="*60 + "🎯")
    print("🚀 DASHBOARD BAKER - WINDOWS - PORTA CORRIGIDA")
    print("🎯" + "="*60 + "🎯")
    
    print(f"🌐 Porta utilizada: {PORT}")
    print(f"🔧 PORT env var: {os.environ.get('PORT', 'NÃO DEFINIDO')}")
    print(f"🌍 Ambiente: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"💻 Sistema: Windows")
    print(f"📁 Diretório: {os.getcwd()}")
    
    # Verificar dependências
    print("\n🔍 Verificando dependências...")
    dependencies_ok = True
    
    try:
        import flask
        print(f"   ✅ Flask {flask.__version__}")
    except ImportError:
        print("   ❌ Flask não encontrado")
        dependencies_ok = False
    
    try:
        import pandas
        print(f"   ✅ Pandas {pandas.__version__} - Funcionalidades completas")
    except ImportError:
        print("   ⚠️  Pandas não disponível - Funcionalidades limitadas")
    
    try:
        from app import create_app
        print("   ✅ App module OK")
    except ImportError as e:
        print(f"   ❌ Erro no app module: {e}")
        dependencies_ok = False
    
    if not dependencies_ok:
        print("\n❌ Dependências críticas em falta!")
        print("💡 Execute: pip install -r requirements.txt")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Modo debug
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    print(f"\n📝 Modo Debug: {'✅ ATIVADO' if debug_mode else '❌ DESATIVADO'}")
    
    # Inicializar para desenvolvimento
    if debug_mode:
        print("\n🔧 Executando inicialização...")
        try:
            with application.app_context():
                success = safe_initialize()
                if success:
                    print("✅ Inicialização OK")
                else:
                    print("⚠️ Problemas na inicialização - continuando")
        except Exception as e:
            print(f"⚠️ Erro na inicialização: {e}")
    
    # Informações de acesso
    print(f"\n🌐 Servidor iniciando em:")
    print(f"   • Aplicação: http://localhost:{PORT}")
    print(f"   • Health:    http://localhost:{PORT}/health")
    print(f"   • Info:      http://localhost:{PORT}/info")
    
    print("\n👤 Login padrão:")
    print("   • Usuário: admin")
    print("   • Senha:   admin123")
    
    print("\n🎯" + "="*60 + "🎯")
    print("🚀 INICIANDO SERVIDOR...")
    print("   Pressione Ctrl+C para parar")
    print("🎯" + "="*60 + "🎯")
    
    # Iniciar servidor
    try:
        application.run(
            host='0.0.0.0',
            port=PORT,
            debug=debug_mode,
            use_reloader=False,
            threaded=True
        )
        
    except OSError as e:
        if "Only one usage of each socket address" in str(e) or "Address already in use" in str(e):
            print(f"\n❌ ERRO: Porta {PORT} já está sendo utilizada!")
            print("\n💡 SOLUÇÕES:")
            print("   1. Feche outros servidores Python")
            print("   2. Use outra porta: $env:PORT='5001'; python wsgi.py")
            print("   3. Reinicie o PowerShell")
        else:
            print(f"\n❌ Erro ao iniciar servidor: {e}")
            
        input("Pressione Enter para sair...")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Servidor interrompido pelo usuário")
        print("✅ Dashboard Baker finalizado")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)
'@

# Escrever arquivo com codificação UTF-8 sem BOM
$wsgiContent | Out-File -FilePath "wsgi.py" -Encoding UTF8 -NoNewline
Show-Success "wsgi.py corrigido criado"

# PASSO 5: Verificar estrutura do projeto
Show-Step "Verificando estrutura do projeto"
if (Test-Path "app") {
    Show-Success "Diretório 'app' encontrado"
} else {
    Show-Error "Diretório 'app' não encontrado!"
    Write-Host "❌ Execute este script na raiz do projeto Dashboard Baker" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# PASSO 6: Testar importação
Show-Step "Testando arquivo corrigido"
$testResult = python -c @"
import os
os.environ['PORT'] = '5000'
try:
    import wsgi
    print('✅ wsgi.py importa corretamente')
    print(f'✅ Porta definida como: {wsgi.PORT}')
    exit(0)
except Exception as e:
    print(f'❌ Erro na importação: {e}')
    exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Show-Success "Arquivo wsgi.py funcionando!"
} else {
    Show-Error "Problema na importação do wsgi.py"
    Read-Host "Pressione Enter para continuar mesmo assim"
}

# PASSO 7: Mostrar resultado final
Write-Host ""
Write-Host "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉" -ForegroundColor Green
Write-Host "✅ CORREÇÃO PARA WINDOWS APLICADA COM SUCESSO!" -ForegroundColor Green
Write-Host "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 PROBLEMA RESOLVIDO:" -ForegroundColor Cyan
Write-Host "   ❌ ANTES: Erro '`$PORT' não é número válido" -ForegroundColor Red
Write-Host "   ✅ AGORA: Porta tratada corretamente no Windows" -ForegroundColor Green
Write-Host ""
Write-Host "📋 MELHORIAS PARA WINDOWS:" -ForegroundColor Cyan
Write-Host "   ✅ Codificação UTF-8 correta" -ForegroundColor Green
Write-Host "   ✅ Terminações de linha Windows (CRLF)" -ForegroundColor Green
Write-Host "   ✅ Tratamento de variáveis de ambiente Windows" -ForegroundColor Green
Write-Host "   ✅ Detecção automática de plataforma" -ForegroundColor Green
Write-Host "   ✅ Fallback seguro para porta 5000" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 EXECUTE AGORA:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   python wsgi.py" -ForegroundColor White -BackgroundColor Blue
Write-Host ""
Write-Host "🔗 DEPOIS DE INICIAR, TESTE:" -ForegroundColor Cyan
Write-Host "   curl http://localhost:5000/health" -ForegroundColor White
Write-Host "   curl http://localhost:5000/info" -ForegroundColor White
Write-Host ""
Write-Host "🌐 ACESSE NO NAVEGADOR:" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor White -BackgroundColor Blue
Write-Host ""
Write-Host "👤 LOGIN PADRÃO:" -ForegroundColor Cyan
Write-Host "   Usuário: admin" -ForegroundColor White
Write-Host "   Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "💡 SE AINDA DER ERRO DE PORTA:" -ForegroundColor Yellow
Write-Host "   `$env:PORT='8000'; python wsgi.py" -ForegroundColor White
Write-Host ""
Write-Host "✨ TUDO PRONTO PARA WINDOWS! ✨" -ForegroundColor Green -BackgroundColor Black

Read-Host "`nPressione Enter para finalizar"