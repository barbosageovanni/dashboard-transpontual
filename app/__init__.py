#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Financeiro Baker - Aplicação Flask
Versão 3.0 com Sistema de Administração Completo
"""

import os
from datetime import datetime
import logging

from dotenv import load_dotenv
load_dotenv()  # garante que .env seja carregado antes de ler as configs

from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config, DevelopmentConfig, ProductionConfig


# Instâncias globais
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=None):
    """Factory da aplicação Flask"""
    app = Flask(__name__)

    # Escolha do config
    if config_class is None:
        if os.environ.get('FLASK_ENV') == 'production':
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig

    # Carrega as configs da classe...
    app.config.from_object(config_class)
    # ...e define a URL do banco DEPOIS do load_dotenv (lazy)
    # Requer que sua Config tenha @staticmethod get_database_url()
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.get_database_url()

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Context processors globais
    @app.context_processor
    def inject_globals():
        """Injetar variáveis globais nos templates"""
        return {
            'current_year': datetime.now().year,
            'app_version': '3.0',
            'app_name': 'Dashboard Baker'
        }

    # Middleware de segurança
    @app.before_request
    def security_headers():
        """Aplicar headers de segurança"""
        g.start_time = datetime.utcnow()
        # Log de acesso para rotas admin
        if request.path.startswith('/admin'):
            print(f"🔐 Acesso admin: {request.remote_addr} -> {request.path}")

    @app.after_request
    def after_request(response):
        """Headers de segurança e logs"""
        # Headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Log de tempo de resposta
        if hasattr(g, 'start_time'):
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            if duration > 1.0:  # Log requests lentos
                print(f"⚠️ Request lento: {request.path} ({duration:.2f}s)")

        return response

    # Registrar Blueprints
    registrar_blueprints(app)

    # Comandos CLI customizados
    registrar_comandos_cli(app)

    # Configurar logging
    configurar_logging(app)

    return app

def registrar_blueprints(app):
    """Registra todos os blueprints da aplicação"""

    # Blueprints principais
    from app.routes import auth, dashboard, ctes, baixas
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(ctes.bp)
    app.register_blueprint(baixas.bp)

    # 🆕 Blueprint de Administração
    from app.routes import admin
    app.register_blueprint(admin.bp)

    from app.routes import analise_financeira
    app.register_blueprint(analise_financeira.bp)

    from app.routes import alertas
    app.register_blueprint(alertas.bp)

    # API Blueprint
    from app.routes import api
    app.register_blueprint(api.bp)

    from app.routes import health_check
    app.register_blueprint(health_check.bp)

    # Rota raiz
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.login'))

def registrar_comandos_cli(app):
    """Registra comandos CLI customizados"""

    @app.cli.command()
    def init_db():
        """Inicializar banco de dados"""
        print("🔧 Inicializando banco de dados...")
        db.create_all()

        # Criar admin inicial
        from app.models.user import User
        sucesso, resultado = User.criar_admin_inicial()

        if sucesso:
            print("✅ Banco inicializado com sucesso!")
            if isinstance(resultado, User):
                print(f"👑 Admin criado: {resultado.username}")
        else:
            print(f"❌ Erro na inicialização: {resultado}")

    @app.cli.command()
    def criar_admin():
        """Criar usuário administrador"""
        print("👑 Criando usuário administrador...")

        from app.models.user import User

        username = input("Username: ")
        email = input("Email: ")
        password = input("Senha: ")
        nome_completo = input("Nome completo: ")

        sucesso, resultado = User.criar_usuario(
            username=username,
            email=email,
            password=password,
            nome_completo=nome_completo,
            tipo_usuario='admin'
        )

        if sucesso:
            print(f"✅ Admin criado: {username}")
        else:
            print(f"❌ Erro: {resultado}")

    @app.cli.command()
    def reset_admin():
        """Reset senha do admin"""
        print("🔑 Reset de senha do admin...")

        from app.models.user import User

        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.set_password('Admin123!')
            admin.reset_security_flags()
            db.session.commit()
            print("✅ Senha do admin resetada para: Admin123!")
        else:
            print("❌ Admin não encontrado")

    @app.cli.command()
    def stats():
        """Estatísticas do sistema"""
        print("📊 Estatísticas do Sistema")
        print("=" * 40)

        from app.models.user import User
        from app.models.cte import CTE

        # Estatísticas de usuários
        user_stats = User.estatisticas_usuarios()
        print(f"👥 Usuários:")
        print(f"   Total: {user_stats['total']}")
        print(f"   Ativos: {user_stats['ativos']}")
        print(f"   Admins: {user_stats['admins']}")
        print(f"   Bloqueados: {user_stats['bloqueados']}")

        # Estatísticas de CTEs
        total_ctes = CTE.query.count()
        print(f"\n📋 CTEs:")
        print(f"   Total: {total_ctes}")

        if total_ctes > 0:
            valor_total = db.session.query(db.func.sum(CTE.valor_total)).scalar() or 0
            print(f"   Valor Total: R$ {valor_total:,.2f}")

    @app.cli.command()
    def security_check():
        """Verificação de segurança"""
        print("🔐 Verificação de Segurança")
        print("=" * 40)

        from app.models.user import User

        # Usuários bloqueados
        bloqueados = User.query.filter(User.locked_until.isnot(None)).count()
        print(f"🚨 Usuários bloqueados: {bloqueados}")

        # Usuários com muitas tentativas
        suspeitos = User.query.filter(User.failed_logins >= 3).count()
        print(f"⚠️ Usuários com tentativas suspeitas: {suspeitos}")

        # Admins ativos
        admins = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
        print(f"👑 Admins ativos: {admins}")

        if admins == 0:
            print("❌ CRÍTICO: Nenhum admin ativo!")
        elif admins == 1:
            print("⚠️ AVISO: Apenas 1 admin ativo")
        else:
            print("✅ Múltiplos admins configurados")

def configurar_logging(app):
    """Configurar sistema de logging"""
    if not app.debug and not app.testing:
        # Configurar logging para produção
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = logging.FileHandler('logs/dashboard_baker.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dashboard Baker startup')

# Funções de inicialização rápida
def init_database():
    """Inicializar banco de dados programaticamente"""
    from app import db
    from app.models.user import User

    print("🔧 Inicializando banco...")
    db.create_all()

    # Criar admin se não existir
    sucesso, resultado = User.criar_admin_inicial()

    if sucesso:
        print("✅ Banco inicializado!")
        return True
    else:
        print(f"❌ Erro: {resultado}")
        return False

def verificar_admin():
    """Verificar se existe pelo menos um admin"""
    from app.models.user import User

    admins = User.query.filter_by(tipo_usuario='admin', ativo=True).count()

    if admins == 0:
        print("⚠️ Nenhum admin encontrado, criando admin padrão...")
        sucesso, resultado = User.criar_admin_inicial()

        if sucesso:
            print("✅ Admin padrão criado!")
            return True
        else:
            print(f"❌ Erro ao criar admin: {resultado}")
            return False
    else:
        print(f"✅ {admins} admin(s) encontrado(s)")
        return True
