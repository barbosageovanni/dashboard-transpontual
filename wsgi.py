#!/usr/bin/env python3
import os
import sys

print("🚀 SISTEMA TRANSPONTUAL - CORRIGINDO DUPLICATAS")

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

import logging
logging.getLogger().setLevel(logging.ERROR)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ERRO_SISTEMA = None

try:
    from app import create_app
    from config import ProductionConfig
    
    application = create_app(ProductionConfig)
    
    with application.app_context():
        from sqlalchemy import text
        from app import db
        db.session.execute(text("SELECT 1"))
        db.create_all()
        
        from app.models.user import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@transpontual.app.br',
                nome_completo='Administrador Transpontual',
                tipo_usuario='admin',
                ativo=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
    
    print("🎉 SISTEMA FUNCIONANDO!")
    
except Exception as erro_capturado:
    ERRO_SISTEMA = str(erro_capturado)
    print(f"❌ Erro: {ERRO_SISTEMA}")
    
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def pagina_status():
        return f'''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Sistema Transpontual - Correção</title>
            <style>
                body {{ font-family: Arial; padding: 20px; background: #f0f2f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error {{ background: #ffebee; border-left: 5px solid #f44336; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .success {{ background: #e8f5e8; border-left: 5px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .btn {{ background: #2196f3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 5px; }}
                .code {{ background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Sistema Transpontual - Correção de Duplicatas</h1>
                
                <div class="error">
                    <h3>❌ Problema Identificado:</h3>
                    <p><strong>Erro:</strong> {ERRO_SISTEMA}</p>
                    <p><strong>Causa:</strong> Funções duplicadas no arquivo ctes.py</p>
                </div>
                
                <div class="success">
                    <h3>✅ Solução Manual Garantida:</h3>
                    <p>Execute os comandos abaixo no PowerShell para corrigir:</p>
                    
                    <div class="code">
# 1. Verificar quantas duplicatas existem<br>
$count = (Get-Content "app\\routes\\ctes.py" | Select-String "@bp\\.route\\('/atualizar-lote'\\)").Count<br>
Write-Host "Duplicatas encontradas: $count"<br><br>

# 2. Criar versão limpa (execute linha por linha):<br>
$linhas = Get-Content "app\\routes\\ctes.py"<br>
$novo_arquivo = @()<br>
$primeira_encontrada = $false<br>
$pulando = $false<br><br>

for ($i = 0; $i -lt $linhas.Count; $i++) {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;$linha = $linhas[$i]<br>
&nbsp;&nbsp;&nbsp;&nbsp;if ($linha -match "@bp\\.route\\('/atualizar-lote'\\)") {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if (!$primeira_encontrada) {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$primeira_encontrada = $true<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$pulando = $false<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}} else {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$pulando = $true<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}}<br>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br>
&nbsp;&nbsp;&nbsp;&nbsp;if ($pulando -and $linha -match "@bp\\.route" -and $linha -notmatch "atualizar") {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$pulando = $false<br>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br>
&nbsp;&nbsp;&nbsp;&nbsp;if (!$pulando) {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$novo_arquivo += $linha<br>
&nbsp;&nbsp;&nbsp;&nbsp;}}<br>
}}<br><br>

# 3. Salvar arquivo corrigido<br>
$novo_arquivo | Out-File "app\\routes\\ctes.py" -Encoding utf8 -Force<br><br>

# 4. Verificar resultado<br>
$count_final = (Get-Content "app\\routes\\ctes.py" | Select-String "@bp\\.route\\('/atualizar-lote'\\)").Count<br>
Write-Host "Resultado: $count_final função(ões)"<br><br>

# 5. Se resultado = 1, fazer deploy<br>
if ($count_final -eq 1) {{<br>
&nbsp;&nbsp;&nbsp;&nbsp;git add app\\routes\\ctes.py<br>
&nbsp;&nbsp;&nbsp;&nbsp;git commit -m "FIX: removed duplicate atualizar_lote functions"<br>
&nbsp;&nbsp;&nbsp;&nbsp;git push<br>
}}
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <a href="/instrucoes" class="btn">📋 Instruções Detalhadas</a>
                    <a href="/verificar" class="btn">🔍 Verificar Status</a>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
                    <strong>🎯 Meta:</strong> Reduzir de 3 funções para apenas 1 função atualizar_lote
                </div>
            </div>
        </body>
        </html>
        '''
    
    @application.route('/instrucoes')
    def instrucoes():
        return '''
        <h1>📋 Instruções Passo a Passo</h1>
        
        <h3>Problema:</h3>
        <p>O arquivo app/routes/ctes.py tem 3 funções com o mesmo nome "atualizar_lote", causando conflito.</p>
        
        <h3>Solução:</h3>
        <ol>
            <li>Abra PowerShell na pasta do projeto</li>
            <li>Execute os comandos da página anterior linha por linha</li>
            <li>Aguarde até o count ser = 1</li>
            <li>Faça git push</li>
            <li>Aguarde 3 minutos para o sistema funcionar</li>
        </ol>
        
        <h3>Resultado Esperado:</h3>
        <p>Sistema Transpontual funcionando com login admin/Admin123!</p>
        
        <p><a href="/">← Voltar</a></p>
        '''
    
    @application.route('/verificar')
    def verificar():
        return f'''
        <h1>🔍 Status Atual</h1>
        <p><strong>Erro:</strong> {ERRO_SISTEMA}</p>
        <p><strong>Solução:</strong> Remover duplicatas manualmente</p>
        <p><strong>Arquivo:</strong> app/routes/ctes.py</p>
        <p><a href="/">← Voltar</a></p>
        '''

app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
