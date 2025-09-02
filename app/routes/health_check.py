# app/routes/health_check.py
from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('health', __name__)

@bp.route('/health')
def health_check():
    """Health check endpoint para monitoramento"""
    try:
        # Testar conexão com banco
        result = db.session.execute(text('SELECT 1 as test')).fetchone()
        if result[0] != 1:
            raise Exception("Database test failed")
        
        return jsonify({
            'status': 'healthy',
            'service': 'dashboard-transpontual',
            'database': 'connected',
            'version': '3.1.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'dashboard-transpontual'
        }), 500

@bp.route('/api/status')
def api_status():
    """Status detalhado da API"""
    try:
        from app.models.cte import CTE
        from app.models.user import User
        
        ctes_count = CTE.query.count()
        users_count = User.query.count()
        
        return jsonify({
            'success': True,
            'status': 'operational',
            'stats': {
                'ctes': ctes_count,
                'users': users_count
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500