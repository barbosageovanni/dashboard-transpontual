#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para localizar arquivos de template no projeto
"""

import os
import glob

def encontrar_templates():
    """Localiza todos os arquivos de template no projeto"""
    
    print("🔍 LOCALIZANDO ARQUIVOS DE TEMPLATE")
    print("=" * 50)
    
    # Procurar por arquivos .html em todo o projeto
    patterns = [
        "**/*.html",
        "**/templates/**/*.html", 
        "**/app/templates/**/*.html",
        "templates/**/*.html",
        "app/templates/**/*.html"
    ]
    
    arquivos_encontrados = set()
    
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            arquivos_encontrados.add(os.path.normpath(match))
    
    if not arquivos_encontrados:
        print("❌ Nenhum arquivo HTML encontrado!")
        return None
    
    print("📄 ARQUIVOS HTML ENCONTRADOS:")
    arquivos_ordenados = sorted(list(arquivos_encontrados))
    
    base_files = []
    auth_files = []
    outros_files = []
    
    for arquivo in arquivos_ordenados:
        print(f"  📁 {arquivo}")
        
        if 'base.html' in arquivo.lower():
            base_files.append(arquivo)
        elif 'auth' in arquivo.lower() or 'login' in arquivo.lower():
            auth_files.append(arquivo)
        else:
            outros_files.append(arquivo)
    
    print(f"\n📊 TOTAL: {len(arquivos_encontrados)} arquivos encontrados")
    
    # Destacar arquivos importantes
    if base_files:
        print(f"\n🎯 ARQUIVOS BASE ENCONTRADOS:")
        for arquivo in base_files:
            print(f"  ⭐ {arquivo}")
    
    if auth_files:
        print(f"\n🔐 ARQUIVOS DE AUTENTICAÇÃO:")
        for arquivo in auth_files:
            print(f"  🔑 {arquivo}")
    
    # Verificar estrutura de pastas
    print(f"\n📁 ESTRUTURA DE PASTAS:")
    pastas = set()
    for arquivo in arquivos_encontrados:
        pasta = os.path.dirname(arquivo)
        if pasta:
            pastas.add(pasta)
    
    for pasta in sorted(pastas):
        print(f"  📂 {pasta}/")
    
    return base_files[0] if base_files else arquivos_ordenados[0] if arquivos_ordenados else None

def verificar_conteudo_base(arquivo_base):
    """Verifica o conteúdo do arquivo base encontrado"""
    
    if not arquivo_base or not os.path.exists(arquivo_base):
        print("❌ Arquivo base não encontrado para verificação")
        return False
    
    print(f"\n📄 VERIFICANDO CONTEÚDO: {arquivo_base}")
    print("-" * 50)
    
    try:
        with open(arquivo_base, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificações básicas
        checks = [
            ("Tag DOCTYPE", "<!DOCTYPE html>"),
            ("Bootstrap CSS", "bootstrap"),
            ("Font Awesome", "font-awesome"),
            ("Navbar", "navbar"),
            ("Current user", "current_user"),
            ("Dropdown", "dropdown"),
            ("Link Sair", "Sair"),
            ("Dashboard Baker", "Dashboard")
        ]
        
        print("VERIFICAÇÕES:")
        for desc, pattern in checks:
            if pattern.lower() in content.lower():
                print(f"  ✅ {desc}")
            else:
                print(f"  ❌ {desc}")
        
        # Mostrar trecho do dropdown se existir
        if 'dropdown' in content.lower():
            print(f"\n📄 TRECHO DO DROPDOWN:")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'dropdown-menu' in line.lower():
                    start = max(0, i-2)
                    end = min(len(lines), i+10)
                    for j in range(start, end):
                        print(f"  {j+1:3d}: {lines[j]}")
                    break
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False

if __name__ == "__main__":
    arquivo_base = encontrar_templates()
    
    if arquivo_base:
        verificar_conteudo_base(arquivo_base)
        print(f"\n🎯 ARQUIVO PRINCIPAL IDENTIFICADO: {arquivo_base}")
        print(f"💡 Use este caminho para fazer as modificações")
    else:
        print("\n❌ Nenhum arquivo de template encontrado!")
        print("💡 Verifique se está na pasta correta do projeto")