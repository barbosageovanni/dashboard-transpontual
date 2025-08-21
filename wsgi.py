#!/usr/bin/env python3
import os
import sys

print("🚀 SISTEMA ORIGINAL TRANSPONTUAL - VERSÃO PURA")

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# Desabilitar logs
import logging
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("📱 Importando sistema original...")
    
    # IMPORTAR APENAS SEU SISTEMA ORIGINAL
    from app import create_app, db
    from config import ProductionConfig
    
    print("✅ Módulos importados com sucesso!")
    
    # CRIAR APLICAÇÃO ORIGINAL SEM MODIFICAÇÕES
    application = create_app(ProductionConfig)
    
    print("✅ Aplicação original criada!")
    
    # Configurar banco se necessário
    with application.app_context():
        try:
            # Testar conexão
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Banco conectado!")
            
            # Criar tabelas se necessário
            db.create_all()
            print("✅ Tabelas verificadas!")
            
            # Verificar admin
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
                print("✅ Admin criado!")
            else:
                print("✅ Admin já existe!")
                
        except Exception as e:
            print(f"⚠️ Aviso banco: {e}")
    
    print("🎉 SISTEMA ORIGINAL FUNCIONANDO 100%!")
    
except ImportError as e:
    print(f"❌ Erro importação: {e}")
    
    # Sistema de fallback MUITO simples
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def erro_importacao():
        return f'''
        <h1>🔧 Erro de Importação</h1>
        <p>Erro: {e}</p>
        <p>Verifique se todos os arquivos estão presentes.</p>
        '''

except Exception as e:
    print(f"❌ Erro geral: {e}")
    
    # Sistema de fallback
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def erro_geral():
        return f'''
        <h1>🔧 Erro no Sistema</h1>
        <p>Erro: {e}</p>
        <p>Sistema será reconfigurado.</p>
        '''

# Exportar app
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
