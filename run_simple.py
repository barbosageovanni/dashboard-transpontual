# run_simple.py - Sistema Administrativo Funcional
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'transpontual-secret-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
        if user and user.check_password(password):
            login_user(user)
            return redirect('/admin')
        
        return "Credenciais invalidas", 401
    
    return '''
    <html>
    <head>
        <title>Login - Transpontual</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; margin: 50px; }
            .login { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 10px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .help { margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="login">
            <h2>Dashboard Transpontual</h2>
            <form method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Senha" required>
                <button type="submit">Entrar</button>
            </form>
            <div class="help">
                <b>Credenciais de teste:</b><br>
                Username: admin<br>
                Senha: Admin123!
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin')
@login_required
def admin():
    if current_user.tipo_usuario != 'admin':
        return "Acesso negado", 403
    
    return '''
    <html>
    <head>
        <title>Admin - Usuarios</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .header { background: #007bff; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: flex; gap: 15px; margin-bottom: 20px; }
            .stat { flex: 1; background: white; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-num { font-size: 24px; font-weight: bold; color: #007bff; }
            .users { background: white; border-radius: 8px; overflow: hidden; }
            .user { padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
            .btn { padding: 8px 12px; margin: 0 5px; border: none; border-radius: 4px; cursor: pointer; color: white; }
            .btn-warning { background: #ffc107; color: black; }
            .btn-danger { background: #dc3545; }
            .btn-success { background: #28a745; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Gerenciamento de Usuarios</h1>
            <p>Usuario logado: ''' + current_user.username + '''</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-num" id="total">0</div>
                <div>Total</div>
            </div>
            <div class="stat">
                <div class="stat-num" id="active">0</div>
                <div>Ativos</div>
            </div>
            <div class="stat">
                <div class="stat-num" id="admins">0</div>
                <div>Admins</div>
            </div>
        </div>
        
        <div class="users" id="users">
            <div style="padding: 20px; text-align: center;">Carregando...</div>
        </div>
        
        <script>
        function loadUsers() {
            $.get('/api/users', function(data) {
                if (data.success) {
                    showUsers(data.users);
                    updateStats(data.users);
                }
            });
        }
        
        function updateStats(users) {
            $('#total').text(users.length);
            $('#active').text(users.filter(u => u.ativo).length);
            $('#admins').text(users.filter(u => u.tipo_usuario === 'admin').length);
        }
        
        function showUsers(users) {
            var html = '';
            users.forEach(function(user) {
                html += '<div class="user">';
                html += '<div><b>' + (user.nome_completo || user.username) + '</b><br>';
                html += '<small>' + user.email + ' | ' + user.tipo_usuario + ' | ';
                html += (user.ativo ? 'Ativo' : 'Inativo') + '</small></div>';
                html += '<div>';
                html += '<button class="btn btn-warning" onclick="resetPass(' + user.id + ')">Reset</button>';
                html += '<button class="btn ' + (user.ativo ? 'btn-danger' : 'btn-success') + '" ';
                html += 'onclick="toggleUser(' + user.id + ')">' + (user.ativo ? 'Desativar' : 'Ativar') + '</button>';
                html += '</div></div>';
            });
            $('#users').html(html);
        }
        
        function resetPass(userId) {
            if (confirm('Resetar senha?')) {
                $.post('/api/users/' + userId + '/reset', function(data) {
                    if (data.success) {
                        alert('Nova senha: ' + data.password);
                    }
                });
            }
        }
        
        function toggleUser(userId) {
            $.post('/api/users/' + userId + '/toggle', function(data) {
                if (data.success) {
                    alert(data.message);
                    loadUsers();
                }
            });
        }
        
        $(document).ready(function() {
            loadUsers();
        });
        </script>
    </body>
    </html>
    '''

@app.route('/api/users')
@login_required
def api_users():
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False}), 403
    
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
            'total_logins': user.total_logins or 0
        })
    
    return jsonify({'success': True, 'users': users_data})

@app.route('/api/users/<int:user_id>/reset', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False}), 404
    
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Senha resetada',
        'password': new_password
    })

@app.route('/api/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False}), 404
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Nao pode desativar a si mesmo'}), 400
    
    user.ativo = not user.ativo
    db.session.commit()
    
    status = 'ativado' if user.ativo else 'desativado'
    return jsonify({
        'success': True,
        'message': f'Usuario {user.username} {status}'
    })

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Criar admin se nao existir
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
        
        # Criar usuarios teste
        test_users = [
            ('user1', 'user1@test.com', 'Usuario 1'),
            ('user2', 'user2@test.com', 'Usuario 2'),
            ('user3', 'user3@test.com', 'Usuario 3')
        ]
        
        for username, email, nome in test_users:
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    email=email,
                    nome_completo=nome,
                    tipo_usuario='user',
                    ativo=True
                )
                user.set_password('123456')
                db.session.add(user)
        
        db.session.commit()
        print("Usuarios teste criados")
    
    print("\n" + "="*40)
    print("SISTEMA ADMINISTRATIVO FUNCIONANDO")
    print("="*40)
    print("URL: http://localhost:5000")
    print("Login: admin / Admin123!")
    print("="*40)
    
    app.run(debug=True, port=5000)