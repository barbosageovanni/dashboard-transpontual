#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica se o modelo User está implementado corretamente
Execute: python verificar_modelo_user.py
"""

import inspect
from app import create_app
from app.models.user import User

def verificar_modelo_user():
    """Verifica a implementação do modelo User"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 VERIFICAÇÃO DO MODELO USER")
            print("=" * 40)
            
            # Verificar se a classe User existe
            print(f"✅ Classe User importada: {User}")
            
            # Verificar propriedades da classe
            print(f"\n📋 PROPRIEDADES DA CLASSE USER:")
            
            # Listar todos os atributos
            atributos = dir(User)
            propriedades = [attr for attr in atributos if not attr.startswith('_')]
            
            for prop in propriedades:
                print(f"   - {prop}")
            
            # Verificar se is_admin existe
            if hasattr(User, 'is_admin'):
                print(f"\n✅ Propriedade 'is_admin' encontrada!")
                
                # Verificar se é uma property
                is_property = isinstance(getattr(User, 'is_admin'), property)
                print(f"   É uma @property? {is_property}")
                
                if is_property:
                    # Tentar obter o código fonte
                    try:
                        source = inspect.getsource(User.is_admin.fget)
                        print(f"\n📝 CÓDIGO DA PROPRIEDADE is_admin:")
                        print(source)
                    except:
                        print(f"   (Não foi possível obter o código fonte)")
                
            else:
                print(f"\n❌ Propriedade 'is_admin' NÃO encontrada!")
                print(f"   Isso explica por que o menu não aparece")
            
            # Testar com um usuário real
            print(f"\n🧪 TESTE COM USUÁRIO ADMIN:")
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                print(f"   admin.username = '{admin.username}'")
                print(f"   admin.tipo_usuario = '{admin.tipo_usuario}'")
                
                if hasattr(admin, 'is_admin'):
                    print(f"   admin.is_admin = {admin.is_admin}")
                else:
                    print(f"   ❌ admin.is_admin não funciona!")
                
                # Teste manual da lógica
                manual_is_admin = admin.tipo_usuario == 'admin'
                print(f"   Teste manual: tipo_usuario == 'admin' = {manual_is_admin}")
            else:
                print(f"   ❌ Usuário admin não encontrado!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            import traceback
            traceback.print_exc()
            return False

def verificar_rota_admin():
    """Verifica se a rota admin existe"""
    app = create_app()
    
    print(f"\n🔗 VERIFICAÇÃO DAS ROTAS ADMIN:")
    
    # Listar todas as rotas
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            if 'admin' in rule.rule:
                routes.append(f"   {rule.rule} -> {rule.endpoint}")
        
        if routes:
            print(f"✅ Rotas admin encontradas:")
            for route in routes:
                print(route)
        else:
            print(f"❌ Nenhuma rota admin encontrada!")
            print(f"   Isso explica por que url_for('admin.index') falha")
        
        # Verificar blueprints
        print(f"\n📋 BLUEPRINTS REGISTRADOS:")
        for name, blueprint in app.blueprints.items():
            print(f"   - {name}: {blueprint}")

if __name__ == '__main__':
    print("🚀 VERIFICANDO MODELO USER E ROTAS...")
    
    verificar_modelo_user()
    verificar_rota_admin()
    
    print("\n" + "=" * 40)
    print("💡 RESUMO:")
    print("   1. Execute este script para identificar problemas")
    print("   2. Execute diagnostico_admin.py para corrigir usuário")
    print("   3. Verifique se todas as rotas admin existem")
    print("=" * 40)