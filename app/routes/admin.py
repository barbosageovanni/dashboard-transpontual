#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Administração - Dashboard Baker Flask
Gerenciamento completo de usuários, senhas e configurações
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
from functools import wraps
import secrets
import string
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator para verificar se o usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Página principal da administração"""
    try:
        # Estatísticas dos usuários
        total_users = User.query.count()
        active_users = User.query.filter_by(ativo=True).count()
        admin_users = User.query.filter_by(tipo_usuario='admin').count()
        recent_logins = User.query.filter(
            User.ultimo_login >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Estatísticas do sistema
        total_ctes = CTE.query.count()
        ctes_hoje = CTE.query.filter(
            func.date(CTE.created_at) == datetime.utcnow().date()
        ).count()
        
        stats = {
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users,
                'recent_logins': recent_logins
            },
            'system': {
                'total_ctes': total_ctes,
                'ctes_today': ctes_hoje,
                'uptime': '99.9%',  # Placeholder
                'last_backup': datetime.utcnow().strftime('%d/%m/%Y %H:%M')
            }
        }
        
        return render_template('admin/index.html', stats=stats)
        
    except Exception as e:
        flash(f'Erro ao carregar dashboard admin: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@bp.route('/users')
@login_required
@admin_required
def users():
    """Página de gerenciamento de usuários"""
    return render_template('admin/users.html')

@bp.route('/api/users')
@login_required
@admin_required
def api_users():
    """API para listar usuários com paginação e filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        
        # Query base
        query = User.query
        
        # Filtro de busca
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.nome_completo.ilike(search_pattern)
                )
            )
        
        # Filtro por role
        if role_filter:
            query = query.filter(User.tipo_usuario == role_filter)
        
        # Filtro por status
        if status_filter == 'active':
            query = query.filter(User.ativo == True)
        elif status_filter == 'inactive':
            query = query.filter(User.ativo == False)
        
        # Paginação
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            user_dict = user.to_dict()
            
            # Adicionar informações extras
            user_dict.update({
                'last_login_formatted': user.ultimo_login.strftime('%d/%m/%Y %H:%M') if user.ultimo_login else 'Nunca',
                'created_at_formatted': user.created_at.strftime('%d/%m/%Y') if user.created_at else '',
                'status_label': 'Ativo' if user.ativo else 'Inativo',
                'role_label': {
                    'admin': 'Administrador',
                    'user': 'Usuário',
                    'moderator': 'Moderador'
                }.get(user.tipo_usuario, 'Usuário'),
                'avatar_letter': user.nome_completo[0].upper() if user.nome_completo else user.username[0].upper()
            })
            
            users_data.append(user_dict)
        
        return jsonify({
            'success': True,
            'users': users_data,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/users', methods=['POST'])
@login_required
@admin_required
def api_create_user():
    """API para criar novo usuário"""
    try:
        data = request.get_json()
        
        # Validações
        required_fields = ['username', 'email', 'nome_completo', 'tipo_usuario']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        # Verificar se username já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'error': 'Nome de usuário já existe'
            }), 400
        
        # Verificar se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'error': 'Email já existe'
            }), 400
        
        # Gerar senha temporária se não fornecida
        password = data.get('password')
        if not password:
            password = generate_temp_password()
        
        # Criar usuário
        user = User(
            username=data['username'],
            email=data['email'],
            nome_completo=data['nome_completo'],
            tipo_usuario=data['tipo_usuario'],
            ativo=data.get('ativo', True)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário {user.username} criado com sucesso',
            'user': user.to_dict(),
            'temp_password': password if not data.get('password') else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_user(user_id):
    """API para atualizar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Não permitir editar o próprio usuário admin
        if user.id == current_user.id and data.get('ativo') == False:
            return jsonify({
                'success': False,
                'error': 'Não é possível desativar sua própria conta'
            }), 400
        
        # Verificar se username já existe (exceto o atual)
        if data.get('username') and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({
                    'success': False,
                    'error': 'Nome de usuário já existe'
                }), 400
        
        # Verificar se email já existe (exceto o atual)
        if data.get('email') and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({
                    'success': False,
                    'error': 'Email já existe'
                }), 400
        
        # Atualizar campos
        if data.get('username'):
            user.username = data['username']
        if data.get('email'):
            user.email = data['email']
        if data.get('nome_completo'):
            user.nome_completo = data['nome_completo']
        if data.get('tipo_usuario'):
            user.tipo_usuario = data['tipo_usuario']
        if 'ativo' in data:
            user.ativo = data['ativo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário {user.username} atualizado com sucesso',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def api_reset_password(user_id):
    """API para resetar senha do usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Gerar nova senha temporária
        new_password = generate_temp_password()
        user.set_password(new_password)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Senha resetada para o usuário {user.username}',
            'temp_password': new_password
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def api_toggle_user_status(user_id):
    """API para ativar/desativar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Não permitir desativar o próprio usuário
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'error': 'Não é possível alterar o status da sua própria conta'
            }), 400
        
        # Alternar status
        user.ativo = not user.ativo
        db.session.commit()
        
        status_text = 'ativado' if user.ativo else 'desativado'
        
        return jsonify({
            'success': True,
            'message': f'Usuário {user.username} {status_text} com sucesso',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_user(user_id):
    """API para excluir usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Não permitir excluir o próprio usuário
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir sua própria conta'
            }), 400
        
        # Verificar se é o único admin
        if user.tipo_usuario == 'admin':
            admin_count = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
            if admin_count <= 1:
                return jsonify({
                    'success': False,
                    'error': 'Não é possível excluir o último administrador ativo'
                }), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário {username} excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/system-stats')
@login_required
@admin_required
def api_system_stats():
    """API para estatísticas do sistema"""
    try:
        # Estatísticas de usuários
        user_stats = {
            'total': User.query.count(),
            'active': User.query.filter_by(ativo=True).count(),
            'inactive': User.query.filter_by(ativo=False).count(),
            'admins': User.query.filter_by(tipo_usuario='admin').count(),
            'users': User.query.filter_by(tipo_usuario='user').count(),
            'recent_logins': User.query.filter(
                User.ultimo_login >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
        
        # Estatísticas de CTEs
        cte_stats = {
            'total': CTE.query.count(),
            'today': CTE.query.filter(
                func.date(CTE.created_at) == datetime.utcnow().date()
            ).count(),
            'this_week': CTE.query.filter(
                CTE.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count(),
            'this_month': CTE.query.filter(
                CTE.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
        }
        
        return jsonify({
            'success': True,
            'stats': {
                'users': user_stats,
                'ctes': cte_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Funções auxiliares
def generate_temp_password(length=12):
    """Gera senha temporária segura"""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    # Garantir pelo menos uma letra maiúscula, minúscula, número e símbolo
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*")
    ]
    
    # Completar o resto da senha
    for _ in range(length - 4):
        password.append(secrets.choice(alphabet))
    
    # Embaralhar a senha
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

@bp.route('/api/generate-password')
@login_required
@admin_required
def api_generate_password():
    """API para gerar senha temporária"""
    try:
        password = generate_temp_password()
        return jsonify({
            'success': True,
            'password': password
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500