#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração JWT com Sistema de Gestão de Frotas - Versão Unificada
Permite autenticação compartilhada entre os sistemas Transpontual
"""

import os
import jwt
from datetime import datetime
from flask import request, session, redirect, url_for, g
from flask_login import login_user
from functools import wraps
from typing import Optional, Dict, Any, List

# Tentar importar sistema unificado
try:
    from transpontual_auth import (
        verify_token as verify_unified_token,
        create_access_token as create_unified_token,
        create_user_payload,
        extract_user_from_payload,
        UserInfo,
        SystemRole,
        PermissionClaim
    )
    from transpontual_auth.utils import create_sso_url, get_system_urls
    UNIFIED_AUTH_AVAILABLE = True
    print("[OK] Sistema unificado transpontual_auth disponivel")
except ImportError:
    UNIFIED_AUTH_AVAILABLE = False
    print("Warning: transpontual_auth not available, using legacy system")

# Configurações JWT (mesmo secret do sistema de frotas)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
FROTAS_API_URL = os.getenv("FROTAS_API_URL", "http://localhost:8005")  # FastAPI
FROTAS_DASHBOARD_URL = os.getenv("FROTAS_DASHBOARD_URL", "http://localhost:8050")  # Flask Dashboard


def decode_jwt_token(token: str) -> Optional[Dict[Any, Any]]:
    """
    Decodifica um token JWT - versão unificada
    Suporta tanto tokens legados quanto novos
    """
    if UNIFIED_AUTH_AVAILABLE:
        try:
            # Tentar decodificar com sistema unificado
            payload = verify_unified_token(token, validate_restrictions=True)
            if payload:
                return extract_user_from_payload(payload)
        except Exception as e:
            print(f"[WARNING] Erro no sistema unificado, tentando legado: {e}")

    # Sistema legado
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("[WARNING] Token expirado")
        return None
    except jwt.InvalidTokenError:
        print("[WARNING] Token invalido")
        return None


def extract_jwt_from_request() -> Optional[str]:
    """
    Extrai o token JWT da requisição
    Verifica tanto Authorization header quanto query parameters
    """
    # 1. Header Authorization: Bearer token
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]

    # 2. Query parameter: ?jwt_token=...
    jwt_token = request.args.get('jwt_token')
    if jwt_token:
        return jwt_token

    # 3. Cookie (para navegação entre sistemas)
    jwt_cookie = request.cookies.get('frotas_jwt')
    if jwt_cookie:
        return jwt_cookie

    return None


def verificar_autenticacao_jwt():
    """
    Middleware que verifica autenticação JWT antes de cada requisição
    """
    # Pular verificação para rotas públicas
    rotas_publicas = ['/auth/login', '/static/', '/health', '/']
    if any(request.path.startswith(rota) for rota in rotas_publicas):
        return

    # Verificar se já está logado no Flask
    from flask_login import current_user
    if current_user.is_authenticated:
        return

    # Tentar extrair token JWT
    token = extract_jwt_from_request()
    if not token:
        return  # Prosseguir sem JWT

    # Decodificar token
    payload = decode_jwt_token(token)
    if not payload:
        return  # Token inválido, prosseguir sem autenticação

    # Extrair informações do usuário (compatível com novo e legado)
    if UNIFIED_AUTH_AVAILABLE and isinstance(payload, dict) and 'sistema_origem' in payload:
        # Token novo - usar estrutura unificada
        user_data = {
            'email': payload.get('email'),
            'username': payload.get('username'),
            'nome': payload.get('nome'),
            'id': payload.get('id'),
            'roles': payload.get('roles', []),
            'sistema_origem': payload.get('sistema_origem')
        }
        auth_source = f"{payload.get('sistema_origem', 'unknown')}_sso"
    else:
        # Token legado - usar estrutura antiga
        user_data = payload.get('sub', {})
        if not user_data:
            return
        auth_source = 'frotas_jwt'

    if not user_data or not user_data.get('email'):
        return

    # Tentar encontrar usuário correspondente no sistema Flask
    try:
        from app.models.user import User

        # Buscar por email (prioridade) ou username
        user = None
        if user_data.get('email'):
            user = User.query.filter_by(email=user_data['email']).first()

        if not user and user_data.get('username'):
            user = User.query.filter_by(username=user_data['username']).first()

        if user and user.ativo:
            # Fazer login automático
            login_user(user, remember=True)

            # Salvar informações do JWT na sessão
            session['jwt_token'] = token
            session['jwt_user_data'] = user_data
            session['auth_source'] = auth_source

            # Salvar no g para uso durante a requisição
            g.jwt_authenticated = True
            g.jwt_user_data = user_data

            print(f"[OK] Usuario autenticado via {auth_source}: {user.username}")

    except Exception as e:
        print(f"❌ Erro na autenticação JWT: {e}")


def requires_frotas_access(f):
    """
    Decorator que requer autenticação do sistema de frotas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        # Verificar se está autenticado
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        # Verificar se tem acesso via JWT do sistema de frotas
        if session.get('auth_source') == 'frotas_jwt':
            return f(*args, **kwargs)

        # Verificar se é admin local
        if hasattr(current_user, 'tipo_usuario') and current_user.tipo_usuario == 'admin':
            return f(*args, **kwargs)

        # Não tem acesso
        from flask import flash
        flash('Acesso negado. Esta funcionalidade requer autenticação do Sistema de Frotas.', 'error')
        return redirect(url_for('dashboard.index'))

    return decorated_function


def get_frotas_user_info() -> Optional[Dict[str, Any]]:
    """
    Retorna informações do usuário autenticado via sistema de frotas
    """
    if session.get('auth_source') == 'frotas_jwt':
        return session.get('jwt_user_data')
    return None


def criar_link_sistema_frotas(path: str = "") -> str:
    """
    Cria um link para o sistema de frotas com token JWT para SSO
    """
    jwt_token = session.get('jwt_token')
    base_url = FROTAS_API_URL.rstrip('/')

    # Para URLs específicas do sistema de frotas
    if path.startswith('/'):
        full_url = f"{base_url}{path}"
    else:
        full_url = f"{base_url}/{path}" if path else f"{base_url}/docs"

    if jwt_token:
        if UNIFIED_AUTH_AVAILABLE:
            from transpontual_auth.utils import create_sso_url
            return create_sso_url(full_url, jwt_token)
        else:
            separator = '&' if '?' in full_url else '?'
            return f"{full_url}{separator}jwt_token={jwt_token}"
    else:
        return full_url


def create_user_sso_token(user, target_system: str = "baker") -> Optional[str]:
    """
    Cria token SSO para usuário atual navegar para outro sistema
    """
    if not UNIFIED_AUTH_AVAILABLE:
        return None

    try:
        # Mapear role do Baker para roles do sistema unificado
        roles = map_baker_user_to_system_roles(user)

        # Criar payload do usuário
        user_info, system_roles, permissoes, access_restrictions = create_user_payload(
            user_id=user.id,
            email=user.email,
            nome=user.nome if hasattr(user, 'nome') else user.username,
            sistema_origem="baker",
            roles=roles,
            papel=getattr(user, 'tipo_usuario', 'viewer'),
            username=user.username,
            ativo=user.ativo
        )

        # Criar token unificado
        return create_unified_token(
            user=user_info,
            roles=system_roles,
            permissoes=permissoes,
            restricoes=access_restrictions
        )

    except Exception as e:
        print(f"❌ Erro criando token SSO: {e}")
        return None


def map_baker_user_to_system_roles(user) -> List[str]:
    """
    Mapeia usuário do Baker para roles do sistema unificado
    """
    user_type = getattr(user, 'tipo_usuario', 'viewer')

    role_mapping = {
        'admin': ['admin'],
        'financeiro': ['operador'],
        'operador': ['operador'],
        'viewer': ['viewer']
    }

    return role_mapping.get(user_type, ['viewer'])


def get_cross_system_navigation_links(current_user) -> List[Dict[str, str]]:
    """
    Retorna links de navegação para outros sistemas com SSO
    """
    if not UNIFIED_AUTH_AVAILABLE:
        return []

    try:
        links = []

        # URLs dos sistemas
        system_urls = get_system_urls() if UNIFIED_AUTH_AVAILABLE else {
            'frotas_dashboard': FROTAS_DASHBOARD_URL,
            'frotas_api': FROTAS_API_URL
        }

        # Token SSO do usuário
        sso_token = create_user_sso_token(current_user)
        if not sso_token:
            return links

        # Link para Sistema de Frotas
        frotas_url = f"{system_urls.get('frotas_dashboard', FROTAS_DASHBOARD_URL)}/auth/sso-login"
        frotas_sso_url = create_sso_url(frotas_url, sso_token) if UNIFIED_AUTH_AVAILABLE else frotas_url

        links.append({
            'name': 'Sistema de Frotas',
            'description': 'Gestão de veículos e motoristas',
            'url': frotas_sso_url,
            'icon': 'local_shipping',
            'system': 'frotas'
        })

        # Link para Sistema Financeiro (se implementado)
        financial_url = system_urls.get('financial_dashboard')
        if financial_url:
            financial_sso_url = create_sso_url(f"{financial_url}/auth/sso-login", sso_token)
            links.append({
                'name': 'Sistema Financeiro',
                'description': 'Gestão financeira e contábil',
                'url': financial_sso_url,
                'icon': 'attach_money',
                'system': 'financeiro'
            })

        return links

    except Exception as e:
        print(f"❌ Erro gerando links de navegação: {e}")
        return []


def verificar_integracao_disponivel() -> bool:
    """
    Verifica se a integração com o sistema de frotas está disponível
    """
    try:
        import requests

        # URL do sistema de frotas (garantir que não tenha barra no final)
        url = FROTAS_API_URL.rstrip('/')

        # Testar primeiro a rota de documentação (mais confiável)
        test_urls = [
            f"{url}/docs",
            f"{url}/health",
            f"{url}/"
        ]

        for test_url in test_urls:
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code in [200, 404]:  # 404 também indica que o serviço está rodando
                    print(f"[OK] Sistema de frotas disponível: {test_url} -> {response.status_code}")
                    return True
            except Exception as e:
                print(f"[ERRO] Erro testando {test_url}: {e}")
                continue

        return False
    except Exception as e:
        print(f"[ERRO] Erro geral na verificação: {e}")
        return False


# Context processor para templates
def inject_integration_context():
    """
    Injeta variáveis de contexto da integração nos templates
    """
    from flask_login import current_user

    context = {
        'frotas_system_url': FROTAS_API_URL,
        'frotas_dashboard_url': FROTAS_DASHBOARD_URL,
        'frotas_user_info': get_frotas_user_info(),
        'is_jwt_authenticated': session.get('auth_source', '').endswith('_jwt') or session.get('auth_source', '').endswith('_sso'),
        'integration_available': verificar_integracao_disponivel(),
        'frotas_dashboard_link': FROTAS_DASHBOARD_URL,
        'unified_auth_available': UNIFIED_AUTH_AVAILABLE
    }

    # Adicionar links de navegação entre sistemas se usuário logado
    if current_user.is_authenticated and UNIFIED_AUTH_AVAILABLE:
        context['cross_system_links'] = get_cross_system_navigation_links(current_user)
    else:
        context['cross_system_links'] = []

    return context