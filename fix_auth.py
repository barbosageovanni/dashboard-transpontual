#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO DO SISTEMA DE AUTENTICAÇÃO
Execute este script para corrigir problemas de login
"""

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

def corrigir_autenticacao():
    """Corrige problemas de autenticação do sistema"""
    print("=" * 60)
    print("🔧 CORREÇÃO DO SISTEMA DE AUTENTICAÇÃO")
    print("=" * 60)
    
    try:
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            print("\n1️⃣ VERIFICANDO USUÁRIOS NO BANCO...")
            usuarios = User.query.all()
            
            print(f"   Total de usuários: {len(usuarios)}")
            
            for user in usuarios:
                print(f"   - {user.username} ({user.email}) - Ativo: {user.ativo} - Tipo: {user.tipo_usuario}")
            
            print("\n2️⃣ CRIANDO/CORRIGINDO USUÁRIO ADMIN...")
            
            # Buscar ou criar usuário admin
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("   Criando usuário admin...")
                admin = User(
                    username='admin',
                    email='admin@transpontual.com',
                    nome_completo='Administrador do Sistema',
                    tipo_usuario='admin',
                    ativo=True
                )
                db.session.add(admin)
            else:
                print("   Usuário admin encontrado, verificando configurações...")
                admin.tipo_usuario = 'admin'
                admin.ativo = True
            
            # Definir senhas para testar
            senhas_teste = ['senha123', 'Admin123!', 'admin123', '123456']
            
            print(f"\n3️⃣ CONFIGURANDO MÚLTIPLAS SENHAS PARA TESTE...")
            
            for i, senha in enumerate(senhas_teste):
                admin.set_password(senha)
                db.session.commit()
                
                print(f"   ✅ Senha {i+1} configurada: {senha}")
                
                # Testar a senha
                if admin.check_password(senha):
                    print(f"   ✅ Verificação OK para: {senha}")
                else:
                    print(f"   ❌ Verificação FALHOU para: {senha}")
            
            # Usar a primeira senha como padrão
            admin.set_password(senhas_teste[0])  # senha123
            db.session.commit()
            
            print(f"\n4️⃣ USUÁRIO ADMIN CONFIGURADO:")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Senha padrão: {senhas_teste[0]}")
            print(f"   Tipo: {admin.tipo_usuario}")
            print(f"   Ativo: {admin.ativo}")
            
            print("\n5️⃣ TESTANDO AUTENTICAÇÃO...")
            
            # Testar login programático
            if admin.check_password(senhas_teste[0]):
                print("   ✅ Teste de senha: OK")
            else:
                print("   ❌ Teste de senha: FALHA")
            
            # Verificar se é admin
            if hasattr(admin, 'is_admin'):
                print(f"   Admin check: {admin.is_admin}")
            else:
                print("   Método is_admin não encontrado - verificando tipo_usuario")
                print(f"   Tipo usuário: {admin.tipo_usuario}")
            
            print("\n6️⃣ CREDENCIAIS PARA TESTE:")
            print("   " + "="*40)
            for i, senha in enumerate(senhas_teste):
                print(f"   Opção {i+1}: admin / {senha}")
            print("   " + "="*40)
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_login_direto():
    """Testa login diretamente no sistema"""
    print("\n7️⃣ TESTE DIRETO DE LOGIN...")
    
    try:
        from app import create_app
        from app.models.user import User
        
        app = create_app()
        
        with app.test_client() as client:
            # Testar diferentes combinações
            credenciais = [
                ('admin', 'senha123'),
                ('admin', 'Admin123!'),
                ('admin', 'admin123'),
                ('admin', '123456')
            ]
            
            for username, password in credenciais:
                print(f"\n   Testando: {username} / {password}")
                
                # Fazer POST para login
                response = client.post('/auth/login', data={
                    'username': username,
                    'password': password
                }, follow_redirects=False)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 302:
                    print("   ✅ Login bem-sucedido (redirect)")
                    location = response.headers.get('Location', '')
                    print(f"   Redirecionamento para: {location}")
                elif response.status_code == 200:
                    if 'dashboard' in response.data.decode().lower():
                        print("   ✅ Login bem-sucedido (página dashboard)")
                    else:
                        print("   ❌ Login falhou (permaneceu na página de login)")
                else:
                    print(f"   ⚠️ Status inesperado: {response.status_code}")
                    
    except Exception as e:
        print(f"   ❌ Erro no teste direto: {e}")

def verificar_sessao_flask():
    """Verifica configuração de sessão do Flask"""
    print("\n8️⃣ VERIFICANDO CONFIGURAÇÃO DE SESSÃO...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        print(f"   SECRET_KEY configurada: {'Sim' if app.config.get('SECRET_KEY') else 'Não'}")
        print(f"   SESSION_COOKIE_NAME: {app.config.get('SESSION_COOKIE_NAME', 'session')}")
        print(f"   PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME', 'Padrão')}")
        
        # Verificar se Flask-Login está configurado
        from flask_login import login_manager
        
        if hasattr(app, 'login_manager'):
            print("   ✅ Flask-Login configurado")
            print(f"   Login view: {app.login_manager.login_view}")
        else:
            print("   ❌ Flask-Login não configurado")
            
    except Exception as e:
        print(f"   ❌ Erro na verificação: {e}")

if __name__ == "__main__":
    try:
        corrigir_autenticacao()
        testar_login_direto()
        verificar_sessao_flask()
        
        print("\n" + "=" * 60)
        print("🏁 CORREÇÃO CONCLUÍDA")
        print("=" * 60)
        print("\nPróximos passos:")
        print("1. Reiniciar o servidor: python run.py")
        print("2. Acessar: http://localhost:5000/auth/login")
        print("3. Testar credenciais listadas acima")
        print("4. Se ainda não funcionar, executar: python fix_user_model.py")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()