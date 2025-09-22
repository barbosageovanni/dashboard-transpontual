"""
app/routes/alertas.py
"""

import logging
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from app.services.alertas_service import AlertasService

logger = logging.getLogger(__name__)

bp = Blueprint('alertas', __name__, url_prefix='/alertas')

@bp.route('/')
@login_required
def index():
    """Página principal de alertas"""
    return render_template('alertas/index.html')

@bp.route('/api/alertas-ativos')
@login_required
def api_alertas_ativos():
    """
    API para obter alertas ativos
    GET /alertas/api/alertas-ativos
    """
    try:
        alertas_data = AlertasService.obter_alertas_ativos()
        
        return jsonify({
            'success': True,
            'alertas': alertas_data['alertas'],
            'total_alertas': alertas_data['total_alertas'],
            'ultima_atualizacao': alertas_data['ultima_atualizacao']
        })
        
    except Exception as e:
        logger.error(f"Erro na API de alertas ativos: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao carregar alertas',
            'details': str(e)
        }), 500

@bp.route('/api/alertas/<tipo_alerta>/detalhes')
@login_required
def api_detalhes_alerta(tipo_alerta):
    """
    API para obter detalhes de um alerta específico
    GET /alertas/api/alertas/<tipo>/detalhes
    """
    try:
        detalhes = AlertasService.obter_detalhes_alerta(tipo_alerta)
        
        if 'erro' in detalhes:
            return jsonify({
                'success': False,
                'error': detalhes['erro']
            }), 400
        
        return jsonify({
            'success': True,
            'detalhes': detalhes
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do alerta {tipo_alerta}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao carregar detalhes do alerta'
        }), 500

@bp.route('/api/alertas/resumo')
@login_required  
def api_resumo_alertas():
    """
    API para resumo executivo dos alertas
    GET /alertas/api/alertas/resumo
    """
    try:
        alertas_data = AlertasService.obter_alertas_ativos()
        
        # Calcular métricas de resumo
        total_alertas = alertas_data['total_alertas']
        valor_total_risco = sum(
            alerta.get('valor', 0) for alerta in alertas_data['alertas']
        )
        
        alertas_criticos = len([
            a for a in alertas_data['alertas'] 
            if a.get('tipo') == 'critico'
        ])
        
        return jsonify({
            'success': True,
            'resumo': {
                'total_alertas': total_alertas,
                'alertas_criticos': alertas_criticos,
                'valor_total_risco': valor_total_risco,
                'status_sistema': 'critico' if alertas_criticos > 0 else 'normal',
                'recomendacao': 'Ação imediata necessária' if alertas_criticos > 2 else 'Monitoramento contínuo'
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no resumo de alertas: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao gerar resumo'
        }), 500
