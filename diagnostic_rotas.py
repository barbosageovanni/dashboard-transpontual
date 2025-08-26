#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO DE ROTAS FLASK - ERRO 404
Execute este script para identificar problemas de roteamento
"""

import os
import sys
from flask import Flask

def diagnostico_rotas():
    """Diagnóstico completo das rotas Flask"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE ROTAS FLASK - ERRO 404")
    print("=" * 60)
    
    # 1. Verificar se o servidor está rodando
    print("\n1️⃣ VERIFICANDO SERVIDOR FLASK...")
    verificar_servidor()
    
    # 2. Verificar estrutura de arquivos
    print("\n2️⃣ VERIFICANDO ESTRUTURA DE ARQUIVOS...")
    verificar_estrutura()
    
    # 3. Testar importação da aplicação
    print("\n3️⃣ TESTANDO IMPORTAÇÃO DA APLICAÇÃO...")
    testar_importacao()
    
    # 4. Verificar blueprints registrados
    print("\n4️⃣ VERIFICANDO BLUEPRINTS REGISTRADOS...")
    verificar_blueprints()
    
    # 5. Listar todas as rotas
    print("\n5️⃣ LISTANDO TODAS AS ROTAS DISPONÍVEIS...")
    listar_rotas()
    
    # 6. Testar rotas específicas
    print("\n6️⃣ TESTANDO ROTAS ESPECÍFICAS...")
    testar_rotas()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)

def verificar_servidor():
    """Verifica se o servidor Flask está configurado corretamente"""
    try:
        # Verificar se arquivo principal existe
        arquivos_principais = ['app.py', 'run.py', 'iniciar.py', 'main.py']
        arquivo_encontrado = None
        
        for arquivo in arquivos_principais:
            if os.path.exists(arquivo):
                arquivo_encontrado = arquivo
                print(f"✅ Arquivo principal encontrado: {arquivo}")
                break
        
        if not arquivo_encontrado:
            print("❌ ERRO: Nenhum arquivo principal encontrado")
            print("   Arquivos procurados:", ', '.join(arquivos_principais))
            return False
        
        # Verificar variáveis de ambiente
        flask_app = os.getenv('FLASK_APP')
        flask_env = os.getenv('FLASK_ENV', 'production')
        
        print(f"   FLASK_APP: {flask_app or 'Não definida'}")
        print(f"   FLASK_ENV: {flask_env}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao verificar servidor: {e}")
        return False

def verificar_estrutura():
    """Verifica estrutura de pastas e arquivos"""
    try:
        estrutura_esperada = {
            'app': ['__init__.py', 'routes', 'models', 'templates'],
            'app/routes': ['dashboard.py', 'auth.py', 'ctes.py'],
            'app/models': ['cte.py', 'user.py'],
            'app/templates': ['dashboard'],
            'static': ['js', 'css']
        }
        
        print("Verificando estrutura de pastas:")
        for pasta, arquivos in estrutura_esperada.items():
            if os.path.exists(pasta):
                print(f"✅ {pasta}/ existe")
                for arquivo in arquivos:
                    caminho = os.path.join(pasta, arquivo)
                    if os.path.exists(caminho):
                        print(f"  ✅ {arquivo}")
                    else:
                        print(f"  ❌ {arquivo} - FALTANDO")
            else:
                print(f"❌ {pasta}/ - PASTA FALTANDO")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao verificar estrutura: {e}")
        return False

def testar_importacao():
    """Testa se a aplicação Flask pode ser importada"""
    try:
        # Tentar importar a aplicação
        sys.path.insert(0, '.')
        
        try:
            from app import create_app
            print("✅ Importação de create_app: OK")
        except ImportError as e:
            print(f"❌ ERRO ao importar create_app: {e}")
            return False
        
        try:
            app = create_app()
            print("✅ Criação da aplicação: OK")
            print(f"   Nome da app: {app.name}")
            print(f"   Debug mode: {app.debug}")
            return app
        except Exception as e:
            print(f"❌ ERRO ao criar aplicação: {e}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO na importação: {e}")
        return False

def verificar_blueprints():
    """Verifica se os blueprints estão registrados"""
    try:
        app = testar_importacao()
        if not app:
            print("❌ Não foi possível criar aplicação para verificar blueprints")
            return False
        
        print("Blueprints registrados:")
        for blueprint_name, blueprint in app.blueprints.items():
            print(f"✅ {blueprint_name}: {blueprint.url_prefix}")
        
        # Verificar blueprints esperados
        blueprints_esperados = ['dashboard', 'auth', 'ctes']
        for bp in blueprints_esperados:
            if bp in app.blueprints:
                print(f"✅ Blueprint '{bp}' registrado")
            else:
                print(f"❌ Blueprint '{bp}' NÃO registrado")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao verificar blueprints: {e}")
        return False

def listar_rotas():
    """Lista todas as rotas disponíveis"""
    try:
        app = testar_importacao()
        if not app:
            print("❌ Não foi possível criar aplicação para listar rotas")
            return False
        
        with app.app_context():
            print("Rotas disponíveis:")
            for rule in app.url_map.iter_rules():
                methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"  {rule.rule:<30} [{methods}] -> {rule.endpoint}")
        
        # Verificar rotas específicas do dashboard
        rotas_dashboard = [
            '/dashboard/',
            '/dashboard/api/metricas',
            '/dashboard/api/debug',
            '/dashboard/api/test-fix'
        ]
        
        print("\nVerificando rotas do dashboard:")
        with app.test_client() as client:
            for rota in rotas_dashboard:
                try:
                    response = client.get(rota)
                    if response.status_code == 404:
                        print(f"❌ {rota} - NÃO ENCONTRADA (404)")
                    elif response.status_code in [200, 302, 401]:
                        print(f"✅ {rota} - EXISTE (status: {response.status_code})")
                    else:
                        print(f"⚠️ {rota} - STATUS: {response.status_code}")
                except Exception as e:
                    print(f"❌ {rota} - ERRO: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao listar rotas: {e}")
        return False

def testar_rotas():
    """Testa rotas específicas"""
    try:
        app = testar_importacao()
        if not app:
            return False
        
        rotas_teste = {
            '/': 'Página inicial',
            '/dashboard/': 'Dashboard principal',
            '/dashboard/api/debug': 'API de debug',
            '/auth/login': 'Página de login',
            '/ctes/': 'Página de CTEs'
        }
        
        print("Testando rotas específicas:")
        with app.test_client() as client:
            for rota, descricao in rotas_teste.items():
                try:
                    response = client.get(rota)
                    status = response.status_code
                    
                    if status == 200:
                        print(f"✅ {rota:<25} - {descricao} - OK")
                    elif status == 302:
                        print(f"🔄 {rota:<25} - {descricao} - REDIRECT")
                    elif status == 401:
                        print(f"🔐 {rota:<25} - {descricao} - LOGIN NECESSÁRIO")
                    elif status == 404:
                        print(f"❌ {rota:<25} - {descricao} - NÃO ENCONTRADA")
                    else:
                        print(f"⚠️ {rota:<25} - {descricao} - STATUS: {status}")
                        
                except Exception as e:
                    print(f"❌ {rota:<25} - ERRO: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao testar rotas: {e}")
        return False

def gerar_solucoes():
    """Gera soluções baseadas nos problemas encontrados"""
    print("\n" + "=" * 60)
    print("🔧 SOLUÇÕES RECOMENDADAS")
    print("=" * 60)
    
    print("\n1. VERIFICAR SE O SERVIDOR ESTÁ RODANDO:")
    print("   flask run")
    print("   # ou")
    print("   python iniciar.py")
    
    print("\n2. VERIFICAR VARIÁVEL FLASK_APP:")
    print("   export FLASK_APP=iniciar.py  # Linux/Mac")
    print("   set FLASK_APP=iniciar.py     # Windows")
    
    print("\n3. VERIFICAR SE AS ROTAS ESTÃO REGISTRADAS:")
    print("   # No arquivo __init__.py, verificar se os blueprints estão sendo importados")
    
    print("\n4. ROTAS CORRETAS PARA ACESSAR:")
    print("   http://localhost:5000/")
    print("   http://localhost:5000/dashboard/")
    print("   http://localhost:5000/auth/login")
    
    print("\n5. MODO DEBUG PARA VER ERROS DETALHADOS:")
    print("   export FLASK_ENV=development")
    print("   export FLASK_DEBUG=1")

if __name__ == "__main__":
    try:
        diagnostico_rotas()
        gerar_solucoes()
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()