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
