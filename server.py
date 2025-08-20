import os
import sys

os.environ['FLASK_ENV'] = 'production'

try:
    sys.path.insert(0, os.path.dirname(__file__))
    from app import create_app, db
    from config import ProductionConfig
    
    app = create_app(ProductionConfig)
    
    with app.app_context():
        try:
            db.session.execute("SELECT 1")
            print("✅ DB OK")
            db.create_all()
            
            from app.models.user import User
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin', 
                    email='admin@transpontual.app.br',
                    nome_completo='Admin',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin criado")
        except Exception as e:
            print(f"Init: {e}")
            
except Exception as e:
    print(f"Error: {e}")
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return f"<h1>Dashboard Transpontual</h1><p>Error: {e}</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
