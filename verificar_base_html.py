#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se o arquivo base.html foi modificado corretamente
"""

import os

def verificar_base_html():
    """Verifica o conteúdo do arquivo base.html"""
    
    print("🔍 VERIFICANDO ARQUIVO base.html")
    print("=" * 40)
    
    arquivo = "templates/base.html"
    
    if not os.path.exists(arquivo):
        print("❌ Arquivo templates/base.html não encontrado!")
        return False
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificações
    checks = [
        ("Link 'Minha Conta'", "auth.profile"),
        ("Ícone user-circle", "fas fa-user-circle"),
        ("Texto 'Minha Conta'", "Minha Conta"),
        ("Separador dropdown", "dropdown-divider"),
        ("Condicional admin", "current_user.tipo_usuario == 'admin'"),
        ("Link Administração", "Administração"),
        ("Role button correto", 'role="button"'),
        ("Dropdown menu end", "dropdown-menu-end")
    ]
    
    encontrados = 0
    total = len(checks)
    
    print("VERIFICAÇÕES:")
    for desc, pattern in checks:
        if pattern in content:
            print(f"  ✅ {desc}")
            encontrados += 1
        else:
            print(f"  ❌ {desc}")
    
    print(f"\n📊 RESULTADO: {encontrados}/{total} verificações passaram")
    
    # Mostrar trecho do dropdown atual
    print("\n📄 TRECHO DO DROPDOWN ATUAL:")
    print("-" * 50)
    
    lines = content.split('\n')
    in_dropdown = False
    dropdown_lines = []
    
    for i, line in enumerate(lines):
        if 'dropdown-menu' in line:
            in_dropdown = True
        
        if in_dropdown:
            dropdown_lines.append(f"{i+1:3d}: {line}")
            if '</ul>' in line and 'dropdown' in ''.join(lines[max(0, i-5):i]):
                break
        
        if len(dropdown_lines) > 15:  # Limite de segurança
            break
    
    for line in dropdown_lines[-10:]:  # Mostrar últimas 10 linhas
        print(line)
    
    return encontrados >= (total * 0.7)  # 70% das verificações

if __name__ == "__main__":
    verificar_base_html()