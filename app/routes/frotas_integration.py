#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas de integração com o Sistema de Frotas
"""

from flask import Blueprint, redirect, session, request, jsonify
from flask_login import login_required
from app.services.jwt_integration import criar_link_sistema_frotas, verificar_integracao_disponivel

bp = Blueprint('frotas', __name__, url_prefix='/frotas')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Redireciona para o dashboard principal do sistema de frotas"""
    # O sistema de frotas está no porto 8050 (Flask Dashboard)
    frotas_dashboard_url = "http://localhost:8050"
    return redirect(frotas_dashboard_url)


@bp.route('/veiculos')
@login_required
def veiculos():
    """Redireciona para a gestão de veículos"""
    frotas_dashboard_url = "http://localhost:8050/vehicles"
    return redirect(frotas_dashboard_url)


@bp.route('/motoristas')
@login_required
def motoristas():
    """Redireciona para a gestão de motoristas"""
    frotas_dashboard_url = "http://localhost:8050/drivers"
    return redirect(frotas_dashboard_url)


@bp.route('/checklists')
@login_required
def checklists():
    """Redireciona para o sistema de checklists"""
    frotas_dashboard_url = "http://localhost:8050/checklists"
    return redirect(frotas_dashboard_url)


@bp.route('/abastecimentos')
@login_required
def abastecimentos():
    """Redireciona para o controle de abastecimentos"""
    frotas_dashboard_url = "http://localhost:8050/abastecimentos"
    return redirect(frotas_dashboard_url)


@bp.route('/ordens-servico')
@login_required
def ordens_servico():
    """Redireciona para as ordens de serviço"""
    frotas_dashboard_url = "http://localhost:8050/service_orders"
    return redirect(frotas_dashboard_url)


@bp.route('/status')
def status():
    """API para verificar status da integração"""
    try:
        disponivel = verificar_integracao_disponivel()
        jwt_token = session.get('jwt_token')
        user_data = session.get('jwt_user_data')

        return jsonify({
            'success': True,
            'integration_available': disponivel,
            'jwt_authenticated': bool(jwt_token),
            'user_data': user_data if jwt_token else None,
            'frotas_url': criar_link_sistema_frotas()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/connect')
@login_required
def connect():
    """Página para estabelecer conexão com sistema de frotas"""
    if verificar_integracao_disponivel():
        return redirect(criar_link_sistema_frotas('/auth/login'))
    else:
        from flask import flash
        flash('Sistema de Frotas não está disponível no momento.', 'warning')
        return redirect(request.referrer or '/dashboard')