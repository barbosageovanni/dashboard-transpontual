# ARQUIVO: verificar_rotas.py - SCRIPT PARA VERIFICAR ROTAS REGISTRADAS
# Execute este script para verificar se todas as rotas estão sendo registradas

from flask import Flask
from app import create_app
import sys

def verificar_rotas():
    """Verifica se todas as rotas estão registradas corretamente"""
    
    print("🔍 Verificando rotas registradas no sistema...")
    print("="*60)
    
    try:
        app = create_app()
        
        with app.app_context():
            # Obter todas as rotas registradas
            rotas_registradas = []
            
            for rule in app.url_map.iter_rules():
                rotas_registradas.append({
                    'endpoint': rule.endpoint,
                    'rule': rule.rule,
                    'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'})
                })
            
            # Organizar por blueprint
            blueprints = {}
            for rota in rotas_registradas:
                if '.' in rota['endpoint']:
                    blueprint = rota['endpoint'].split('.')[0]
                else:
                    blueprint = 'main'
                
                if blueprint not in blueprints:
                    blueprints[blueprint] = []
                
                blueprints[blueprint].append(rota)
            
            # Verificar blueprints essenciais
            blueprints_essenciais = [
                'auth', 'dashboard', 'ctes', 'baixas', 
                'analise_financeira', 'admin'
            ]
            
            blueprints_faltando = []
            for bp in blueprints_essenciais:
                if bp not in blueprints:
                    blueprints_faltando.append(bp)
            
            # Mostrar resultados
            print(f"📊 Total de rotas registradas: {len(rotas_registradas)}")
            print(f"📦 Blueprints encontrados: {len(blueprints)}")
            print()
            
            # Listar blueprints
            for blueprint, rotas in sorted(blueprints.items()):
                status = "✅" if blueprint in blueprints_essenciais else "ℹ️"
                print(f"{status} Blueprint '{blueprint}' - {len(rotas)} rotas:")
                
                for rota in sorted(rotas, key=lambda x: x['rule']):
                    methods = ', '.join(rota['methods'])
                    print(f"   {rota['rule']} [{methods}] -> {rota['endpoint']}")
                print()
            
            # Verificar rotas específicas importantes
            rotas_importantes = [
                'baixas.index',
                'baixas.conciliacao', 
                'admin.index',
                'admin.users',
                'analise_financeira.index'
            ]
            
            print("🎯 Verificando rotas importantes:")
            print("-" * 40)
            
            for rota_importante in rotas_importantes:
                encontrada = any(r['endpoint'] == rota_importante for r in rotas_registradas)
                status = "✅" if encontrada else "❌"
                print(f"{status} {rota_importante}")
            
            print()
            
            # Mostrar erros se houver
            if blueprints_faltando:
                print("❌ PROBLEMAS ENCONTRADOS:")
                print(f"   Blueprints não registrados: {', '.join(blueprints_faltando)}")
                return False
            else:
                print("✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
                print("   Todos os blueprints essenciais estão registrados.")
                return True
                
    except Exception as e:
        print(f"❌ ERRO na verificação: {str(e)}")
        return False

if __name__ == "__main__":
    verificar_rotas()


# ARQUIVO: debug_blueprints.py - SCRIPT PARA DEBUG DE BLUEPRINTS
# Execute este script se as rotas não estiverem aparecendo

def debug_blueprints():
    """Debug detalhado dos blueprints"""
    
    print("🔧 Debug de Blueprints...")
    print("="*50)
    
    try:
        # Testar importação individual de cada blueprint
        blueprints_para_testar = [
            ('auth', 'app.routes.auth'),
            ('dashboard', 'app.routes.dashboard'),
            ('ctes', 'app.routes.ctes'),
            ('baixas', 'app.routes.baixas'),
            ('analise_financeira', 'app.routes.analise_financeira'),
            ('admin', 'app.routes.admin')
        ]
        
        for nome, modulo in blueprints_para_testar:
            try:
                print(f"📦 Testando {nome}...")
                exec(f"from {modulo} import bp")
                print(f"   ✅ Blueprint '{nome}' importado com sucesso")
            except ImportError as e:
                print(f"   ❌ Erro ao importar '{nome}': {e}")
            except Exception as e:
                print(f"   ⚠️ Outro erro em '{nome}': {e}")
        
        print()
        print("🏗️ Testando criação da aplicação...")
        
        from app import create_app
        app = create_app()
        
        print("   ✅ Aplicação criada com sucesso")
        print(f"   📊 Blueprints registrados: {list(app.blueprints.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Executar ambos os scripts
    print("1️⃣ FASE 1: Debug de Blueprints")
    debug_ok = debug_blueprints()
    
    print("\n" + "="*60 + "\n")
    
    print("2️⃣ FASE 2: Verificação de Rotas")
    if debug_ok:
        verificar_rotas()
    else:
        print("❌ Pulando verificação de rotas devido a erros na importação de blueprints")


# COMANDO PARA EXECUTAR:
# python verificar_rotas.py