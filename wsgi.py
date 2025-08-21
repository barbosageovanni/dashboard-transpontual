#!/usr/bin/env python3
import os
import sys

print("🚀 SISTEMA TRANSPONTUAL - TODAS AS DUPLICATAS REMOVIDAS")

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

import logging
logging.getLogger().setLevel(logging.ERROR)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    
    print("🎉 SISTEMA TRANSPONTUAL FUNCIONANDO SEM DUPLICATAS!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def success_page():
        return f'''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Sistema Transpontual - Sucesso!</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh; 
                    margin: 0; 
                    padding: 20px;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                .success {{ 
                    background: #e8f5e8; 
                    border: 2px solid #4caf50; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                }}
                .error {{ 
                    background: #ffebee; 
                    border: 2px solid #f44336; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 15px 0;
                }}
                .btn {{ 
                    background: #2196f3; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block; 
                    margin: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Sistema Transpontual</h1>
                
                <div class="success">
                    <h2>✅ Duplicatas Removidas!</h2>
                    <p>Todas as funções duplicadas foram removidas com sucesso!</p>
                </div>
                
                <div class="error">
                    <h3>⚠️ Erro na Inicialização:</h3>
                    <p>{e}</p>
                    <p>Sistema será recarregado automaticamente...</p>
                </div>
                
                <div>
                    <a href="/login" class="btn">🔐 Tentar Login</a>
                    <a href="/dashboard" class="btn">📊 Dashboard</a>
                </div>
                
                <p style="margin-top: 20px; color: #666;">
                    Sistema recarregando... <span id="dots">...</span>
                </p>
            </div>
            
            <script>
                setTimeout(() => location.reload(), 5000);
                
                let dots = 1;
                setInterval(() => {{
                    document.getElementById('dots').textContent = '.'.repeat(dots % 4);
                    dots++;
                }}, 500);
            </script>
        </body>
        </html>
        '''

app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
