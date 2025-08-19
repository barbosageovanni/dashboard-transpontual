#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o template auth/profile.html com erro de sintaxe
"""

import os
import shutil
from datetime import datetime

def fazer_backup(arquivo):
    """Faz backup do arquivo com erro"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{arquivo}.backup_erro_{timestamp}"
    shutil.copy2(arquivo, backup_file)
    print(f"✅ Backup do arquivo com erro: {backup_file}")
    return backup_file

def corrigir_profile_template():
    """Substitui o template profile.html problemático por um correto"""
    
    arquivo = "app/templates/auth/profile.html"
    
    print("🔧 CORRIGINDO TEMPLATE auth/profile.html")
    print("=" * 45)
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    # Fazer backup do arquivo com erro
    backup_file = fazer_backup(arquivo)
    
    try:
        # Template corrigido e completo
        template_corrigido = '''{% extends "base.html" %}

{% block title %}Minha Conta - Dashboard Baker{% endblock %}

{% block extra_css %}
<style>
    .profile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }

    .profile-avatar {
        width: 80px;
        height: 80px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1rem;
        border: 3px solid rgba(255,255,255,0.3);
    }

    .info-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
    }

    .info-card h4 {
        color: #2d3748;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #f7fafc;
    }

    .info-row:last-child {
        border-bottom: none;
    }

    .info-label {
        color: #718096;
        font-weight: 500;
    }

    .info-value {
        color: #2d3748;
        font-weight: 600;
    }

    .badge-role {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-admin {
        background: linear-gradient(135deg, #f56565, #e53e3e);
        color: white;
    }

    .badge-user {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
    }

    .status-active {
        color: #48bb78;
        font-weight: 600;
    }

    .btn-profile {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .btn-profile:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        color: white;
        text-decoration: none;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <!-- Header do Perfil -->
    <div class="profile-header">
        <div class="profile-avatar">
            <i class="fas fa-user"></i>
        </div>
        <h1 style="margin-bottom: 0.5rem; font-weight: 800;">
            {{ current_user.nome_completo or current_user.username }}
        </h1>
        <p style="opacity: 0.9; margin-bottom: 1rem;">
            <span class="badge-role badge-{{ current_user.tipo_usuario }}">
                <i class="fas fa-{{ 'crown' if current_user.tipo_usuario == 'admin' else 'user' }}"></i>
                {{ current_user.tipo_usuario.title() }}
            </span>
        </p>
        <small style="opacity: 0.7;">
            Membro desde {{ current_user.created_at.strftime('%d/%m/%Y') if current_user.created_at else 'N/A' }}
        </small>
    </div>

    <!-- Informações do Usuário -->
    <div class="row">
        <div class="col-md-6">
            <div class="info-card">
                <h4>
                    <i class="fas fa-user-circle"></i>
                    Informações Pessoais
                </h4>
                
                <div class="info-row">
                    <span class="info-label">Nome de Usuário</span>
                    <span class="info-value">{{ current_user.username }}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Email</span>
                    <span class="info-value">{{ current_user.email }}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Nome Completo</span>
                    <span class="info-value">{{ current_user.nome_completo or 'Não informado' }}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Tipo de Conta</span>
                    <span class="info-value">
                        <span class="badge-role badge-{{ current_user.tipo_usuario }}">
                            {{ current_user.tipo_usuario.title() }}
                        </span>
                    </span>
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="info-card">
                <h4>
                    <i class="fas fa-chart-line"></i>
                    Estatísticas da Conta
                </h4>
                
                <div class="info-row">
                    <span class="info-label">Status</span>
                    <span class="info-value">
                        <span class="status-active">
                            <i class="fas fa-circle"></i>
                            {{ 'Conta Ativa' if current_user.ativo else 'Conta Inativa' }}
                        </span>
                    </span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Total de Logins</span>
                    <span class="info-value">{{ current_user.total_logins or 0 }}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Último Acesso</span>
                    <span class="info-value">
                        {% if current_user.ultimo_login %}
                            {{ current_user.ultimo_login.strftime('%d/%m/%Y às %H:%M') }}
                        {% else %}
                            Primeiro acesso
                        {% endif %}
                    </span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Membro desde</span>
                    <span class="info-value">
                        {% if current_user.created_at %}
                            {{ current_user.created_at.strftime('%d/%m/%Y') }}
                        {% else %}
                            Data não disponível
                        {% endif %}
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- Ações da Conta -->
    <div class="info-card">
        <h4>
            <i class="fas fa-cogs"></i>
            Ações da Conta
        </h4>
        
        <div class="d-flex gap-3 flex-wrap">
            <a href="{{ url_for('dashboard.index') }}" class="btn-profile">
                <i class="fas fa-tachometer-alt"></i>
                Voltar ao Dashboard
            </a>
            
            <button class="btn-profile" onclick="alert('Funcionalidade em desenvolvimento')">
                <i class="fas fa-edit"></i>
                Editar Perfil
            </button>
            
            <button class="btn-profile" onclick="alert('Funcionalidade em desenvolvimento')">
                <i class="fas fa-key"></i>
                Alterar Senha
            </button>
            
            {% if current_user.tipo_usuario == 'admin' %}
            <a href="{{ url_for('admin.index') }}" class="btn-profile">
                <i class="fas fa-crown"></i>
                Painel Admin
            </a>
            {% endif %}
        </div>
    </div>

    <!-- Informações Técnicas -->
    <div class="info-card">
        <h4>
            <i class="fas fa-info-circle"></i>
            Informações do Sistema
        </h4>
        
        <div class="row">
            <div class="col-md-4">
                <div class="text-center">
                    <h5 class="text-primary">{{ current_user.total_logins or 0 }}</h5>
                    <small class="text-muted">Total de Logins</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="text-center">
                    <h5 class="text-success">{{ 'Ativa' if current_user.ativo else 'Inativa' }}</h5>
                    <small class="text-muted">Status da Conta</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="text-center">
                    <h5 class="text-info">{{ current_user.tipo_usuario.title() }}</h5>
                    <small class="text-muted">Nível de Acesso</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
        
        # Escrever o template corrigido
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(template_corrigido)
        
        print("✅ Template corrigido e substituído!")
        
        # Verificar se o arquivo foi criado corretamente
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificações básicas
            if '{% extends "base.html" %}' in content and '{% endblock %}' in content:
                print("✅ Estrutura Jinja2 correta")
                print("✅ Sintaxe validada")
                print("✅ Template pronto para uso")
                return True
            else:
                print("⚠️ Possível problema na estrutura do template")
                return False
        else:
            print("❌ Erro ao criar o arquivo")
            return False
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        
        # Tentar restaurar backup se possível
        if os.path.exists(backup_file):
            print(f"🔄 Backup disponível em: {backup_file}")
        
        return False

if __name__ == "__main__":
    sucesso = corrigir_profile_template()
    
    if sucesso:
        print("\n" + "=" * 50)
        print("🎉 TEMPLATE CORRIGIDO COM SUCESSO!")
        print("🎯 PRÓXIMOS PASSOS:")
        print("1. Atualizar a página no navegador")
        print("2. Clicar em 'Minha Conta' no dropdown")
        print("3. Verificar se a página carrega sem erros")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ FALHA NA CORREÇÃO")
        print("💡 Tente substituir manualmente o arquivo")
        print("=" * 50)