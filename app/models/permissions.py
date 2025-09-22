#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Permissões Unificado
Gerencia permissões por perfil de usuário e módulos do sistema
"""

from app import db
from datetime import datetime
from flask_login import current_user
import json

class UserPermission(db.Model):
    """Permissões específicas por usuário"""
    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module = db.Column(db.String(50), nullable=False)  # 'financeiro', 'frotas', 'admin'
    actions = db.Column(db.Text)  # JSON com ações permitidas: ['view', 'create', 'edit', 'delete']
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, module, actions):
        self.user_id = user_id
        self.module = module
        self.actions = json.dumps(actions) if isinstance(actions, list) else actions

    @property
    def actions_list(self):
        """Retorna lista de ações permitidas"""
        try:
            return json.loads(self.actions) if self.actions else []
        except:
            return []

    def has_action(self, action):
        """Verifica se tem permissão para uma ação específica"""
        return action in self.actions_list

class UserProfile(db.Model):
    """Perfis de usuário com permissões pré-definidas"""
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON com permissões
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description, permissions):
        self.name = name
        self.description = description
        self.permissions = json.dumps(permissions) if isinstance(permissions, dict) else permissions

    @property
    def permissions_dict(self):
        """Retorna dicionário de permissões"""
        try:
            return json.loads(self.permissions) if self.permissions else {}
        except:
            return {}

class PermissionManager:
    """Gerenciador central de permissões"""

    # Definição dos módulos do sistema
    MODULES = {
        'financeiro': {
            'name': 'Sistema Financeiro',
            'description': 'CTEs, Baixas, Análise Financeira',
            'routes': ['ctes', 'baixas', 'analise_financeira'],
            'icon': 'bi-currency-dollar'
        },
        'frotas': {
            'name': 'Sistema de Frotas',
            'description': 'Veículos, Motoristas, Checklists',
            'routes': ['vehicles', 'drivers', 'checklists', 'maintenance'],
            'icon': 'bi-truck'
        },
        'admin': {
            'name': 'Administração',
            'description': 'Usuários, Configurações, Relatórios',
            'routes': ['users', 'settings', 'reports'],
            'icon': 'bi-gear'
        }
    }

    # Ações disponíveis
    ACTIONS = ['view', 'create', 'edit', 'delete', 'approve']

    # Perfis pré-definidos
    DEFAULT_PROFILES = {
        'admin': {
            'name': 'Administrador',
            'description': 'Acesso total a todos os módulos',
            'permissions': {
                'financeiro': ['view', 'create', 'edit', 'delete', 'approve'],
                'frotas': ['view', 'create', 'edit', 'delete', 'approve'],
                'admin': ['view', 'create', 'edit', 'delete']
            }
        },
        'operacional': {
            'name': 'Operacional',
            'description': 'Acesso aos módulos operacionais',
            'permissions': {
                'frotas': ['view', 'create', 'edit'],
                'financeiro': ['view']
            }
        },
        'financeiro': {
            'name': 'Financeiro',
            'description': 'Acesso ao módulo financeiro',
            'permissions': {
                'financeiro': ['view', 'create', 'edit', 'approve'],
                'frotas': ['view']
            }
        },
        'motorista': {
            'name': 'Motorista',
            'description': 'Acesso limitado para motoristas',
            'permissions': {
                'frotas': ['view']
            }
        }
    }

    @classmethod
    def create_default_profiles(cls):
        """Cria perfis padrão no banco de dados"""
        for profile_key, profile_data in cls.DEFAULT_PROFILES.items():
            existing = UserProfile.query.filter_by(name=profile_data['name']).first()
            if not existing:
                profile = UserProfile(
                    name=profile_data['name'],
                    description=profile_data['description'],
                    permissions=profile_data['permissions']
                )
                db.session.add(profile)

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar perfis padrão: {e}")
            return False

    @classmethod
    def get_user_permissions(cls, user_id):
        """Obtém todas as permissões de um usuário"""
        permissions = {}

        # Buscar permissões específicas do usuário
        user_perms = UserPermission.query.filter_by(user_id=user_id).all()
        for perm in user_perms:
            permissions[perm.module] = perm.actions_list

        return permissions

    @classmethod
    def user_can(cls, user_id, module, action):
        """Verifica se usuário tem permissão para uma ação específica"""
        # Administradores sempre podem
        from app.models.user import User
        user = User.query.get(user_id)
        if user and user.tipo_usuario == 'admin':
            return True

        # Verificar permissões específicas
        permission = UserPermission.query.filter_by(
            user_id=user_id,
            module=module
        ).first()

        if permission:
            return permission.has_action(action)

        return False

    @classmethod
    def assign_profile_to_user(cls, user_id, profile_name):
        """Atribui um perfil pré-definido a um usuário"""
        profile = UserProfile.query.filter_by(name=profile_name).first()
        if not profile:
            return False, "Perfil não encontrado"

        # Remover permissões existentes
        UserPermission.query.filter_by(user_id=user_id).delete()

        # Adicionar novas permissões baseadas no perfil
        for module, actions in profile.permissions_dict.items():
            permission = UserPermission(user_id, module, actions)
            db.session.add(permission)

        try:
            db.session.commit()
            return True, "Perfil atribuído com sucesso"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atribuir perfil: {e}"

    @classmethod
    def get_user_modules(cls, user_id):
        """Retorna módulos que o usuário tem acesso para exibir na interface"""
        from app.models.user import User
        user = User.query.get(user_id)

        # Administradores veem tudo
        if user and user.tipo_usuario == 'admin':
            return list(cls.MODULES.keys())

        # Usuários normais veem apenas módulos com permissão 'view'
        user_permissions = cls.get_user_permissions(user_id)
        accessible_modules = []

        for module, actions in user_permissions.items():
            if 'view' in actions:
                accessible_modules.append(module)

        return accessible_modules

    @classmethod
    def get_modules_for_display(cls, user_id):
        """Retorna informações completas dos módulos para exibição"""
        accessible_modules = cls.get_user_modules(user_id)
        modules_info = []

        for module_key in accessible_modules:
            if module_key in cls.MODULES:
                module_info = cls.MODULES[module_key].copy()
                module_info['key'] = module_key

                # Verificar ações específicas
                module_info['can_create'] = cls.user_can(user_id, module_key, 'create')
                module_info['can_edit'] = cls.user_can(user_id, module_key, 'edit')
                module_info['can_delete'] = cls.user_can(user_id, module_key, 'delete')

                modules_info.append(module_info)

        return modules_info

# Decorator para verificar permissões
def requires_permission(module, action):
    """Decorator para verificar permissões antes de executar uma função"""
    def decorator(f):
        from functools import wraps
        from flask import abort, flash, redirect, url_for
        from flask_login import current_user

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            if not PermissionManager.user_can(current_user.id, module, action):
                flash(f'Você não tem permissão para {action} em {module}', 'error')
                return redirect(url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator