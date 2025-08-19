#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOLUÇÃO DEFINITIVA - MÓDULO DE ADMINISTRAÇÃO
Execute: python solucao_definitiva.py

Este script resolve TODOS os problemas do módulo admin de uma vez
"""

import os
import sys
from pathlib import Path

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    print("🔍 VERIFICANDO ARQUIVOS NECESSÁRIOS...")
    
    arquivos_necessarios = {
        'app/routes/admin.py': 'Rotas de administração',
        'app/templates/admin/index.html': 'Template principal admin',
        'app/templates/admin/users.html': 'Template de usuários',
        'app/__init__.py': 'Inicializador da app'
    }
    
    arquivos_faltando = []
    
    for arquivo, descricao in arquivos_necessarios.items():
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo} - {descricao}")
        else:
            print(f"   ❌ {arquivo} - {descricao} (FALTANDO)")
            arquivos_faltando.append(arquivo)
    
    return arquivos_faltando

def criar_arquivo_admin_routes():
    """Cria o arquivo app/routes/admin.py"""
    print("📝 Criando app/routes/admin.py...")
    
    os.makedirs('app/routes', exist_ok=True)
    
    conteudo = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/routes/admin.py - Rotas de Administração
Gerado automaticamente pelo script de correção
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User
from app.models.cte import CTE
from app import db
from datetime import datetime
from sqlalchemy import func

# Criar blueprint
bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator para requerer acesso de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Página principal de administração"""
    return render_template('admin/index.html')

@bp.route('/users')
@login_required
@admin_required
def users():
    """Gerenciamento de usuários"""
    usuarios = User.query.all()
    return render_template('admin/users.html', usuarios=usuarios)

@bp.route('/system-info')
@login_required
@admin_required
def system_info():
    """Informações do sistema"""
    try:
        stats = {
            'total_usuarios': User.query.count(),
            'usuarios_ativos': User.query.filter_by(ativo=True).count(),
            'admins': User.query.filter_by(tipo_usuario='admin').count(),
            'total_ctes': CTE.query.count(),
            'valor_total': db.session.query(func.sum(CTE.valor_total)).scalar() or 0,
            'timestamp': datetime.now()
        }
        return render_template('admin/system_info.html', stats=stats)
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

@bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API para estatísticas"""
    try:
        stats = {
            'sistema': {
                'total_usuarios': User.query.count(),
                'usuarios_ativos': User.query.filter_by(ativo=True).count(),
                'administradores': User.query.filter_by(tipo_usuario='admin').count(),
            },
            'dados': {
                'total_ctes': CTE.query.count(),
                'valor_total': float(db.session.query(func.sum(CTE.valor_total)).scalar() or 0),
            }
        }
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''
    
    with open('app/routes/admin.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("   ✅ app/routes/admin.py criado!")

def criar_template_admin():
    """Cria os templates admin"""
    print("📝 Criando templates admin...")
    
    os.makedirs('app/templates/admin', exist_ok=True)
    
    # Template principal
    template_index = '''{% extends "base.html" %}

{% block title %}Painel de Administração{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h4><i class="fas fa-crown"></i> Painel de Administração</h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-success">
                        <h5>🎉 Módulo Admin Funcionando!</h5>
                        <p>Bem-vindo ao painel de administração, <strong>{{ current_user.username }}</strong>!</p>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h5><i class="fas fa-users"></i> Gerenciar Usuários</h5>
                                    <p>Criar, editar e remover usuários do sistema</p>
                                    <a href="{{ url_for('admin.users') }}" class="btn btn-primary">
                                        Acessar
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h5><i class="fas fa-info-circle"></i> Informações do Sistema</h5>
                                    <p>Ver estatísticas e detalhes técnicos</p>
                                    <a href="{{ url_for('admin.system_info') }}" class="btn btn-info">
                                        Ver Detalhes
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-12">
                            <h6>Estatísticas Rápidas:</h6>
                            <div id="stats-container">
                                <p>Carregando estatísticas...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
$(document).ready(function() {
    // Carregar estatísticas
    $.ajax({
        url: '/admin/api/stats',
        success: function(data) {
            if (data.success) {
                const stats = data.stats;
                $('#stats-container').html(`
                    <div class="row">
                        <div class="col-md-3 text-center">
                            <h4>${stats.sistema.total_usuarios}</h4>
                            <small>Total Usuários</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <h4>${stats.sistema.administradores}</h4>
                            <small>Administradores</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <h4>${stats.dados.total_ctes}</h4>
                            <small>CTEs Total</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <h4>R$ ${stats.dados.valor_total.toLocaleString('pt-BR')}</h4>
                            <small>Valor Total</small>
                        </div>
                    </div>
                `);
            }
        },
        error: function() {
            $('#stats-container').html('<p class="text-danger">Erro ao carregar estatísticas</p>');
        }
    });
});
</script>
{% endblock %}'''
    
    with open('app/templates/admin/index.html', 'w', encoding='utf-8') as f:
        f.write(template_index)
    
    # Template de usuários simples
    template_users = '''{% extends "base.html" %}

{% block title %}Gerenciar Usuários{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="card">
        <div class="card-header">
            <h4><i class="fas fa-users"></i> Gerenciar Usuários</h4>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Tipo</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for usuario in usuarios %}
                        <tr>
                            <td>{{ usuario.id }}</td>
                            <td>{{ usuario.username }}</td>
                            <td>{{ usuario.email }}</td>
                            <td>
                                {% if usuario.is_admin %}
                                    <span class="badge bg-success">Admin</span>
                                {% else %}
                                    <span class="badge bg-primary">User</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if usuario.ativo %}
                                    <span class="badge bg-success">Ativo</span>
                                {% else %}
                                    <span class="badge bg-danger">Inativo</span>
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
{% endblock %}'''
    
    with open('app/templates/admin/users.html', 'w', encoding='utf-8') as f:
        f.write(template_users)
    
    print("   ✅ Templates admin criados!")

def corrigir_usuario_admin():
    """Corrige o usuário admin no banco"""
    print("🔧 CORRIGINDO USUÁRIO ADMIN...")
    
    try:
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                admin.tipo_usuario = 'admin'
                admin.ativo = True
                admin.set_password('Admin123!')
                db.session.commit()
                print(f"   ✅ Admin corrigido: tipo='{admin.tipo_usuario}', is_admin={admin.is_admin}")
            else:
                admin = User(
                    username='admin',
                    email='admin@dashboardbaker.com',
                    nome_completo='Administrador',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("   ✅ Admin criado com sucesso!")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Erro ao corrigir admin: {e}")
        return False

def testar_sistema():
    """Testa se o sistema está funcionando"""
    print("🧪 TESTANDO SISTEMA...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Verificar blueprints
            blueprints = list(app.blueprints.keys())
            print(f"   📦 Blueprints: {blueprints}")
            
            if 'admin' in blueprints:
                print("   ✅ Blueprint admin registrado!")
            else:
                print("   ❌ Blueprint admin não encontrado!")
                return False
            
            # Verificar rotas admin
            admin_routes = []
            for rule in app.url_map.iter_rules():
                if 'admin' in rule.rule:
                    admin_routes.append(rule.rule)
            
            print(f"   🔗 Rotas admin: {admin_routes}")
            
            # Verificar usuário admin
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            
            if admin and admin.is_admin:
                print(f"   👑 Admin OK: {admin.username} (is_admin={admin.is_admin})")
                return True
            else:
                print(f"   ❌ Admin com problema!")
                return False
                
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

def main():
    """Função principal - executa todas as correções"""
    print("🚀 SOLUÇÃO DEFINITIVA - MÓDULO ADMINISTRAÇÃO")
    print("=" * 60)
    
    # Passo 1: Verificar arquivos
    arquivos_faltando = verificar_arquivos()
    
    # Passo 2: Criar arquivos faltando
    if 'app/routes/admin.py' in arquivos_faltando:
        criar_arquivo_admin_routes()
    
    if any('admin' in arquivo for arquivo in arquivos_faltando):
        criar_template_admin()
    
    # Passo 3: Corrigir usuário admin
    admin_ok = corrigir_usuario_admin()
    
    # Passo 4: Testar sistema
    sistema_ok = testar_sistema()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print(f"   ✅ Arquivos criados: {'OK' if not arquivos_faltando else 'Pendente'}")
    print(f"   ✅ Usuário admin: {'OK' if admin_ok else 'ERRO'}")
    print(f"   ✅ Sistema funcionando: {'OK' if sistema_ok else 'ERRO'}")
    
    if admin_ok and sistema_ok:
        print(f"\n🎉 SUCESSO TOTAL!")
        print(f"📝 PRÓXIMOS PASSOS:")
        print(f"   1. Execute: python iniciar.py")
        print(f"   2. Acesse: http://localhost:5000")
        print(f"   3. Login: admin")
        print(f"   4. Senha: Admin123!")
        print(f"   5. Menu 'Administração' deve aparecer!")
        print(f"\n💡 VERIFICAÇÕES:")
        print(f"   • Menu verde 'Administração' na navbar")
        print(f"   • Badge 'Admin' ao lado do nome")
        print(f"   • Acesso ao /admin funcionando")
    else:
        print(f"\n❌ AINDA HÁ PROBLEMAS!")
        print(f"📝 VERIFICAR:")
        print(f"   • Logs de erro no terminal")
        print(f"   • Arquivo app/__init__.py")
        print(f"   • Modelo User propriedade is_admin")
    
    print("=" * 60)

if __name__ == '__main__':
    main()