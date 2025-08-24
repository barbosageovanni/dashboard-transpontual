#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico Completo - Dashboard Baker Flask
diagnostico_sistema.py

EXECUTE ESTE SCRIPT NA RAIZ DO PROJETO PARA IDENTIFICAR PROBLEMAS
"""

import os
import sys
import glob
from pathlib import Path
import importlib.util

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80)

def print_subheader(title):
    """Imprime subcabeçalho formatado"""
    print(f"\n📋 {title}")
    print("-" * 60)

def check_file_exists(filepath, description=""):
    """Verifica se arquivo existe e mostra status"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {filepath} - {size} bytes {description}")
        return True
    else:
        print(f"❌ {filepath} - NÃO ENCONTRADO {description}")
        return False

def scan_directory_contents(directory, pattern="*", description=""):
    """Escaneia conteúdo de diretório"""
    if not os.path.exists(directory):
        print(f"❌ Diretório não existe: {directory}")
        return []
    
    files = glob.glob(os.path.join(directory, pattern))
    if files:
        print(f"📁 {directory} {description}:")
        for file in sorted(files):
            rel_path = os.path.relpath(file)
            size = os.path.getsize(file) if os.path.isfile(file) else "DIR"
            print(f"   - {os.path.basename(file)} ({size} bytes)")
    else:
        print(f"📁 {directory} - VAZIO")
    return files

def search_text_in_files(directory, pattern, search_text, description=""):
    """Busca texto específico em arquivos"""
    if not os.path.exists(directory):
        return []
    
    files = glob.glob(os.path.join(directory, pattern), recursive=True)
    found_files = []
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if search_text.lower() in content.lower():
                    found_files.append(file)
                    print(f"🔍 ENCONTRADO '{search_text}' em: {os.path.relpath(file)}")
        except Exception as e:
            continue
    
    if not found_files:
        print(f"❌ Texto '{search_text}' não encontrado em {description}")
    
    return found_files

def diagnose_flask_routes():
    """Diagnostica rotas Flask registradas"""
    try:
        # Tentar importar a aplicação
        sys.path.insert(0, os.getcwd())
        
        # Tentar diferentes formas de importar
        possible_imports = [
            'app',
            'iniciar',
            'run'
        ]
        
        app = None
        for module_name in possible_imports:
            try:
                if module_name == 'app':
                    from app import create_app
                    app = create_app()
                    break
                elif module_name == 'iniciar':
                    import iniciar
                    if hasattr(iniciar, 'app'):
                        app = iniciar.app
                        break
                elif module_name == 'run':
                    import run
                    if hasattr(run, 'app'):
                        app = run.app
                        break
            except Exception as e:
                continue
        
        if app:
            print("✅ Aplicação Flask carregada com sucesso")
            
            # Listar todas as rotas
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(str(rule))
            
            print(f"📊 Total de rotas registradas: {len(routes)}")
            
            # Buscar rotas específicas de análise financeira
            analise_routes = [r for r in routes if 'analise' in r.lower()]
            if analise_routes:
                print(f"💰 Rotas de análise financeira encontradas ({len(analise_routes)}):")
                for route in analise_routes:
                    print(f"   - {route}")
            else:
                print("❌ Nenhuma rota de análise financeira encontrada")
            
            # Verificar blueprints registrados
            blueprints = list(app.blueprints.keys())
            print(f"📦 Blueprints registrados ({len(blueprints)}): {', '.join(blueprints)}")
            
            return True
        else:
            print("❌ Não foi possível carregar a aplicação Flask")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao diagnosticar rotas Flask: {str(e)}")
        return False

def main():
    """Função principal de diagnóstico"""
    print_header("DIAGNÓSTICO COMPLETO DO SISTEMA DASHBOARD BAKER")
    
    # 1. VERIFICAR ESTRUTURA BÁSICA DO PROJETO
    print_subheader("1. ESTRUTURA BÁSICA DO PROJETO")
    
    base_files = [
        ('iniciar.py', '(Arquivo principal de inicialização)'),
        ('app.py', '(Arquivo alternativo de inicialização)'),
        ('run.py', '(Arquivo alternativo de inicialização)'),
        ('config.py', '(Configurações)'),
        ('requirements.txt', '(Dependências)'),
        ('.env', '(Variáveis de ambiente)')
    ]
    
    for file, desc in base_files:
        check_file_exists(file, desc)
    
    # 2. VERIFICAR ESTRUTURA DA APLICAÇÃO
    print_subheader("2. ESTRUTURA DA APLICAÇÃO")
    
    app_dirs = [
        'app',
        'app/routes',
        'app/services', 
        'app/templates',
        'app/templates/analise_financeira',
        'app/static',
        'app/static/js',
        'app/models'
    ]
    
    for directory in app_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - NÃO ENCONTRADO")
    
    # 3. VERIFICAR ARQUIVOS DE ANÁLISE FINANCEIRA
    print_subheader("3. ARQUIVOS DE ANÁLISE FINANCEIRA")
    
    analise_files = [
        ('app/routes/analise_financeira.py', '(Routes de análise financeira)'),
        ('app/services/analise_financeira_service.py', '(Serviço principal)'),
        ('app/services/projecoes_service.py', '(Serviço de projeções - NOVO)'),
        ('app/services/analise_veiculo_service.py', '(Serviço de veículos - NOVO)'),
        ('app/templates/analise_financeira/index.html', '(Template principal)'),
        ('app/static/js/analise_financeira_avancada.js', '(JavaScript avançado - NOVO)')
    ]
    
    missing_files = []
    for file, desc in analise_files:
        if not check_file_exists(file, desc):
            missing_files.append(file)
    
    # 4. ESCANEAR TEMPLATES EXISTENTES
    print_subheader("4. TEMPLATES EXISTENTES")
    
    scan_directory_contents('app/templates', '*.html', '(Templates HTML)')
    scan_directory_contents('app/templates/analise_financeira', '*.html', '(Templates análise financeira)')
    
    # 5. ESCANEAR ARQUIVOS JAVASCRIPT
    print_subheader("5. ARQUIVOS JAVASCRIPT")
    
    scan_directory_contents('app/static/js', '*.js', '(Arquivos JavaScript)')
    
    # 6. BUSCAR REFERÊNCIAS A ANÁLISE FINANCEIRA
    print_subheader("6. BUSCAR REFERÊNCIAS A ANÁLISE FINANCEIRA")
    
    search_text_in_files('app/routes', '*.py', 'analise_financeira', 'routes')
    search_text_in_files('app/templates', '*.html', 'analise-financeira', 'templates')
    search_text_in_files('app', '__init__.py', 'analise_financeira', 'init files')
    
    # 7. VERIFICAR BLUEPRINTS REGISTRADOS
    print_subheader("7. VERIFICAR IMPORTS E BLUEPRINTS")
    
    # Buscar por imports de análise financeira
    search_text_in_files('app', '*.py', 'from.*analise_financeira', 'imports')
    search_text_in_files('app', '*.py', 'register_blueprint.*analise', 'blueprint registrations')
    
    # 8. DIAGNOSTICAR ROTAS FLASK
    print_subheader("8. DIAGNÓSTICO DE ROTAS FLASK")
    
    flask_ok = diagnose_flask_routes()
    
    # 9. VERIFICAR POSSÍVEIS PROBLEMAS
    print_subheader("9. POSSÍVEIS PROBLEMAS IDENTIFICADOS")
    
    problems = []
    
    if missing_files:
        problems.append(f"❌ Arquivos faltantes: {', '.join(missing_files)}")
    
    if not os.path.exists('app/templates/analise_financeira/index.html'):
        problems.append("❌ Template principal de análise financeira não encontrado")
    
    if not os.path.exists('app/routes/analise_financeira.py'):
        problems.append("❌ Routes de análise financeira não encontradas")
    
    if not flask_ok:
        problems.append("❌ Problemas para carregar aplicação Flask")
    
    # Verificar se está usando template antigo
    if os.path.exists('app/templates/analise_financeira/index.html'):
        try:
            with open('app/templates/analise_financeira/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'projecoes-tab' not in content:
                    problems.append("❌ Template de análise financeira é a versão ANTIGA (sem novas abas)")
                if 'analise_financeira_avancada.js' not in content:
                    problems.append("❌ Template não está carregando JavaScript avançado")
        except:
            problems.append("❌ Erro ao ler template de análise financeira")
    
    if problems:
        for problem in problems:
            print(problem)
    else:
        print("✅ Nenhum problema crítico identificado")
    
    # 10. RECOMENDAÇÕES
    print_subheader("10. RECOMENDAÇÕES DE CORREÇÃO")
    
    if missing_files:
        print("🔧 AÇÕES NECESSÁRIAS:")
        print("1. Criar os arquivos faltantes usando as Artifacts fornecidas")
        print("2. Verificar se os imports estão corretos no __init__.py")
        print("3. Reiniciar o servidor Flask após criar os arquivos")
        print("4. Limpar cache do navegador (Ctrl+F5)")
    
    # Verificar qual template está sendo servido
    if os.path.exists('app/templates/analise_financeira/index.html'):
        print(f"\n🔍 VERIFICAR TEMPLATE ATUAL:")
        print(f"   - Arquivo: app/templates/analise_financeira/index.html")
        print(f"   - Tamanho: {os.path.getsize('app/templates/analise_financeira/index.html')} bytes")
        print(f"   - Verificar se contém as 5 abas novas (projecoes-tab, comparativo-tab, etc.)")
    
    print_header("DIAGNÓSTICO CONCLUÍDO")
    print("📋 Revise as seções acima para identificar problemas")
    print("🔧 Implemente as correções sugeridas")
    print("🚀 Reinicie o servidor após as correções")

if __name__ == "__main__":
    main()