#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Financeiro Baker - Inicializador Flask CORRIGIDO
Conecta ao banco existente no Supabase
"""

import os
import sys
from app import create_app, db

def verificar_conexao_banco():
    """Verifica conexão com o banco existente"""
    try:
        from app.models.user import User
        from app.models.cte import CTE
        
        # Testar conexão
        total_ctes = CTE.query.count()
        total_users = User.query.count()
        
        print(f"✅ Conectado ao banco Supabase")
        print(f"📊 {total_ctes} CTEs encontrados")
        print(f"👥 {total_users} usuários cadastrados")
        
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def criar_usuario_admin():
    """Cria usuário admin se não existir - VERSÃO CORRIGIDA"""
    try:
        from app.models.user import User
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # ✅ CRIAÇÃO CORRETA DO ADMIN
            admin = User(
                username='admin',
                email='admin@dashboardbaker.com',
                nome_completo='Administrador do Sistema',
                tipo_usuario='admin',  # ← CORREÇÃO PRINCIPAL!
                ativo=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado (admin/Admin123!)")
        else:
            # ✅ CORRIGIR ADMIN EXISTENTE SE NECESSÁRIO
            if admin.tipo_usuario != 'admin':
                print("🔧 Corrigindo tipo do usuário admin...")
                admin.tipo_usuario = 'admin'
                admin.set_password('Admin123!')  # Reset da senha também
                db.session.commit()
                print("✅ Tipo do admin corrigido para 'admin'")
            else:
                print("✅ Usuário admin já existe e está correto")
            
        return True
    except Exception as e:
        print(f"❌ Erro ao criar/corrigir usuário: {e}")
        return False

def main():
    """Função principal CORRIGIDA"""
    print("🚀 DASHBOARD FINANCEIRO BAKER - VERSÃO CORRIGIDA")
    print("=" * 60)
    print("🔗 Conectando ao banco Supabase existente...")
    
    # Criar aplicação
    app = create_app()
    
    with app.app_context():
        # Verificar conexão com banco existente
        if not verificar_conexao_banco():
            print("❌ Erro: Não foi possível conectar ao banco")
            print("💡 Verifique as credenciais do Supabase")
            sys.exit(1)
        
        # Criar/verificar/corrigir usuário admin
        try:
            db.create_all()  # Cria apenas tabelas que não existem (users)
            criar_usuario_admin()
            
            # ✅ VERIFICAÇÃO FINAL
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if admin and admin.is_admin:
                print(f"✅ Admin verificado: {admin.username} (tipo: {admin.tipo_usuario})")
                print("👑 Módulo de administração disponível!")
            else:
                print("❌ ERRO: Admin ainda não está correto!")
                
        except Exception as e:
            print(f"⚠️ Aviso: {e}")
    
    print("\n🌐 Servidor iniciado em: http://localhost:5000")
    print("👤 Login: admin")
    print("🔑 Senha: Admin123!")
    print("📊 Usando banco existente com seus dados")
    print("👑 Módulo Admin: Menu aparecerá após login")
    print("=" * 60)
    print("💡 Pressione Ctrl+C para parar\n")
    
    # Executar aplicação
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard Baker encerrado!")

if __name__ == '__main__':
    main()