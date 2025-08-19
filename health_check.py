# 3. SCRIPT DE SAÚDE (criar health_check.py)
from flask import jsonify
from app import create_app, db

app = create_app()

@app.route('/health')
def health_check():
    """Endpoint de saúde para monitoramento"""
    try:
        # Testar conexão com banco
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# 4. CONFIGURAÇÕES DE PRODUÇÃO EXTRAS
class ProductionConfig(Config):
    # Adicionar estas configurações de segurança
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 ano cache
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = 'https'
    
    # Logging
    import logging
    logging.basicConfig(level=logging.INFO)

# 5. COMANDO PARA TESTAR LOCALMENTE ANTES DO DEPLOY
"""
# Instalar Gunicorn
pip install gunicorn

# Testar produção localmente
gunicorn wsgi:app --bind 127.0.0.1:8000 --workers 2

# Acessar: http://localhost:8000
"""