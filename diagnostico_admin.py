#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico específico do problema de administração
Execute: python diagnostico_admin.py
"""

from app import create_app, db
from app.models.user import User

def diagnosticar_admin():
    """Diagnóstica o problema do admin"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 DIAGNÓSTICO ESPECÍFICO - USUÁRIO ADMIN")
            print("=" * 50)
            
            # Buscar usuário admin
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("❌ ERRO: Usuário admin não encontrado!")
                return False
            
            print(f"📋 DADOS DO USUÁRIO ADMIN:")
            print(f"   ID: {admin.id}")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Nome Completo: {admin.nome_completo}")
            print(f"   Tipo Usuário: '{admin.tipo_usuario}' ← PROBLEMA AQUI!")
            print(f"   Ativo: {admin.ativo}")
            print(f"   Total Logins: {admin.total_logins}")
            
            # Verificar propriedade is_admin
            print(f"\n🔍 VERIFICAÇÃO DA PROPRIEDADE is_admin:")
            print(f"   admin.is_admin = {admin.is_admin}")
            print(f"   Condição: admin.tipo_usuario == 'admin'")
            print(f"   Atual: '{admin.tipo_usuario}' == 'admin' = {admin.tipo_usuario == 'admin'}")
            
            # Verificar outros usuários
            print(f"\n👥 TODOS OS USUÁRIOS:")
            usuarios = User.query.all()
            for user in usuarios:
                print(f"   - {user.username}: tipo='{user.tipo_usuario}', is_admin={user.is_admin}")
            
            # Diagnosticar o template
            print(f"\n🎨 DIAGNÓSTICO DO TEMPLATE:")
            print(f"   Condição no template: current_user.is_authenticated and current_user.is_admin")
            print(f"   current_user.is_authenticated = True (assumindo)")
            print(f"   current_user.is_admin = {admin.is_admin}")
            print(f"   Resultado da condição = {True and admin.is_admin}")
            
            if not admin.is_admin:
                print(f"\n❌ PROBLEMA IDENTIFICADO:")
                print(f"   O usuário admin tem tipo_usuario = '{admin.tipo_usuario}'")
                print(f"   Deveria ser tipo_usuario = 'admin'")
                print(f"   Por isso admin.is_admin = False")
                print(f"   E o menu não aparece no template")
            
            return admin.is_admin
            
        except Exception as e:
            print(f"❌ Erro no diagnóstico: {e}")
            import traceback
            traceback.print_exc()
            return False

def corrigir_admin():
    """Corrige o usuário admin"""
    app = create_app()
    
    with app.app_context():
        try:
            print(f"\n🔧 CORRIGINDO USUÁRIO ADMIN...")
            
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("❌ Usuário admin não encontrado!")
                return False
            
            # Mostrar estado atual
            print(f"   Estado atual: tipo_usuario = '{admin.tipo_usuario}'")
            
            # Corrigir
            admin.tipo_usuario = 'admin'
            admin.set_password('Admin123!')  # Reset da senha também
            db.session.commit()
            
            print(f"   ✅ Corrigido para: tipo_usuario = '{admin.tipo_usuario}'")
            print(f"   ✅ Senha resetada para: Admin123!")
            
            # Verificar correção
            admin = User.query.filter_by(username='admin').first()
            print(f"\n📊 VERIFICAÇÃO PÓS-CORREÇÃO:")
            print(f"   admin.tipo_usuario = '{admin.tipo_usuario}'")
            print(f"   admin.is_admin = {admin.is_admin}")
            
            if admin.is_admin:
                print(f"\n🎉 SUCESSO! Agora o menu de administração deve aparecer!")
                print(f"📝 Para testar:")
                print(f"   1. Reinicie o servidor: python iniciar.py")
                print(f"   2. Faça login com: admin / Admin123!")
                print(f"   3. O menu 'Administração' deve aparecer na navbar")
            else:
                print(f"\n❌ AINDA HÁ PROBLEMA! Verificar modelo User...")
            
            return admin.is_admin
            
        except Exception as e:
            print(f"❌ Erro na correção: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🚀 INICIANDO DIAGNÓSTICO...")
    
    # Diagnóstico
    admin_ok = diagnosticar_admin()
    
    if not admin_ok:
        # Correção
        print(f"\n🔧 INICIANDO CORREÇÃO...")
        sucesso = corrigir_admin()
        
        if sucesso:
            print(f"\n✅ PROBLEMA RESOLVIDO!")
            print(f"🚀 Execute: python iniciar.py")
            print(f"👤 Login: admin")
            print(f"🔑 Senha: Admin123!")
        else:
            print(f"\n❌ FALHA NA CORREÇÃO!")
    else:
        print(f"\n✅ Admin já está correto!")
        print(f"🤔 Se o menu não aparece, verificar:")
        print(f"   1. Cache do navegador")
        print(f"   2. Template base.html")
        print(f"   3. Rota admin.index existe")
    
    print("=" * 50)