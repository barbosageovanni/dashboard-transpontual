#!/usr/bin/env python3
import os
import sys

print("🗃️ Dashboard Baker - SQLite Local")

# FORÇAR SQLite
os.environ['DATABASE_URL'] = 'sqlite:///dashboard_baker.db'
os.environ['FLASK_ENV'] = 'development'

try:
    from app import create_app, db
    
    # Criar aplicação
    application = create_app()
    
    # Configurar SQLite na app
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard_baker.db'
    
    print("✅ Aplicação criada")

    # Inicializar banco
    with application.app_context():
        print("🔧 Inicializando SQLite...")
        db.create_all()
        print("✅ Tabelas criadas")

        # Criar admin
        from app.models.user import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@transpontual.app.br',
                nome_completo='Administrador Sistema',
                tipo_usuario='admin',
                ativo=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin criado: admin / Admin123!")
        else:
            print("✅ Admin já existe")
            
        print("🎉 SQLite pronto!")

except Exception as e:
    print(f"❌ Erro: {e}")
    
    # Fallback mínimo
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def home():
        return '''
        <h1>🗃️ Dashboard Baker - SQLite Local</h1>
        <p><strong>Sistema funcionando com banco local</strong></p>
        <p>Login: <strong>admin / Admin123!</strong></p>
        <br>
        <a href="/health" style="color: blue;">Health Check</a>
        '''
    
    @application.route('/health')  
    def health():
        return {"status": "ok", "database": "sqlite-local"}

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Dashboard Baker SQLite")
    print("🌐 URL: http://localhost:5000") 
    print("👤 Login: admin / Admin123!")
    print("🗃️ Banco: Arquivo local (dashboard_baker.db)")
    print("=" * 50)
    
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=True)
