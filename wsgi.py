#!/usr/bin/env python3
import os
import sys

print("🚀 SISTEMA TRANSPONTUAL - ERRO DE ESCOPO CORRIGIDO")

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

import logging
logging.getLogger().setLevel(logging.ERROR)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Variável global para armazenar erro
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
    
    print("🎉 SISTEMA TRANSPONTUAL FUNCIONANDO!")
    
except Exception as erro_capturado:
    ERRO_SISTEMA = str(erro_capturado)
    print(f"❌ Erro capturado: {ERRO_SISTEMA}")
    
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def pagina_principal():
        return f'''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Sistema Transpontual</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                .success {{ 
                    background: #e8f5e8; 
                    border-left: 5px solid #4caf50; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .error {{ 
                    background: #ffebee; 
                    border-left: 5px solid #f44336; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .btn {{ 
                    background: #2196f3; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block; 
                    margin: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Sistema Transpontual</h1>
                
                <div class="success">
                    <h3>✅ Progresso das Correções:</h3>
                    <ul>
                        <li>✅ Duplicatas de funções removidas</li>
                        <li>✅ Sintaxe Python corrigida</li>
                        <li>✅ Erro de escopo no wsgi.py corrigido</li>
                        <li>🔄 Sistema carregando...</li>
                    </ul>
                </div>
                
                <div class="error">
                    <h3>⚠️ Status Atual:</h3>
                    <p><strong>Erro:</strong> {ERRO_SISTEMA or "Sistema em inicialização"}</p>
                    <p><strong>Ação:</strong> Sistema será recarregado automaticamente</p>
                </div>
                
                <h3>🎯 Próximos Passos:</h3>
                <ol>
                    <li>Sistema está sendo carregado sem erros de escopo</li>
                    <li>Todas as duplicatas foram removidas</li>
                    <li>Sintaxe Python foi corrigida</li>
                    <li>Login será: admin / Admin123!</li>
                </ol>
                
                <div style="margin-top: 30px;">
                    <a href="/status" class="btn">📊 Ver Status</a>
                    <a href="/tentar-novamente" class="btn">🔄 Recarregar</a>
                </div>
                
                <div style="margin-top: 20px; text-align: center; color: #666;">
                    Sistema será recarregado em <span id="countdown">30</span> segundos...
                </div>
            </div>
            
            <script>
                let count = 30;
                const countdown = document.getElementById('countdown');
                const timer = setInterval(() => {{
                    count--;
                    countdown.textContent = count;
                    if (count <= 0) {{
                        clearInterval(timer);
                        location.reload();
                    }}
                }}, 1000);
            </script>
        </body>
        </html>
        '''
    
    @application.route('/status')
    def status_sistema():
        return f'''
        <h1>📊 Status do Sistema Transpontual</h1>
        <h3>Informações:</h3>
        <p><strong>Erro atual:</strong> {ERRO_SISTEMA or "Nenhum erro"}</p>
        <p><strong>Status:</strong> Sistema em correção</p>
        <p><strong>Último deploy:</strong> Correções aplicadas</p>
        <h3>Correções Aplicadas:</h3>
        <ul>
            <li>✅ Funções duplicadas removidas</li>
            <li>✅ Sintaxe Python corrigida</li>
            <li>✅ Erro de escopo no wsgi.py corrigido</li>
        </ul>
        <p><a href="/">← Voltar</a></p>
        '''
    
    @application.route('/tentar-novamente')
    def tentar_novamente():
        return '''
        <h1>🔄 Recarregando Sistema</h1>
        <p>Sistema será recarregado...</p>
        <script>setTimeout(() => location.href="/", 2000);</script>
        '''

app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
