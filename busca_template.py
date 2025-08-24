#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Busca Específica - Identificar Template Atual
busca_template.py

EXECUTE ESTE SCRIPT PARA ENCONTRAR EXATAMENTE QUAL TEMPLATE ESTÁ SENDO USADO
"""

import os
import glob
import re
from datetime import datetime

def print_separator(char="=", length=70):
    print(char * length)

def print_header(title):
    print_separator()
    print(f"🔍 {title}")
    print_separator()

def search_files_content(pattern, search_terms, directory="."):
    """Busca termos específicos em arquivos"""
    results = {}
    
    for root, dirs, files in os.walk(directory):
        # Pular diretórios desnecessários
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.env']):
            continue
            
        for file in files:
            if file.endswith(pattern):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Verificar cada termo de busca
                        for term in search_terms:
                            if term.lower() in content.lower():
                                if filepath not in results:
                                    results[filepath] = []
                                results[filepath].append(term)
                                
                except Exception as e:
                    continue
    
    return results

def analyze_template_content(filepath):
    """Analisa conteúdo detalhado do template"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📄 ANÁLISE DETALHADA: {filepath}")
        print(f"📏 Tamanho: {len(content)} caracteres")
        print(f"📅 Modificado: {datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Verificar indicadores de versão nova
        indicators_new = [
            'projecoes-tab',
            'comparativo-tab', 
            'veiculos-tab',
            'insights-tab',
            'analise_financeira_avancada.js',
            'filtros-avancados',
            'nav-tabs-enhanced',
            'Score de Saúde'
        ]
        
        # Verificar indicadores de versão antiga
        indicators_old = [
            'Dashboard Financeiro Baker',
            'chart-line',
            'Sistema Avançado de Gestão'
        ]
        
        new_count = 0
        old_count = 0
        
        print(f"\n🔍 INDICADORES DE VERSÃO NOVA:")
        for indicator in indicators_new:
            if indicator in content:
                print(f"   ✅ {indicator}")
                new_count += 1
            else:
                print(f"   ❌ {indicator}")
        
        print(f"\n🔍 INDICADORES DE VERSÃO ANTIGA:")
        for indicator in indicators_old:
            if indicator in content:
                print(f"   ✅ {indicator}")
                old_count += 1
        
        # Buscar estrutura de abas
        print(f"\n📑 ESTRUTURA DE ABAS:")
        tab_patterns = [
            r'id="([^"]*-tab)"',
            r'data-bs-target="#([^"]*)"',
            r'<div class="tab-pane[^>]*id="([^"]*)"'
        ]
        
        tabs_found = set()
        for pattern in tab_patterns:
            matches = re.findall(pattern, content)
            tabs_found.update(matches)
        
        if tabs_found:
            print(f"   Abas encontradas: {', '.join(sorted(tabs_found))}")
        else:
            print("   ❌ Nenhuma aba encontrada")
        
        # Verificar imports de JS
        print(f"\n📜 IMPORTS JAVASCRIPT:")
        js_patterns = [
            r'src="[^"]*\.js"',
            r'static.*\.js'
        ]
        
        js_files = set()
        for pattern in js_patterns:
            matches = re.findall(pattern, content)
            js_files.update(matches)
        
        if js_files:
            for js_file in js_files:
                print(f"   - {js_file}")
        else:
            print("   ❌ Nenhum arquivo JS encontrado")
        
        # Determinar versão
        if new_count >= 5:
            version = "✅ VERSÃO NOVA (Avançada)"
        elif new_count >= 2:
            version = "⚠️ VERSÃO PARCIAL (Alguns recursos novos)"
        else:
            version = "❌ VERSÃO ANTIGA (Básica)"
        
        print(f"\n🎯 CONCLUSÃO: {version}")
        print(f"   Indicadores novos: {new_count}/{len(indicators_new)}")
        
        return version, new_count, len(indicators_new)
        
    except Exception as e:
        print(f"❌ Erro ao analisar template: {str(e)}")
        return "ERRO", 0, 0

def find_route_registrations():
    """Encontra onde as rotas são registradas"""
    print_header("BUSCA DE REGISTROS DE ROTAS")
    
    route_terms = [
        'register_blueprint',
        'analise_financeira',
        'Blueprint',
        'url_prefix'
    ]
    
    results = search_files_content('.py', route_terms)
    
    for filepath, terms in results.items():
        print(f"\n📄 {filepath}")
        print(f"   Termos encontrados: {', '.join(terms)}")
        
        # Ler linha específica com register_blueprint
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if 'register_blueprint' in line.lower() and 'analise' in line.lower():
                        print(f"   Linha {i+1}: {line.strip()}")
        except:
            pass

def check_import_errors():
    """Verifica possíveis erros de import"""
    print_header("VERIFICAÇÃO DE IMPORTS")
    
    service_files = [
        'app/services/analise_financeira_service.py',
        'app/services/projecoes_service.py', 
        'app/services/analise_veiculo_service.py'
    ]
    
    for service_file in service_files:
        if os.path.exists(service_file):
            print(f"✅ {service_file} existe")
            
            # Verificar imports dentro do arquivo
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Buscar imports problemáticos
                problematic_imports = [
                    'from scipy',
                    'import scipy',
                    'from dateutil',
                    'import pandas'
                ]
                
                for imp in problematic_imports:
                    if imp in content:
                        print(f"   ⚠️ Import encontrado: {imp}")
                        
            except Exception as e:
                print(f"   ❌ Erro ao ler arquivo: {str(e)}")
        else:
            print(f"❌ {service_file} NÃO EXISTE")

def main():
    print_header("BUSCA ESPECÍFICA - TEMPLATE DE ANÁLISE FINANCEIRA")
    
    # 1. Buscar todos os templates relacionados
    print("\n🔍 1. BUSCANDO TEMPLATES DE ANÁLISE FINANCEIRA...")
    
    template_patterns = [
        'app/templates/analise_financeira/*.html',
        'app/templates/**/analise*.html',
        'templates/**/analise*.html'
    ]
    
    templates_found = []
    for pattern in template_patterns:
        templates_found.extend(glob.glob(pattern, recursive=True))
    
    # Remover duplicatas
    templates_found = list(set(templates_found))
    
    if templates_found:
        print(f"📄 Templates encontrados ({len(templates_found)}):")
        for template in templates_found:
            print(f"   - {template}")
    else:
        print("❌ Nenhum template de análise financeira encontrado!")
    
    # 2. Analisar cada template encontrado
    print(f"\n🔍 2. ANÁLISE DETALHADA DOS TEMPLATES...")
    
    for template in templates_found:
        analyze_template_content(template)
    
    # 3. Buscar referências em rotas
    print(f"\n🔍 3. BUSCANDO ROTAS QUE USAM ESTES TEMPLATES...")
    
    route_terms = [
        'analise_financeira/index.html',
        'render_template',
        'analise-financeira'
    ]
    
    route_results = search_files_content('.py', route_terms)
    
    if route_results:
        print("📄 Arquivos de rota que referenciam análise financeira:")
        for filepath, terms in route_results.items():
            print(f"   - {filepath}: {', '.join(terms)}")
    else:
        print("❌ Nenhuma referência encontrada em rotas")
    
    # 4. Verificar registros de blueprint
    find_route_registrations()
    
    # 5. Verificar possíveis erros de import
    check_import_errors()
    
    # 6. Verificar JavaScript
    print_header("BUSCA DE ARQUIVOS JAVASCRIPT")
    
    js_files = glob.glob('app/static/js/*.js')
    if js_files:
        print("📜 Arquivos JavaScript encontrados:")
        for js_file in js_files:
            size = os.path.getsize(js_file)
            print(f"   - {js_file} ({size} bytes)")
            
            # Verificar se contém funções específicas
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                advanced_functions = [
                    'carregarProjecoesFuturas',
                    'carregarComparativoTemporal',
                    'carregarAnaliseVeiculos',
                    'filtrosAtivos'
                ]
                
                found_functions = [func for func in advanced_functions if func in content]
                if found_functions:
                    print(f"      ✅ Funções avançadas: {', '.join(found_functions)}")
                else:
                    print(f"      ❌ Sem funções avançadas")
                    
            except:
                pass
    else:
        print("❌ Nenhum arquivo JavaScript encontrado")
    
    # 7. DIAGNÓSTICO FINAL
    print_header("DIAGNÓSTICO FINAL")
    
    print("🎯 PROBLEMAS MAIS PROVÁVEIS:")
    
    if not templates_found:
        print("❌ 1. Template de análise financeira não existe")
        print("   Solução: Criar app/templates/analise_financeira/index.html")
    
    elif len(templates_found) == 1:
        template_path = templates_found[0]
        version, new_count, total_new = analyze_template_content(template_path)
        
        if new_count < total_new // 2:
            print("❌ 2. Template existe mas é a VERSÃO ANTIGA")
            print(f"   Arquivo: {template_path}")
            print("   Solução: Substituir conteúdo pela versão avançada (Artifact 5)")
    
    if not route_results:
        print("❌ 3. Rotas de análise financeira não registradas")
        print("   Solução: Verificar app/routes/analise_financeira.py e registro no __init__.py")
    
    if not os.path.exists('app/services/projecoes_service.py'):
        print("❌ 4. Serviços novos não criados")
        print("   Solução: Criar arquivos conforme Artifacts 1, 2 e 3")
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print("1. Execute: pip install scipy python-dateutil")
    print("2. Crie/substitua os arquivos conforme as Artifacts")
    print("3. Reinicie o servidor Flask")
    print("4. Limpe cache do navegador (Ctrl+F5)")
    
    print_separator()

if __name__ == "__main__":
    main()