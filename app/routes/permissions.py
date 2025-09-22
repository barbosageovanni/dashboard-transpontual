#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas para gerenciamento de permissões e perfis de usuário
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.permissions import PermissionManager, UserPermission, UserProfile
from app.models.user import User
from app import db

bp = Blueprint('permissions', __name__, url_prefix='/permissions')

@bp.route('/profiles')
@login_required
def profiles():
    """Página de gerenciamento de perfis"""
    if current_user.tipo_usuario != 'admin':
        flash('Acesso negado. Apenas administradores.', 'error')
        return redirect(url_for('dashboard.index'))

    return render_template('permissions/profiles.html')

@bp.route('/api/profiles')
@login_required
def api_profiles():
    """API para listar perfis de usuário"""
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    try:
        profiles = UserProfile.query.filter_by(is_active=True).all()
        profiles_data = []

        for profile in profiles:
            profiles_data.append({
                'id': profile.id,
                'name': profile.name,
                'description': profile.description,
                'permissions': profile.permissions_dict,
                'created_at': profile.created_at.isoformat()
            })

        return jsonify({
            'success': True,
            'profiles': profiles_data,
            'modules': PermissionManager.MODULES,
            'actions': PermissionManager.ACTIONS
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/user/<int:user_id>/assign-profile', methods=['POST'])
@login_required
def api_assign_profile(user_id):
    """API para atribuir perfil a um usuário"""
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    try:
        data = request.get_json()
        profile_name = data.get('profile_name')

        if not profile_name:
            return jsonify({'success': False, 'error': 'Nome do perfil é obrigatório'}), 400

        success, message = PermissionManager.assign_profile_to_user(user_id, profile_name)

        return jsonify({
            'success': success,
            'message': message
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/user/<int:user_id>/permissions')
@login_required
def api_user_permissions(user_id):
    """API para obter permissões de um usuário"""
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404

        permissions = PermissionManager.get_user_permissions(user_id)
        accessible_modules = PermissionManager.get_modules_for_display(user_id)

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'tipo_usuario': user.tipo_usuario
            },
            'permissions': permissions,
            'accessible_modules': accessible_modules
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/user/<int:user_id>/permissions', methods=['POST'])
@login_required
def api_set_user_permissions(user_id):
    """API para definir permissões customizadas de um usuário"""
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    try:
        data = request.get_json()
        permissions = data.get('permissions', {})

        # Remover permissões existentes
        UserPermission.query.filter_by(user_id=user_id).delete()

        # Adicionar novas permissões
        for module, actions in permissions.items():
            if module in PermissionManager.MODULES and actions:
                permission = UserPermission(user_id, module, actions)
                db.session.add(permission)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Permissões atualizadas com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/initialize-permissions', methods=['POST'])
@login_required
def api_initialize_permissions():
    """API para inicializar sistema de permissões"""
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    try:
        # Criar perfis padrão
        success = PermissionManager.create_default_profiles()

        if success:
            # Atribuir perfil admin para administradores existentes
            admin_users = User.query.filter_by(tipo_usuario='admin').all()
            for admin in admin_users:
                PermissionManager.assign_profile_to_user(admin.id, 'Administrador')

            return jsonify({
                'success': True,
                'message': 'Sistema de permissões inicializado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao inicializar sistema de permissões'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/manage')
@login_required
def manage():
    """Página de gerenciamento de permissões por usuário"""
    if current_user.tipo_usuario != 'admin':
        flash('Acesso negado. Apenas administradores.', 'error')
        return redirect(url_for('dashboard.index'))

    users = User.query.all()
    return render_template('permissions/manage.html', users=users)