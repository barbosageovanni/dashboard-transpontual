#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir usuário admin
Arquivo: verificar_admin.py
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_admin():
    """Verifica e corrige o usuário admin"""
    
    try:
        print("🔍 Verificando usuário administrador...")
        print("=" * 60)
        
        # Importar aplicação
        from app import create_app, db
        from app.models.user import User
        
        # Criar contexto da aplicação
        app = create_app()
        
        with app.app_context():
            # Buscar usuário admin
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("❌ Usuário admin não encontrado!")
                print("🔧 Criando usuário admin...")
                
                # Criar admin
                admin = User(
                    username='admin',
                    email='admin@transpontual.com',
                    nome_completo='Administrador do Sistema',
                    tipo_usuario='admin',
                    ativo=True
                )
                admin.set_password('Admin123!')
                
                db.session.add(admin)
                db.session.commit()
                
                print("✅ Usuário admin criado com sucesso!")
                
            else:
                print(f"✅ Usuário admin encontrado: {admin.username}")
                
                # Verificar propriedades
                problemas = []
                
                if admin.tipo_usuario != 'admin':
                    problemas.append(f"Tipo incorreto: {admin.tipo_usuario}")
                    admin.tipo_usuario = 'admin'
                
                if not admin.ativo:
                    problemas.append("Usuário inativo")
                    admin.ativo = True
                
                if admin.email != 'admin@transpontual.com':
                    problemas.append(f"Email incorreto: {admin.email}")
                    admin.email = 'admin@transpontual.com'
                
                if not admin.nome_completo:
                    problemas.append("Nome completo vazio")
                    admin.nome_completo = 'Administrador do Sistema'
                
                # Resetar senha se necessário
                if not admin.check_password('Admin123!'):
                    problemas.append("Senha incorreta")
                    admin.set_password('Admin123!')
                
                if problemas:
                    print(f"🔧 Corrigindo {len(problemas)} problemas:")
                    for problema in problemas:
                        print(f"   - {problema}")
                    
                    db.session.commit()
                    print("✅ Correções aplicadas!")
                else:
                    print("✅ Usuário admin está correto!")
            
            # Informações finais
            print("\n" + "=" * 60)
            print("📊 INFORMAÇÕES DO ADMIN:")
            print("=" * 60)
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Nome: {admin.nome_completo}")
            print(f"Tipo: {admin.tipo_usuario}")
            print(f"Ativo: {admin.ativo}")
            print(f"Senha: Admin123!")
            print(f"É Admin: {admin.is_admin}")
            
            # Verificar total de usuários
            total_users = User.query.count()
            admins = User.query.filter_by(tipo_usuario='admin').count()
            ativos = User.query.filter_by(ativo=True).count()
            
            print(f"\n📈 ESTATÍSTICAS:")
            print(f"Total de usuários: {total_users}")
            print(f"Administradores: {admins}")
            print(f"Usuários ativos: {ativos}")
            
            print("\n" + "=" * 60)
            print("🎉 VERIFICAÇÃO CONCLUÍDA!")
            print("💡 Agora você pode fazer login com:")
            print("   Usuário: admin")
            print("   Senha: Admin123!")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        print("💡 Certifique-se de que o banco de dados está acessível")
        return False

if __name__ == "__main__":
    verificar_admin()