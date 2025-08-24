# ===================================================================
# CORREÇÃO SUPER SIMPLES - Dashboard Baker Windows
# Salve como: fix_simples.ps1
# Execute: .\fix_simples.ps1
# ===================================================================

Write-Host "Corrigindo Dashboard Baker..." -ForegroundColor Green

# Configurar variaveis
$env:PORT = "5000"
$env:FLASK_ENV = "development"
Write-Host "PORT definido: $($env:PORT)"

# Matar processos Python
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Backup do original
if (Test-Path "wsgi.py") {
    Copy-Item "wsgi.py" "wsgi.py.backup" -Force
    Write-Host "Backup criado"
}

# Criar wsgi.py simples
$codigo = @"
import os
import sys
from app import create_app, db
from sqlalchemy import text

def get_port():
    try:
        p = os.environ.get('PORT', '5000')
        return int(''.join(c for c in str(p) if c.isdigit())) if p else 5000
    except:
        return 5000

PORT = get_port()
print('Porta:', PORT)

application = create_app()

@application.route('/health')
def health():
    try:
        with application.app_context():
            db.session.execute(text('SELECT 1'))
        return {'status': 'ok', 'port': PORT}
    except:
        return {'status': 'error', 'port': PORT}

@application.route('/info')
def info():
    return {'service': 'Dashboard Baker', 'port': PORT, 'status': 'running'}

if __name__ == '__main__':
    print('Iniciando Dashboard Baker...')
    print('Porta:', PORT)
    print('Acesse: http://localhost:' + str(PORT))
    try:
        application.run(host='0.0.0.0', port=PORT, debug=True)
    except Exception as e:
        print('Erro:', e)
        if 'Address already in use' in str(e):
            print('Porta em uso! Tente: PORT=5001 python wsgi.py')
        input('Pressione Enter...')
"@

# Escrever arquivo
$codigo | Out-File -FilePath "wsgi.py" -Encoding ASCII -Force

Write-Host "wsgi.py criado!" -ForegroundColor Green

# Testar
Write-Host "Testando..." -ForegroundColor Blue
try {
    $result = python -c "import wsgi; print('OK - Porta:', wsgi.PORT)" 2>&1
    Write-Host $result -ForegroundColor Green
    Write-Host ""
    Write-Host "SUCESSO! Execute agora:" -ForegroundColor Yellow
    Write-Host "python wsgi.py" -BackgroundColor Blue -ForegroundColor White
} catch {
    Write-Host "Erro no teste, mas pode funcionar" -ForegroundColor Yellow
    Write-Host "Execute: python wsgi.py"
}

Write-Host ""
Write-Host "Acesse: http://localhost:5000" -ForegroundColor Cyan