#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criador de Estrutura Flask - Dashboard Baker
Cria todos os arquivos e pastas necessários
"""

import os

def criar_estrutura_flask():
    """Cria toda a estrutura de pastas e arquivos Flask"""
    
    print("📁 Criando estrutura Flask completa...")
    
    # 1. Criar estrutura de pastas
    pastas = [
        'app',
        'app/models',
        'app/routes', 
        'app/services',
        'app/templates',
        'app/templates/auth',
        'app/templates/dashboard',
        'app/templates/baixas',
        'app/static',
        'app/static/css',
        'app/static/js',
        'app/static/uploads',
        'migrations'
    ]
    
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
        print(f"   📂 {pasta}/")
    
    # 2. Criar arquivo __init__.py da app
    criar_app_init()
    
    # 3. Criar modelos
    criar_models()
    
    # 4. Criar rotas
    criar_routes()
    
    # 5. Criar serviços
    criar_services()
    
    # 6. Criar templates
    criar_templates()
    
    # 7. Criar arquivos estáticos
    criar_static_files()
    
    print("\n✅ Estrutura Flask criada com sucesso!")
    print("🚀 Agora execute: python run.py")

def criar_app_init():
    """Cria app/__init__.py"""
    content = '''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

# Extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    """Factory para criar app Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página.'

    # Registrar blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.baixas import bp as baixas_bp
    from app.routes.api import bp as api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(baixas_bp, url_prefix='/baixas')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
'''
    
    with open('app/__init__.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✅ app/__init__.py")

def criar_models():
    """Cria todos os modelos"""
    
    # models/__init__.py
    with open('app/models/__init__.py', 'w', encoding='utf-8') as f:
        f.write('# Models\n')
    
    # models/cte.py
    cte_content = '''from app import db
from datetime import datetime
from sqlalchemy import func

class CTE(db.Model):
    """Modelo para CTEs"""
    __tablename__ = 'dashboard_baker'

    id = db.Column(db.Integer, primary_key=True)
    numero_cte = db.Column(db.Integer, unique=True, nullable=False, index=True)
    destinatario_nome = db.Column(db.String(255))
    veiculo_placa = db.Column(db.String(20))
    valor_total = db.Column(db.DECIMAL(15, 2))
    
    # Datas principais
    data_emissao = db.Column(db.Date)
    numero_fatura = db.Column(db.String(100))
    data_baixa = db.Column(db.Date)
    observacao = db.Column(db.Text)
    
    # Datas do processo
    data_inclusao_fatura = db.Column(db.Date)
    data_envio_processo = db.Column(db.Date)
    primeiro_envio = db.Column(db.Date)
    data_rq_tmc = db.Column(db.Date)
    data_atesto = db.Column(db.Date)
    envio_final = db.Column(db.Date)
    
    # Metadados
    origem_dados = db.Column(db.String(50), default='Sistema')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CTE {self.numero_cte}>'

    @property
    def has_baixa(self):
        """Verifica se tem baixa"""
        return self.data_baixa is not None

    @property
    def processo_completo(self):
        """Verifica se processo está completo"""
        return all([
            self.data_emissao,
            self.primeiro_envio, 
            self.data_atesto,
            self.envio_final
        ])

    @classmethod
    def get_metricas(cls):
        """Retorna métricas consolidadas"""
        return {
            'total_ctes': cls.query.count(),
            'valor_total': cls.query.with_entities(func.sum(cls.valor_total)).scalar() or 0,
            'faturas_pagas': cls.query.filter(cls.data_baixa.isnot(None)).count(),
            'faturas_pendentes': cls.query.filter(cls.data_baixa.is_(None)).count(),
        }
'''
    
    with open('app/models/cte.py', 'w', encoding='utf-8') as f:
        f.write(cte_content)
    print("   ✅ app/models/cte.py")
    
    # models/user.py
    user_content = '''from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Perfil
    nome_completo = db.Column(db.String(200))
    departamento = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    
    # Permissões
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Define senha com hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)

    def update_login_info(self):
        """Atualiza informações de login"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        db.session.commit()
'''
    
    with open('app/models/user.py', 'w', encoding='utf-8') as f:
        f.write(user_content)
    print("   ✅ app/models/user.py")

def criar_routes():
    """Cria todas as rotas"""
    
    # routes/__init__.py
    with open('app/routes/__init__.py', 'w', encoding='utf-8') as f:
        f.write('# Routes\n')
    
    # routes/auth.py
    auth_content = '''from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        remember_me = data.get('remember_me', False)

        if not username or not password:
            message = 'Username e senha são obrigatórios'
            if request.is_json:
                return jsonify({'success': False, 'message': message})
            flash(message, 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember_me)
            user.update_login_info()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
            
            if request.is_json:
                return jsonify({
                    'success': True, 
                    'message': 'Login realizado com sucesso',
                    'redirect': next_page
                })
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page)
        else:
            message = 'Credenciais inválidas ou usuário inativo'
            if request.is_json:
                return jsonify({'success': False, 'message': message})
            flash(message, 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))
'''
    
    with open('app/routes/auth.py', 'w', encoding='utf-8') as f:
        f.write(auth_content)
    print("   ✅ app/routes/auth.py")
    
    # routes/dashboard.py
    dashboard_content = '''from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.models.cte import CTE
from app import db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    return render_template('dashboard/index.html')

@bp.route('/api/metricas')
@login_required  
def api_metricas():
    """API para métricas do dashboard"""
    metricas = CTE.get_metricas()
    
    return jsonify({
        'metricas': metricas,
        'status': 'success'
    })
'''
    
    with open('app/routes/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(dashboard_content)
    print("   ✅ app/routes/dashboard.py")
    
    # routes/baixas.py
    baixas_content = '''from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

bp = Blueprint('baixas', __name__)

@bp.route('/')
@login_required
def index():
    """Página principal de baixas"""
    return render_template('baixas/index.html')
'''
    
    with open('app/routes/baixas.py', 'w', encoding='utf-8') as f:
        f.write(baixas_content)
    print("   ✅ app/routes/baixas.py")
    
    # routes/api.py
    api_content = '''from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.cte import CTE

bp = Blueprint('api', __name__)

@bp.route('/ctes', methods=['GET'])
@login_required
def listar_ctes():
    """Lista CTEs com paginação"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    ctes = CTE.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'ctes': [
            {
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome,
                'valor_total': float(cte.valor_total) if cte.valor_total else 0,
                'data_emissao': cte.data_emissao.isoformat() if cte.data_emissao else None,
                'has_baixa': cte.has_baixa
            }
            for cte in ctes.items
        ],
        'pagination': {
            'page': page,
            'pages': ctes.pages,
            'total': ctes.total
        }
    })
'''
    
    with open('app/routes/api.py', 'w', encoding='utf-8') as f:
        f.write(api_content)
    print("   ✅ app/routes/api.py")

def criar_services():
    """Cria serviços"""
    
    # services/__init__.py
    with open('app/services/__init__.py', 'w', encoding='utf-8') as f:
        f.write('# Services\n')
    
    # services/cte_service.py
    service_content = '''from app.models.cte import CTE
from app import db
import pandas as pd

class CTEService:
    """Serviço para operações com CTEs"""

    @staticmethod
    def buscar_cte(numero_cte):
        """Busca CTE por número"""
        return CTE.query.filter_by(numero_cte=numero_cte).first()

    @staticmethod
    def criar_cte(dados):
        """Cria novo CTE"""
        try:
            cte = CTE(**dados)
            db.session.add(cte)
            db.session.commit()
            return True, cte
        except Exception as e:
            db.session.rollback()
            return False, str(e)
'''
    
    with open('app/services/cte_service.py', 'w', encoding='utf-8') as f:
        f.write(service_content)
    print("   ✅ app/services/cte_service.py")

def criar_templates():
    """Cria templates básicos"""
    
    # Base template
    base_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Dashboard Baker{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard.index') }}">
                <i class="fas fa-chart-line"></i> Dashboard Baker
            </a>
            
            {% if current_user.is_authenticated %}
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('auth.logout') }}">
                    <i class="fas fa-sign-out-alt"></i> Sair
                </a>
            </div>
            {% endif %}
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Conteúdo Principal -->
    <main class="container-fluid mt-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
'''
    
    with open('app/templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_content)
    print("   ✅ app/templates/base.html")
    
    # Login template
    login_content = '''{% extends "base.html" %}

{% block title %}Login - Dashboard Baker{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
            <div class="card shadow">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-chart-line fa-3x text-primary mb-3"></i>
                        <h3>Dashboard Baker</h3>
                        <p class="text-muted">Sistema de Gestão Financeira</p>
                    </div>

                    <form method="POST">
                        <div class="mb-3">
                            <label for="username" class="form-label">
                                <i class="fas fa-user"></i> Usuário
                            </label>
                            <input type="text" class="form-control" id="username" 
                                   name="username" required>
                        </div>

                        <div class="mb-3">
                            <label for="password" class="form-label">
                                <i class="fas fa-lock"></i> Senha
                            </label>
                            <input type="password" class="form-control" id="password" 
                                   name="password" required>
                        </div>

                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember_me" 
                                   name="remember_me">
                            <label class="form-check-label" for="remember_me">
                                Lembrar-me
                            </label>
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt"></i> Entrar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    with open('app/templates/auth/login.html', 'w', encoding='utf-8') as f:
        f.write(login_content)
    print("   ✅ app/templates/auth/login.html")
    
    # Dashboard template
    dashboard_content = '''{% extends "base.html" %}

{% block title %}Dashboard Principal - Baker{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="text-center mb-4">
            <h1 class="display-4">💰 Dashboard Financeiro Baker</h1>
            <p class="lead">Gestão Inteligente de Faturamento</p>
        </div>
    </div>
</div>

<!-- Cards de Métricas -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <i class="fas fa-chart-line fa-2x text-primary mb-2"></i>
                <h4 id="receita-total">R$ 0</h4>
                <p>Receita Total</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <i class="fas fa-file-invoice fa-2x text-success mb-2"></i>
                <h4 id="total-ctes">0</h4>
                <p>CTEs Total</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <i class="fas fa-check-circle fa-2x text-info mb-2"></i>
                <h4 id="faturas-pagas">0</h4>
                <p>Faturas Pagas</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <i class="fas fa-hourglass-half fa-2x text-warning mb-2"></i>
                <h4 id="faturas-pendentes">0</h4>
                <p>Faturas Pendentes</p>
            </div>
        </div>
    </div>
</div>

<script>
// Carregar métricas
fetch('/api/metricas')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('receita-total').textContent = 
                'R$ ' + data.metricas.valor_total.toLocaleString('pt-BR');
            document.getElementById('total-ctes').textContent = 
                data.metricas.total_ctes.toLocaleString('pt-BR');
            document.getElementById('faturas-pagas').textContent = 
                data.metricas.faturas_pagas.toLocaleString('pt-BR');
            document.getElementById('faturas-pendentes').textContent = 
                data.metricas.faturas_pendentes.toLocaleString('pt-BR');
        }
    })
    .catch(error => console.error('Erro ao carregar métricas:', error));
</script>
{% endblock %}
'''
    
    with open('app/templates/dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_content)
    print("   ✅ app/templates/dashboard/index.html")
    
    # Baixas template
    baixas_content = '''{% extends "base.html" %}

{% block title %}Sistema de Baixas - Dashboard Baker{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-money-check-alt"></i> Sistema de Baixas</h1>
        <p class="lead">Gestão e conciliação de baixas em tempo real</p>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h5>Em desenvolvimento...</h5>
                <p>Sistema de baixas será implementado em breve.</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    with open('app/templates/baixas/index.html', 'w', encoding='utf-8') as f:
        f.write(baixas_content)
    print("   ✅ app/templates/baixas/index.html")

def criar_static_files():
    """Cria arquivos estáticos básicos"""
    
    # CSS básico
    css_content = '''/* Dashboard Baker CSS */
.card {
    transition: transform 0.2s;
    border: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.navbar-brand {
    font-weight: bold;
}

.display-4 {
    color: #0f4c75;
}
'''
    
    with open('app/static/css/main.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("   ✅ app/static/css/main.css")
    
    # JS básico
    js_content = '''// Dashboard Baker JavaScript
console.log('Dashboard Baker carregado!');
'''
    
    with open('app/static/js/main.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("   ✅ app/static/js/main.js")

# Executar criação
if __name__ == "__main__":
    criar_estrutura_flask()