# ARQUIVO: app/routes/auth.py
# VERSÃO CORRIGIDA - Remove conflito de rotas api_profile
# Integrado com SSO Transpontual

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from datetime import datetime

# Importar integração SSO
from app.services.jwt_integration import (
    decode_jwt_token,
    get_cross_system_navigation_links,
    create_user_sso_token,
    UNIFIED_AUTH_AVAILABLE
)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login moderna"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Username e senha são obrigatórios', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.ativo:
            login_user(user, remember=remember)
            user.registrar_login()
            
            flash(f'Bem-vindo, {user.nome_completo or user.username}!', 'success')
            
            # Redirecionar para página solicitada ou dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Credenciais inválidas ou usuário inativo', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    flash(f'Até logo, {current_user.username}!', 'info')
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('auth/profile.html')

@bp.route('/api/profile')
@login_required
def api_profile():
    """API de informações do perfil com estatísticas avançadas"""
    try:
        from datetime import datetime, timedelta
        
        # Estatísticas básicas do usuário
        now = datetime.utcnow()
        
        # Calcular tempo desde o último login
        tempo_desde_login = None
        if current_user.ultimo_login:
            delta = now - current_user.ultimo_login
            if delta.days > 0:
                tempo_desde_login = f"{delta.days} dias atrás"
            elif delta.seconds > 3600:
                horas = delta.seconds // 3600
                tempo_desde_login = f"{horas} hora{'s' if horas > 1 else ''} atrás"
            else:
                minutos = delta.seconds // 60
                tempo_desde_login = f"{minutos} minuto{'s' if minutos > 1 else ''} atrás"
        
        # Calcular tempo na plataforma
        tempo_plataforma = None
        if current_user.created_at:
            delta_plataforma = now - current_user.created_at
            tempo_plataforma = delta_plataforma.days
        
        # Estatísticas do usuário
        stats = {
            'total_logins': current_user.total_logins or 0,
            'ultimo_login': current_user.ultimo_login.isoformat() if current_user.ultimo_login else None,
            'ultimo_login_formatado': current_user.ultimo_login.strftime('%d/%m/%Y às %H:%M') if current_user.ultimo_login else 'Primeiro acesso',
            'tempo_desde_login': tempo_desde_login,
            'membro_desde': current_user.created_at.isoformat() if current_user.created_at else None,
            'membro_desde_formatado': current_user.created_at.strftime('%d/%m/%Y') if current_user.created_at else 'N/A',
            'dias_na_plataforma': tempo_plataforma or 0,
            'tipo_conta': current_user.tipo_usuario.title(),
            'status': 'Ativo' if current_user.ativo else 'Inativo',
            'is_admin': current_user.tipo_usuario == 'admin',
            'avatar_letter': (current_user.nome_completo or current_user.username)[0].upper()
        }
        
        # Informações detalhadas do usuário (usando to_dict se disponível)
        if hasattr(current_user, 'to_dict'):
            user_info = current_user.to_dict()
        else:
            user_info = {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'nome_completo': current_user.nome_completo or '',
                'tipo_usuario': current_user.tipo_usuario,
                'ativo': current_user.ativo,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
                'ultimo_login': current_user.ultimo_login.isoformat() if current_user.ultimo_login else None,
                'total_logins': current_user.total_logins or 0
            }
        
        return jsonify({
            'success': True,
            'user': user_info,
            'stats': stats,
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

# ===================================================================
# ROTAS DE GERENCIAMENTO DE USUÁRIOS (APENAS ADMIN)
# ===================================================================

@bp.route('/users')
@login_required
def users():
    """Página de gerenciamento de usuários"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        if current_user.tipo_usuario != 'admin':
            flash('Acesso negado. Apenas administradores.', 'error')
            return redirect(url_for('dashboard.index'))
    
    # Criar objeto usuario vazio para novos usuários ou carregar existente se for edição
    usuario = {}
    user_id = request.args.get('id')
    if user_id:
        # Aqui você carregaria o usuário do banco de dados
        # Por enquanto, simular um usuário existente
        usuario = {
            'id': user_id,
            'nome': 'Usuário Exemplo',
            'email': 'exemplo@transpontual.com',
            'papel': 'admin',
            'ativo': True,
            'ultimo_acesso': None
        }

    return render_template('auth/users.html', usuario=usuario)

@bp.route('/api/users')
@login_required
def api_users():
    """API para listar usuários"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        if current_user.tipo_usuario != 'admin':
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            if hasattr(user, 'to_dict'):
                users_data.append(user.to_dict())
            else:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nome_completo': user.nome_completo,
                    'tipo_usuario': user.tipo_usuario,
                    'ativo': user.ativo,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'ultimo_login': user.ultimo_login.isoformat() if user.ultimo_login else None,
                    'total_logins': user.total_logins or 0
                })
        
        return jsonify({
            'success': True,
            'users': users_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/users', methods=['POST'])
@login_required
def api_criar_usuario():
    """API para criar novo usuário"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        if current_user.tipo_usuario != 'admin':
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Campos obrigatórios faltando'}), 400
        
        # Verificar se já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'Username já existe'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email já existe'}), 400
        
        # Criar usuário
        user = User(
            username=data['username'],
            email=data['email'],
            nome_completo=data.get('nome_completo', ''),
            tipo_usuario=data.get('tipo_usuario', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Retornar dados do usuário criado
        if hasattr(user, 'to_dict'):
            user_data = user.to_dict()
        else:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nome_completo': user.nome_completo,
                'tipo_usuario': user.tipo_usuario,
                'ativo': user.ativo
            }
        
        return jsonify({
            'success': True,
            'message': 'Usuário criado com sucesso',
            'user': user_data
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===================================================================
# ROTAS FUTURAS PARA EDIÇÃO DE PERFIL (PLACEHOLDER)
# ===================================================================

@bp.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    """API para atualizar informações do perfil (FUTURO)"""
    return jsonify({
        'success': False,
        'message': 'Funcionalidade em desenvolvimento'
    }), 501

@bp.route('/api/profile/password', methods=['PUT'])
@login_required
def api_change_password():
    """API para alterar senha do usuário (FUTURO)"""
    return jsonify({
        'success': False,
        'message': 'Funcionalidade em desenvolvimento'
    }), 501


# ===================================================================
# ROTAS SSO TRANSPONTUAL
# ===================================================================

@bp.route('/sso-login', methods=['GET', 'POST'])
def sso_login():
    """
    Login via SSO com token JWT de outros sistemas Transpontual
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    # Extrair token JWT da URL ou formulário
    jwt_token = request.args.get('jwt_token') or request.form.get('jwt_token')

    if not jwt_token:
        flash('Token SSO não fornecido', 'error')
        return redirect(url_for('auth.login'))

    try:
        # Decodificar token JWT
        payload = decode_jwt_token(jwt_token)
        if not payload:
            flash('Token SSO inválido ou expirado', 'error')
            return redirect(url_for('auth.login'))

        # Extrair informações do usuário
        user_email = payload.get('email')
        if not user_email:
            flash('Token SSO não contém informações válidas do usuário', 'error')
            return redirect(url_for('auth.login'))

        # Buscar usuário local correspondente
        user = User.query.filter_by(email=user_email).first()

        if not user:
            # Criar usuário automaticamente se não existir (opcional)
            if UNIFIED_AUTH_AVAILABLE:
                user = User(
                    username=payload.get('username') or user_email.split('@')[0],
                    email=user_email,
                    nome_completo=payload.get('nome', ''),
                    tipo_usuario='user'  # Tipo padrão
                )
                user.set_password('sso_user')  # Senha placeholder
                db.session.add(user)
                db.session.commit()
                flash('Conta criada automaticamente via SSO', 'info')
            else:
                flash('Usuário não encontrado no sistema', 'error')
                return redirect(url_for('auth.login'))

        if not user.ativo:
            flash('Usuário inativo', 'error')
            return redirect(url_for('auth.login'))

        # Fazer login automático
        login_user(user, remember=True)
        user.registrar_login()

        # Salvar informações SSO na sessão
        from flask import session
        session['jwt_token'] = jwt_token
        session['jwt_user_data'] = payload
        session['auth_source'] = f"{payload.get('sistema_origem', 'unknown')}_sso"

        flash(f'Login SSO realizado com sucesso! Bem-vindo, {user.nome_completo or user.username}!', 'success')

        # Redirecionar para página solicitada ou dashboard
        next_page = request.args.get('redirect')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    except Exception as e:
        print(f"❌ Erro no SSO login: {e}")
        flash('Erro interno no processo de SSO', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/api/sso-links')
@login_required
def api_sso_links():
    """
    API para obter links de navegação SSO para outros sistemas
    """
    try:
        links = get_cross_system_navigation_links(current_user)
        return jsonify({
            'success': True,
            'links': links,
            'unified_auth_available': UNIFIED_AUTH_AVAILABLE
        })

    except Exception as e:
        print(f"❌ Erro obtendo links SSO: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno',
            'links': []
        }), 500


@bp.route('/api/create-sso-token')
@login_required
def api_create_sso_token():
    """
    API para criar token SSO para o usuário atual
    """
    try:
        target_system = request.args.get('target', 'baker')
        sso_token = create_user_sso_token(current_user, target_system)

        if not sso_token:
            return jsonify({
                'success': False,
                'error': 'Não foi possível criar token SSO'
            }), 500

        return jsonify({
            'success': True,
            'token': sso_token,
            'message': 'Token SSO criado com sucesso'
        })

    except Exception as e:
        print(f"❌ Erro criando token SSO: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno'
        }), 500