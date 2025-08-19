#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação Rápida - Confirmar se rota de login existe
Execute este script para verificar especificamente a rota de login
"""

import os

def verificar_login_especifico():
    """Verifica especificamente a rota de login"""
    
    print("🔍 VERIFICAÇÃO ESPECÍFICA - ROTA DE LOGIN")
    print("=" * 45)
    
    auth_file = "app/routes/auth.py"
    
    if not os.path.exists(auth_file):
        print("❌ Arquivo auth.py não encontrado!")
        return False
    
    with open(auth_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificações específicas da rota de login
    checks = [
        ("Rota de login (com métodos)", "@bp.route('/login', methods=['GET', 'POST'])"),
        ("Rota de login (simples)", "@bp.route('/login')"),
        ("Função login", "def login():"),
        ("Blueprint definido", "bp = Blueprint('auth'"),
        ("Import Flask", "from flask import Blueprint"),
        ("Render template login", "render_template('auth/login.html')"),
        ("Flash messages", "flash("),
        ("Login user", "login_user(")
    ]
    
    encontrados = []
    nao_encontrados = []
    
    for desc, pattern in checks:
        if pattern in content:
            encontrados.append(f"✅ {desc}")
        else:
            nao_encontrados.append(f"❌ {desc}")
    
    print("RESULTADOS:")
    for item in encontrados:
        print(f"  {item}")
    
    if nao_encontrados:
        print("\nNÃO ENCONTRADOS:")
        for item in nao_encontrados:
            print(f"  {item}")
    
    # Verificar se pelo menos uma versão da rota login existe
    has_login_route = (
        "@bp.route('/login')" in content or 
        "@bp.route('/login', methods=" in content
    )
    has_login_function = "def login():" in content
    
    print(f"\n📊 RESUMO:")
    print(f"✅ Rota de login existe: {'SIM' if has_login_route else 'NÃO'}")
    print(f"✅ Função login existe: {'SIM' if has_login_function else 'NÃO'}")
    
    if has_login_route and has_login_function:
        print("\n🎉 ROTA DE LOGIN ESTÁ CORRETA!")
        print("💡 O erro do script anterior foi um falso positivo.")
        return True
    else:
        print("\n❌ ROTA DE LOGIN TEM PROBLEMAS!")
        return False

def mostrar_trecho_login():
    """Mostra o trecho específico da rota de login"""
    
    auth_file = "app/routes/auth.py"
    
    if not os.path.exists(auth_file):
        return
    
    with open(auth_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n📄 TRECHO DA ROTA DE LOGIN:")
    print("-" * 40)
    
    in_login_function = False
    login_lines = []
    
    for i, line in enumerate(lines):
        # Procurar início da rota login
        if "@bp.route('/login'" in line:
            in_login_function = True
            login_lines.append(f"{i+1:3d}: {line.rstrip()}")
        elif in_login_function:
            login_lines.append(f"{i+1:3d}: {line.rstrip()}")
            
            # Parar na próxima rota ou fim da função
            if line.startswith("@bp.route") and "login" not in line:
                break
            if line.startswith("def ") and "login" not in line:
                break
            if len(login_lines) > 30:  # Limite de segurança
                break
    
    if login_lines:
        for line in login_lines[:20]:  # Mostrar até 20 linhas
            print(line)
        if len(login_lines) > 20:
            print("... (truncado)")
    else:
        print("❌ Trecho da rota de login não encontrado")

if __name__ == "__main__":
    verificar_login_especifico()
    mostrar_trecho_login()
    
    print("\n" + "=" * 50)
    print("🚀 CONCLUSÃO:")
    print("Se a rota de login foi encontrada, o sistema deve funcionar.")
    print("Execute: python iniciar.py")
    print("=" * 50)