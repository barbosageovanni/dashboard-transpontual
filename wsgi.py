#!/usr/bin/env python3
import os
import sys

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_working_app():
    """App Flask completa SEM banco de dados"""
    from flask import Flask, render_template_string, request, redirect, session, flash, jsonify
    
    app = Flask(__name__)
    app.secret_key = 'transpontual-production-key-2025'
    
    # Usuários em memória (temporário)
    USERS = {
        'admin': {
            'password': 'Admin123!',
            'nome': 'Administrador Sistema',
            'email': 'admin@transpontual.app.br',
            'tipo': 'admin'
        }
    }
    
    # CTEs de exemplo em memória
    CTES_EXEMPLO = [
        {'numero': '001', 'cliente': 'Cliente A', 'valor': 5500.00, 'status': 'Pago'},
        {'numero': '002', 'cliente': 'Cliente B', 'valor': 3200.50, 'status': 'Pendente'},
        {'numero': '003', 'cliente': 'Cliente C', 'valor': 7800.00, 'status': 'Processando'},
        {'numero': '004', 'cliente': 'Cliente A', 'valor': 4100.25, 'status': 'Pago'},
        {'numero': '005', 'cliente': 'Cliente D', 'valor': 2900.75, 'status': 'Pendente'},
    ]
    
    @app.route('/')
    def home():
        if 'user' in session:
            return redirect('/dashboard')
        return redirect('/login')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if username in USERS and USERS[username]['password'] == password:
                session['user'] = username
                session['user_data'] = USERS[username]
                return redirect('/dashboard')
            else:
                flash('Credenciais inválidas', 'error')
        
        return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Dashboard Transpontual</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .login-container { max-width: 400px; margin: 10% auto; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .card-header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 15px 15px 0 0; }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); border: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-container">
            <div class="card">
                <div class="card-header text-center">
                    <h3><i class="fas fa-truck"></i> Dashboard Transpontual</h3>
                    <p class="mb-0">Sistema de Gestão Financeira</p>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-danger">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Usuário</label>
                            <input type="text" class="form-control" name="username" value="admin" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Senha</label>
                            <input type="password" class="form-control" name="password" value="Admin123!" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-sign-in-alt"></i> Entrar
                        </button>
                    </form>
                    
                    <div class="text-center mt-3">
                        <small class="text-muted">
                            ✅ Sistema Online | 🚂 Railway Deploy | 💾 Modo Offline
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        ''')
    
    @app.route('/dashboard')
    def dashboard():
        if 'user' not in session:
            return redirect('/login')
        
        # Calcular métricas dos CTEs exemplo
        total_ctes = len(CTES_EXEMPLO)
        valor_total = sum(cte['valor'] for cte in CTES_EXEMPLO)
        valor_pago = sum(cte['valor'] for cte in CTES_EXEMPLO if cte['status'] == 'Pago')
        valor_pendente = sum(cte['valor'] for cte in CTES_EXEMPLO if cte['status'] == 'Pendente')
        
        return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Transpontual</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea, #764ba2); }
        .card { border: none; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .metric-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .metric-value { font-size: 2rem; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="fas fa-truck"></i> Dashboard Transpontual</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">👤 {{ session.user_data.nome }}</span>
                <a class="nav-link" href="/logout">Sair</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col">
                <h1><i class="fas fa-tachometer-alt"></i> Dashboard Financeiro</h1>
                <p class="text-muted">Sistema de gestão financeira - Modo offline com dados de exemplo</p>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-file-invoice fa-2x mb-2"></i>
                        <div class="metric-value">{{ total_ctes }}</div>
                        <div>Total CTEs</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-dollar-sign fa-2x mb-2"></i>
                        <div class="metric-value">R$ {{ "%.2f"|format(valor_total) }}</div>
                        <div>Valor Total</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-check-circle fa-2x mb-2"></i>
                        <div class="metric-value">R$ {{ "%.2f"|format(valor_pago) }}</div>
                        <div>Valor Pago</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x mb-2"></i>
                        <div class="metric-value">R$ {{ "%.2f"|format(valor_pendente) }}</div>
                        <div>Valor Pendente</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> CTEs Recentes</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Número</th>
                                        <th>Cliente</th>
                                        <th>Valor</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for cte in ctes %}
                                    <tr>
                                        <td>{{ cte.numero }}</td>
                                        <td>{{ cte.cliente }}</td>
                                        <td>R$ {{ "%.2f"|format(cte.valor) }}</td>
                                        <td>
                                            {% if cte.status == 'Pago' %}
                                                <span class="badge bg-success">{{ cte.status }}</span>
                                            {% elif cte.status == 'Pendente' %}
                                                <span class="badge bg-warning">{{ cte.status }}</span>
                                            {% else %}
                                                <span class="badge bg-info">{{ cte.status }}</span>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle"></i> Status do Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <strong>Sistema:</strong> <span class="badge bg-success">Online</span>
                        </div>
                        <div class="mb-3">
                            <strong>Deploy:</strong> <span class="badge bg-primary">Railway</span>
                        </div>
                        <div class="mb-3">
                            <strong>Banco:</strong> <span class="badge bg-warning">Offline</span>
                        </div>
                        <div class="mb-3">
                            <strong>Dados:</strong> <span class="badge bg-info">Exemplo</span>
                        </div>
                        <hr>
                        <p class="small text-muted">
                            Sistema funcionando em modo offline com dados de exemplo. 
                            Banco de dados será configurado posteriormente.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        ''', total_ctes=total_ctes, valor_total=valor_total, 
             valor_pago=valor_pago, valor_pendente=valor_pendente, ctes=CTES_EXEMPLO)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/login')
    
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "service": "dashboard-transpontual",
            "mode": "offline",
            "database": "disabled",
            "authentication": "memory-based"
        }
    
    return app

# Criar aplicação sem banco
print("🔄 Iniciando Dashboard Transpontual (Modo Offline)...")
application = create_working_app()
print("✅ Sistema funcionando sem banco de dados!")

# Exportar para Gunicorn
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
