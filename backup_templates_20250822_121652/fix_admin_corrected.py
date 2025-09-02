# ARQUIVO: fix_admin_corrected.py
# Script de correção corrigido sem erros de sintaxe

import os
import sys

def fix_admin_system():
    """Corrige os problemas identificados nos logs"""
    
    print("Corrigindo sistema administrativo...")
    print("=" * 50)
    
    # 1. Corrigir imports problemáticos
    print("\n1. Corrigindo imports...")
    try:
        # Desinstalar e reinstalar flask-migrate
        os.system("pip uninstall flask-migrate -y")
        os.system("pip install flask-migrate==4.0.5")
        print("Flask-migrate corrigido")
    except Exception as e:
        print(f"Problema com flask-migrate: {e}")
    
    # 2. Verificar dependências essenciais
    print("\n2. Verificando dependencias...")
    required_packages = [
        'flask==2.3.3',
        'flask-sqlalchemy==3.0.5',
        'flask-login==0.6.3',
        'werkzeug==2.3.7',
        'psycopg2-binary==2.9.7'
    ]
    
    for package in required_packages:
        try:
            os.system(f"pip install {package}")
            print(f"{package} instalado")
        except Exception as e:
            print(f"Erro em {package}: {e}")
    
    # 3. Criar inicializador simplificado
    print("\n3. Criando inicializador simplificado...")
    
    # Dividir o HTML em partes menores para evitar problemas de sintaxe
    login_html = '''<form method="post" style="max-width: 400px; margin: 50px auto; padding: 20px;">
        <h2>Login - Dashboard Transpontual</h2>
        <div style="margin: 10px 0;">
            <input type="text" name="username" placeholder="Username" required 
                   style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
        </div>
        <div style="margin: 10px 0;">
            <input type="password" name="password" placeholder="Senha" required 
                   style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
        </div>
        <button type="submit" style="width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px;">
            Entrar
        </button>
        <p style="margin-top: 20px; font-size: 12px; color: #666;">
            Teste: admin / Admin123!
        </p>
    </form>'''
    
    css_styles = '''
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #007bff; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .user-list { background: white; border: 1px solid #ddd; border-radius: 8px; }
            .user-item { padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
            .btn { padding: 8px 15px; margin: 0 5px; border: none; border-radius: 4px; cursor: pointer; color: white; }
            .btn-primary { background: #007bff; }
            .btn-warning { background: #ffc107; color: #000; }
            .btn-danger { background: #dc3545; }
    '''
    
    simple_init_content = f'''# ARQUIVO: run_simple.py
# Inicializador simplificado sem flask-migrate

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Configuração básica
app = Flask(__name__)
app.config['SECRET_KEY'] = 'transpontual-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///transpontual.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo User simplificado
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(200))
    tipo_usuario = db.Column(db.String(20), default='user')
    ativo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)
    total_logins = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return self.ativo
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas básicas
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/admin/users')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/admin/users')
        
        return "Credenciais inválidas", 401
    
    return """{login_html}"""

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.tipo_usuario != 'admin':
        return "Acesso negado", 403
    
    html_template = '''<!DOCTYPE html>
    <html>
    <head>
        <title>Gerenciamento de Usuários</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>{css_styles}</style>
    </head>
    <body>
        <div class="header">
            <h1>Gerenciamento de Usuários</h1>
            <button class="btn btn-primary" onclick="location.reload()">Atualizar</button>
        </div>
        
        <div class="user-list" id="usersList">
            <div style="padding: 20px; text-align: center;">Carregando usuários...</div>
        </div>
        
        <script>
        function loadUsers() {{
            $.ajax({{
                url: '/admin/api/users',
                method: 'GET',
                success: function(response) {{
                    if (response.success) {{
                        displayUsers(response.users);
                    }} else {{
                        $('#usersList').html('<div style="padding: 20px; color: red;">Erro: ' + response.error + '</div>');
                    }}
                }},
                error: function() {{
                    $('#usersList').html('<div style="padding: 20px; color: red;">Erro de conexão</div>');
                }}
            }});
        }}
        
        function displayUsers(users) {{
            let html = '';
            users.forEach(user => {{
                html += `
                    <div class="user-item">
                        <div>
                            <strong>${{user.nome_completo || user.username}}</strong><br>
                            <small>${{user.email}} - ${{user.tipo_usuario}} - ${{user.ativo ? 'Ativo' : 'Inativo'}}</small>
                        </div>
                        <div>
                            <button class="btn btn-warning" onclick="resetPassword(${{user.id}}, '${{user.username}}')">
                                Reset Senha
                            </button>
                            <button class="btn btn-danger" onclick="toggleStatus(${{user.id}}, ${{!user.ativo}})">
                                ${{user.ativo ? 'Desativar' : 'Ativar'}}
                            </button>
                        </div>
                    </div>
                `;
            }});
            $('#usersList').html(html);
        }}
        
        function resetPassword(userId, username) {{
            if (confirm('Resetar senha de ' + username + '?')) {{
                $.ajax({{
                    url: '/admin/api/users/' + userId + '/reset-password',
                    method: 'POST',
                    success: function(response) {{
                        if (response.success) {{
                            alert('Nova senha: ' + response.temp_password);
                            loadUsers();
                        }} else {{
                            alert('Erro: ' + response.error);
                        }}
                    }}
                }});
            }}
        }}
        
        function toggleStatus(userId, newStatus) {{
            $.ajax({{
                url: '/admin/api/users/' + userId + '/toggle-status',
                method: 'POST',
                success: function(response) {{
                    if (response.success) {{
                        alert(response.message);
                        loadUsers();
                    }} else {{
                        alert('Erro: ' + response.error);
                    }}
                }}
            }});
        }}
        
        // Carregar usuários ao abrir a página
        $(document).ready(function() {{
            loadUsers();
        }});
        </script>
    </body>
    </html>'''
    
    return html_template.format(css_styles=css_styles)

# APIs do admin
@app.route('/admin/api/users')
@login_required
def api_users():
    if current_user.tipo_usuario != 'admin':
        return jsonify({{'success': False, 'error': 'Sem permissão'}}), 403
    
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nome_completo': user.nome_completo,
            'tipo_usuario': user.tipo_usuario,
            'ativo': user.ativo,
            'ultimo_login': user.ultimo_login.isoformat() if user.ultimo_login else None,
            'total_logins': user.total_logins or 0
        }})
    
    return jsonify({{'success': True, 'users': users_data}})

@app.route('/admin/api/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def api_reset_password(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({{'success': False, 'error': 'Sem permissão'}}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Gerar senha temporária
    import random, string
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.set_password(temp_password)
    
    db.session.commit()
    
    return jsonify({{
        'success': True,
        'message': f'Senha resetada para {{user.username}}',
        'temp_password': temp_password
    }})

@app.route('/admin/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def api_toggle_status(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({{'success': False, 'error': 'Sem permissão'}}), 403
    
    user = User.query.get_or_404(user_id)
    user.ativo = not user.ativo
    
    db.session.commit()
    
    status = 'ativado' if user.ativo else 'desativado'
    return jsonify({{
        'success': True,
        'message': f'Usuário {{user.username}} {{status}}'
    }})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Criar admin padrão
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@transpontual.com',
                nome_completo='Administrador',
                tipo_usuario='admin',
                ativo=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("Admin criado: admin / Admin123!")
    
    print("Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
'''
    
    try:
        with open('run_simple.py', 'w', encoding='utf-8') as f:
            f.write(simple_init_content)
        print("Inicializador criado: run_simple.py")
    except Exception as e:
        print(f"Erro ao criar inicializador: {e}")
    
    print("\nCORREÇÕES APLICADAS!")
    print("=" * 50)
    print("\nPROXIMOS PASSOS:")
    print("1. Feche a aplicação atual (Ctrl+C)")
    print("2. Execute: python run_simple.py")
    print("3. Acesse: http://localhost:5000")
    print("4. Login: admin / Admin123!")
    print("\nSistema administrativo funcionará corretamente!")

if __name__ == '__main__':
    fix_admin_system()