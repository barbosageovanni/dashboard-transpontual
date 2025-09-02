from app import create_app, db
from app.models.user import User
import json

app = create_app()
with app.app_context():
    try:
        # Tentar adicionar coluna permissoes
        db.engine.execute('ALTER TABLE users ADD COLUMN permissoes TEXT DEFAULT "{}"')
        print('Coluna permissoes adicionada')
    except Exception as e:
        print('Coluna já existe:', str(e))
    
    # Configurar permissões do admin
    admin = User.query.filter_by(username='admin').first()
    if admin:
        modules = {
            'dashboard': True,
            'ctes': True, 
            'baixas': True,
            'analise_financeira': True,
            'admin': True,
            'relatorios': True
        }
        admin.permissoes = json.dumps(modules)
        db.session.commit()
        print('Permissões do admin configuradas')
    else:
        print('Admin não encontrado')
