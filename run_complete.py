# run_complete.py - Sistema Administrativo Completo
from flask import Flask, request, jsonify, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'transpontual-admin-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_complete.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo User com permissões
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
    # Novo: permissões por módulos
    permissoes = db.Column(db.Text, default='{}')  # JSON com permissões
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_permissions(self):
        try:
            return json.loads(self.permissoes) if self.permissoes else {}
        except:
            return {}
    
    def set_permissions(self, permissions):
        self.permissoes = json.dumps(permissions)
    
    def has_permission(self, module):
        if self.tipo_usuario == 'admin':
            return True
        permissions = self.get_permissions()
        return permissions.get(module, False)
    
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

# Módulos disponíveis no sistema
MODULOS = {
    'dashboard': 'Dashboard Principal',
    'ctes': 'Gerenciamento de CTEs',
    'baixas': 'Sistema de Baixas',
    'analise_financeira': 'Análise Financeira',
    'admin': 'Administração',
    'relatorios': 'Relatórios'
}

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/admin')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.ativo:
            # Registrar login
            user.ultimo_login = datetime.utcnow()
            user.total_logins = (user.total_logins or 0) + 1
            db.session.commit()
            
            login_user(user)
            return redirect('/admin')
        
        return '''
        <div style="color: red; text-align: center; margin: 20px;">
            Credenciais inválidas ou usuário inativo
        </div>
        ''' + get_login_html()
    
    return get_login_html()

def get_login_html():
    return '''
    <html>
    <head>
        <title>Login - Sistema Transpontual</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0; padding: 50px; min-height: 100vh; }
            .login { max-width: 400px; margin: auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
            .login h2 { text-align: center; color: #333; margin-bottom: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
            input:focus { border-color: #667eea; outline: none; }
            button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
            button:hover { opacity: 0.9; }
            .help { margin-top: 25px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }
        </style>
    </head>
    <body>
        <div class="login">
            <h2>Sistema Administrativo<br>Transpontual</h2>
            <form method="post">
                <input type="text" name="username" placeholder="Nome de usuário" required>
                <input type="password" name="password" placeholder="Senha" required>
                <button type="submit">Entrar no Sistema</button>
            </form>
            <div class="help">
                <strong>Credenciais de teste:</strong><br>
                Admin: admin / Admin123!<br>
                Usuário: user1 / 123456
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin')
@login_required
def admin():
    if current_user.tipo_usuario != 'admin':
        return "Acesso negado - Apenas administradores", 403
    
    return '''
    <html>
    <head>
        <title>Sistema Administrativo Completo</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f5f7fa; }
            .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px; }
            .header h1 { margin: 0 0 10px 0; font-size: 28px; }
            .header .user-info { display: flex; justify-content: space-between; align-items: center; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #667eea; }
            .stat-number { font-size: 32px; font-weight: bold; color: #667eea; margin-bottom: 8px; }
            .stat-label { color: #666; font-weight: 500; }
            
            .main-content { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden; }
            .content-header { background: #f8f9fa; padding: 20px; border-bottom: 1px solid #dee2e6; display: flex; justify-content: space-between; align-items: center; }
            .content-body { padding: 0; }
            
            .user-item { padding: 20px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }
            .user-item:last-child { border-bottom: none; }
            .user-info { flex: 1; }
            .user-info strong { display: block; font-size: 16px; margin-bottom: 5px; color: #333; }
            .user-info .meta { color: #666; font-size: 14px; }
            .user-actions { display: flex; gap: 8px; }
            
            .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; transition: all 0.2s; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-danger { background: #dc3545; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn:hover { opacity: 0.8; transform: translateY(-1px); }
            
            .modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 1000; }
            .modal.show { display: flex; }
            .modal-content { background: white; border-radius: 12px; max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto; }
            .modal-header { padding: 20px; border-bottom: 1px solid #dee2e6; display: flex; justify-content: space-between; align-items: center; background: #f8f9fa; }
            .modal-body { padding: 20px; }
            .modal-footer { padding: 20px; border-top: 1px solid #dee2e6; display: flex; gap: 10px; justify-content: flex-end; background: #f8f9fa; }
            
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
            .form-control { width: 100%; padding: 12px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
            .form-control:focus { border-color: #667eea; outline: none; }
            .form-select { width: 100%; padding: 12px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
            
            .permissions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
            .permission-item { display: flex; align-items: center; gap: 10px; padding: 12px; background: #f8f9fa; border-radius: 6px; }
            .permission-item input[type="checkbox"] { width: 18px; height: 18px; }
            
            .loading { text-align: center; padding: 40px; color: #666; }
            .empty { text-align: center; padding: 40px; color: #999; }
            
            .badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }
            .badge-admin { background: #ff6b6b; color: white; }
            .badge-user { background: #51cf66; color: white; }
            .badge-active { background: #51cf66; color: white; }
            .badge-inactive { background: #868e96; color: white; }
            
            .close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #666; }
            .close-btn:hover { color: #000; }
            
            .logout-btn { background: #dc3545; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; }
            .logout-btn:hover { background: #c82333; color: white; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <div class="user-info">
                    <div>
                        <h1>Sistema Administrativo Completo</h1>
                        <p>Usuário logado: ''' + current_user.nome_completo + ''' (''' + current_user.username + ''')</p>
                    </div>
                    <div>
                        <button class="btn btn-secondary" onclick="openChangePasswordModal()">Alterar Minha Senha</button>
                        <a href="/logout" class="logout-btn">Sair</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="totalUsers">0</div>
                    <div class="stat-label">Total de Usuários</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="activeUsers">0</div>
                    <div class="stat-label">Usuários Ativos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="adminUsers">0</div>
                    <div class="stat-label">Administradores</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="recentLogins">0</div>
                    <div class="stat-label">Logins Hoje</div>
                </div>
            </div>
            
            <div class="main-content">
                <div class="content-header">
                    <h3>Gerenciamento de Usuários</h3>
                    <button class="btn btn-primary" onclick="openCreateUserModal()">+ Criar Novo Usuário</button>
                </div>
                <div class="content-body">
                    <div id="usersList" class="loading">Carregando usuários...</div>
                </div>
            </div>
        </div>
        
        <!-- Modal: Criar Usuário -->
        <div id="createUserModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h4>Criar Novo Usuário</h4>
                    <button class="close-btn" onclick="closeModal('createUserModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="createUserForm">
                        <div class="form-group">
                            <label>Nome Completo *</label>
                            <input type="text" name="nome_completo" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Nome de Usuário *</label>
                            <input type="text" name="username" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Senha *</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Tipo de Usuário</label>
                            <select name="tipo_usuario" class="form-select">
                                <option value="user">Usuário</option>
                                <option value="admin">Administrador</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <select name="ativo" class="form-select">
                                <option value="1">Ativo</option>
                                <option value="0">Inativo</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Permissões de Módulos</label>
                            <div class="permissions-grid" id="createPermissions"></div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeModal('createUserModal')">Cancelar</button>
                    <button class="btn btn-primary" onclick="createUser()">Criar Usuário</button>
                </div>
            </div>
        </div>
        
        <!-- Modal: Editar Usuário -->
        <div id="editUserModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h4>Editar Usuário</h4>
                    <button class="close-btn" onclick="closeModal('editUserModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="editUserForm">
                        <input type="hidden" name="user_id" id="editUserId">
                        <div class="form-group">
                            <label>Nome Completo *</label>
                            <input type="text" name="nome_completo" id="editNomeCompleto" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Nome de Usuário *</label>
                            <input type="text" name="username" id="editUsername" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" name="email" id="editEmail" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Tipo de Usuário</label>
                            <select name="tipo_usuario" id="editTipoUsuario" class="form-select">
                                <option value="user">Usuário</option>
                                <option value="admin">Administrador</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <select name="ativo" id="editAtivo" class="form-select">
                                <option value="1">Ativo</option>
                                <option value="0">Inativo</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Permissões de Módulos</label>
                            <div class="permissions-grid" id="editPermissions"></div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeModal('editUserModal')">Cancelar</button>
                    <button class="btn btn-primary" onclick="updateUser()">Salvar Alterações</button>
                </div>
            </div>
        </div>
        
        <!-- Modal: Alterar Minha Senha -->
        <div id="changePasswordModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h4>Alterar Minha Senha</h4>
                    <button class="close-btn" onclick="closeModal('changePasswordModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="changePasswordForm">
                        <div class="form-group">
                            <label>Senha Atual *</label>
                            <input type="password" name="current_password" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Nova Senha *</label>
                            <input type="password" name="new_password" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Confirmar Nova Senha *</label>
                            <input type="password" name="confirm_password" class="form-control" required>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeModal('changePasswordModal')">Cancelar</button>
                    <button class="btn btn-primary" onclick="changeMyPassword()">Alterar Senha</button>
                </div>
            </div>
        </div>
        
        <script>
        const MODULES = ''' + json.dumps(MODULOS) + ''';
        
        function loadUsers() {
            $.get('/api/users', function(data) {
                if (data.success) {
                    displayUsers(data.users);
                    updateStats(data.users);
                } else {
                    $('#usersList').html('<div class="empty">Erro ao carregar usuários</div>');
                }
            });
        }
        
        function updateStats(users) {
            const today = new Date().toDateString();
            $('#totalUsers').text(users.length);
            $('#activeUsers').text(users.filter(u => u.ativo).length);
            $('#adminUsers').text(users.filter(u => u.tipo_usuario === 'admin').length);
            $('#recentLogins').text(users.filter(u => {
                return u.ultimo_login && new Date(u.ultimo_login).toDateString() === today;
            }).length);
        }
        
        function displayUsers(users) {
            if (users.length === 0) {
                $('#usersList').html('<div class="empty">Nenhum usuário cadastrado</div>');
                return;
            }
            
            let html = '';
            users.forEach(function(user) {
                const statusBadge = user.ativo ? 'badge-active' : 'badge-inactive';
                const statusText = user.ativo ? 'Ativo' : 'Inativo';
                const typeBadge = user.tipo_usuario === 'admin' ? 'badge-admin' : 'badge-user';
                const typeText = user.tipo_usuario === 'admin' ? 'Admin' : 'Usuário';
                
                html += `
                    <div class="user-item">
                        <div class="user-info">
                            <strong>${user.nome_completo || user.username}</strong>
                            <div class="meta">
                                ${user.email} | 
                                <span class="badge ${typeBadge}">${typeText}</span>
                                <span class="badge ${statusBadge}">${statusText}</span>
                                | Logins: ${user.total_logins || 0}
                                ${user.ultimo_login ? ' | Último: ' + new Date(user.ultimo_login).toLocaleString('pt-BR') : ''}
                            </div>
                        </div>
                        <div class="user-actions">
                            <button class="btn btn-primary" onclick="editUser(${user.id})">Editar</button>
                            <button class="btn btn-warning" onclick="resetUserPassword(${user.id}, '${user.username}')">Reset Senha</button>
                            <button class="btn ${user.ativo ? 'btn-danger' : 'btn-success'}" 
                                    onclick="toggleUser(${user.id}, ${!user.ativo})">
                                ${user.ativo ? 'Desativar' : 'Ativar'}
                            </button>
                        </div>
                    </div>
                `;
            });
            $('#usersList').html(html);
        }
        
        function generatePermissionsHTML(containerId, permissions = {}) {
            let html = '';
            for (const [moduleKey, moduleName] of Object.entries(MODULES)) {
                const checked = permissions[moduleKey] ? 'checked' : '';
                html += `
                    <div class="permission-item">
                        <input type="checkbox" id="${containerId}_${moduleKey}" name="permissions[${moduleKey}]" ${checked}>
                        <label for="${containerId}_${moduleKey}">${moduleName}</label>
                    </div>
                `;
            }
            $(`#${containerId}`).html(html);
        }
        
        function getFormPermissions(containerId) {
            const permissions = {};
            for (const moduleKey of Object.keys(MODULES)) {
                permissions[moduleKey] = $(`#${containerId}_${moduleKey}`).is(':checked');
            }
            return permissions;
        }
        
        function openCreateUserModal() {
            generatePermissionsHTML('createPermissions');
            $('#createUserModal').addClass('show');
        }
        
        function createUser() {
            const formData = new FormData($('#createUserForm')[0]);
            const permissions = getFormPermissions('createPermissions');
            
            const userData = {
                nome_completo: formData.get('nome_completo'),
                username: formData.get('username'),
                email: formData.get('email'),
                password: formData.get('password'),
                tipo_usuario: formData.get('tipo_usuario'),
                ativo: formData.get('ativo') === '1',
                permissions: permissions
            };
            
            $.ajax({
                url: '/api/users',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(userData),
                success: function(data) {
                    if (data.success) {
                        alert('Usuário criado com sucesso!');
                        closeModal('createUserModal');
                        loadUsers();
                        $('#createUserForm')[0].reset();
                    } else {
                        alert('Erro: ' + data.message);
                    }
                },
                error: function() {
                    alert('Erro de conexão');
                }
            });
        }
        
        function editUser(userId) {
            $.get('/api/users/' + userId, function(data) {
                if (data.success) {
                    const user = data.user;
                    $('#editUserId').val(user.id);
                    $('#editNomeCompleto').val(user.nome_completo || '');
                    $('#editUsername').val(user.username);
                    $('#editEmail').val(user.email);
                    $('#editTipoUsuario').val(user.tipo_usuario);
                    $('#editAtivo').val(user.ativo ? '1' : '0');
                    
                    generatePermissionsHTML('editPermissions', user.permissions || {});
                    $('#editUserModal').addClass('show');
                }
            });
        }
        
        function updateUser() {
            const formData = new FormData($('#editUserForm')[0]);
            const permissions = getFormPermissions('editPermissions');
            const userId = formData.get('user_id');
            
            const userData = {
                nome_completo: formData.get('nome_completo'),
                username: formData.get('username'),
                email: formData.get('email'),
                tipo_usuario: formData.get('tipo_usuario'),
                ativo: formData.get('ativo') === '1',
                permissions: permissions
            };
            
            $.ajax({
                url: '/api/users/' + userId,
                method: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(userData),
                success: function(data) {
                    if (data.success) {
                        alert('Usuário atualizado com sucesso!');
                        closeModal('editUserModal');
                        loadUsers();
                    } else {
                        alert('Erro: ' + data.message);
                    }
                },
                error: function() {
                    alert('Erro de conexão');
                }
            });
        }
        
        function resetUserPassword(userId, username) {
            if (confirm('Resetar senha do usuário ' + username + '?')) {
                $.post('/api/users/' + userId + '/reset-password', function(data) {
                    if (data.success) {
                        alert('Senha resetada!\\nNova senha: ' + data.password + '\\n\\nAnote esta senha!');
                        loadUsers();
                    } else {
                        alert('Erro: ' + data.message);
                    }
                });
            }
        }
        
        function toggleUser(userId, newStatus) {
            const action = newStatus ? 'ativar' : 'desativar';
            if (confirm('Confirma ' + action + ' este usuário?')) {
                $.post('/api/users/' + userId + '/toggle', function(data) {
                    if (data.success) {
                        alert(data.message);
                        loadUsers();
                    } else {
                        alert('Erro: ' + data.message);
                    }
                });
            }
        }
        
        function openChangePasswordModal() {
            $('#changePasswordModal').addClass('show');
        }
        
        function changeMyPassword() {
            const formData = new FormData($('#changePasswordForm')[0]);
            
            if (formData.get('new_password') !== formData.get('confirm_password')) {
                alert('As senhas não coincidem!');
                return;
            }
            
            $.ajax({
                url: '/api/change-my-password',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    current_password: formData.get('current_password'),
                    new_password: formData.get('new_password')
                }),
                success: function(data) {
                    if (data.success) {
                        alert('Senha alterada com sucesso!');
                        closeModal('changePasswordModal');
                        $('#changePasswordForm')[0].reset();
                    } else {
                        alert('Erro: ' + data.message);
                    }
                },
                error: function() {
                    alert('Erro de conexão');
                }
            });
        }
        
        function closeModal(modalId) {
            $('#' + modalId).removeClass('show');
        }
        
        // Inicialização
        $(document).ready(function() {
            loadUsers();
            
            // Auto-refresh a cada 60 segundos
            setInterval(loadUsers, 60000);
            
            // Fechar modal clicando fora
            $('.modal').click(function(e) {
                if (e.target === this) {
                    $(this).removeClass('show');
                }
            });
        });
        </script>
    </body>
    </html>
    '''

# APIs expandidas
@app.route('/api/users')
@login_required
def api_users():
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nome_completo': user.nome_completo,
            'tipo_usuario': user.tipo_usuario,
            'ativo': user.ativo,
            'ultimo_login': user.ultimo_login.isoformat() if user.ultimo_login else None,
            'total_logins': user.total_logins or 0,
            'permissions': user.get_permissions()
        })
    
    return jsonify({'success': True, 'users': users_data})

@app.route('/api/users/<int:user_id>')
@login_required
def api_get_user(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nome_completo': user.nome_completo,
            'tipo_usuario': user.tipo_usuario,
            'ativo': user.ativo,
            'permissions': user.get_permissions()
        }
    })

@app.route('/api/users', methods=['POST'])
@login_required
def api_create_user():
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    data = request.get_json()
    
    # Validações
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Campos obrigatórios faltando'}), 400
    
    # Verificar se já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username já existe'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email já existe'}), 400
    
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            nome_completo=data.get('nome_completo', ''),
            tipo_usuario=data.get('tipo_usuario', 'user'),
            ativo=data.get('ativo', True)
        )
        user.set_password(data['password'])
        user.set_permissions(data.get('permissions', {}))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuário criado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def api_update_user(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    data = request.get_json()
    
    try:
        # Verificar username único
        if data.get('username') and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'success': False, 'message': 'Username já existe'}), 400
            user.username = data['username']
        
        # Verificar email único
        if data.get('email') and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'message': 'Email já existe'}), 400
            user.email = data['email']
        
        # Atualizar outros campos
        if 'nome_completo' in data:
            user.nome_completo = data['nome_completo']
        if 'tipo_usuario' in data:
            user.tipo_usuario = data['tipo_usuario']
        if 'ativo' in data:
            user.ativo = data['ativo']
        if 'permissions' in data:
            user.set_permissions(data['permissions'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def api_reset_user_password(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    try:
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Senha resetada com sucesso',
            'password': new_password
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def api_toggle_user(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Não pode alterar seu próprio status'}), 400
    
    try:
        user.ativo = not user.ativo
        db.session.commit()
        
        status = 'ativado' if user.ativo else 'desativado'
        return jsonify({
            'success': True,
            'message': f'Usuário {user.username} {status} com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/change-my-password', methods=['POST'])
@login_required
def api_change_my_password():
    data = request.get_json()
    
    if not current_user.check_password(data.get('current_password', '')):
        return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 400
    
    if len(data.get('new_password', '')) < 6:
        return jsonify({'success': False, 'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
    
    try:
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Senha alterada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Criar admin padrão
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@transpontual.com',
                nome_completo='Administrador do Sistema',
                tipo_usuario='admin',
                ativo=True
            )
            admin.set_password('Admin123!')
            admin.set_permissions({module: True for module in MODULOS.keys()})
            db.session.add(admin)
            db.session.commit()
            print("Admin criado: admin / Admin123!")
        
        # Criar usuários teste
        test_users = [
            ('user1', 'user1@test.com', 'Usuário Teste 1', 'user'),
            ('user2', 'user2@test.com', 'Usuário Teste 2', 'user'),
        ]
        
        for username, email, nome, tipo in test_users:
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    email=email,
                    nome_completo=nome,
                    tipo_usuario=tipo,
                    ativo=True
                )
                user.set_password('123456')
                # Dar permissões básicas aos usuários teste
                user.set_permissions({'dashboard': True, 'ctes': True, 'baixas': True})
                db.session.add(user)
        
        db.session.commit()
        print("Usuários teste criados")
    
    print("\n" + "="*50)
    print("SISTEMA ADMINISTRATIVO COMPLETO")
    print("="*50)
    print("URL: http://localhost:5000")
    print("Login Admin: admin / Admin123!")
    print("Login Usuário: user1 / 123456")
    print("\nFuncionalidades:")
    print("- Criar/editar usuários")
    print("- Sistema de permissões por módulos")  
    print("- Alterar própria senha")
    print("- Reset de senhas")
    print("- Ativação/desativação")
    print("="*50)
    
    app.run(debug=True, port=5000)