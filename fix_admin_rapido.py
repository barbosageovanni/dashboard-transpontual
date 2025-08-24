#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX RÁPIDO - Adicionar apenas os menus faltantes
Mantém a estrutura atual e adiciona só o que está faltando
"""

import os
import re

def fix_navegacao_rapida():
    print("🚛 FIX RÁPIDO - ADICIONANDO MENUS FALTANTES")
    print("=" * 50)
    
    arquivo = 'app/templates/base.html'
    
    if not os.path.exists(arquivo):
        print("❌ Arquivo base.html não encontrado!")
        return False
    
    try:
        # Ler arquivo atual
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        print("📖 Arquivo lido, adicionando menus faltantes...")
        
        # Verificar se já tem Análise Financeira
        if 'analise_financeira' not in conteudo:
            print("  ➕ Adicionando Análise Financeira...")
            
            # Encontrar onde inserir (após CTEs)
            padrao_ctes = r'(<li class="nav-item">\s*<a class="nav-link" href="{{ url_for\(\'ctes\.listar\'\) }}">[^<]*</a>\s*</li>)'
            
            menu_analise = '''
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('analise_financeira.index') }}">
                            <i class="fas fa-chart-line"></i> Análise Financeira
                        </a>
                    </li>'''
            
            conteudo = re.sub(padrao_ctes, r'\1' + menu_analise, conteudo)
        
        # Verificar se já tem Baixas
        if 'baixas.index' not in conteudo:
            print("  ➕ Adicionando Sistema de Baixas...")
            
            # Adicionar antes da Análise Financeira
            padrao_analise = r'(<li class="nav-item">\s*<a class="nav-link" href="{{ url_for\(\'analise_financeira\.index\'\) }}">[^<]*</a>\s*</li>)'
            
            menu_baixas = '''
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('baixas.index') }}">
                            <i class="fas fa-money-check-alt"></i> Baixas
                        </a>
                    </li>'''
            
            conteudo = re.sub(padrao_analise, menu_baixas + r'\1', conteudo)
        
        # Verificar se admin está no menu principal
        if 'admin.index' not in conteudo or 'dropdown' not in conteudo:
            print("  ➕ Melhorando menu de Administração...")
            
            # Adicionar admin como item normal se não existir
            if 'admin.index' not in conteudo:
                padrao_final = r'(</ul>\s*<ul class="navbar-nav">)'
                
                menu_admin = '''
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin.index') }}">
                            <i class="fas fa-cogs"></i> Administração
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">'''
                
                conteudo = re.sub(padrao_final, menu_admin, conteudo)
        
        # Salvar arquivo atualizado
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("\n✅ Menus adicionados com sucesso!")
        print("🔄 Reinicie o servidor: python iniciar.py")
        print("🌐 Pressione Ctrl+F5 no navegador")
        
        # Mostrar o que foi adicionado
        print("\n📋 MENUS ADICIONADOS:")
        if 'analise_financeira' in conteudo:
            print("  ✅ Análise Financeira")
        if 'baixas.index' in conteudo:
            print("  ✅ Sistema de Baixas")
        if 'admin.index' in conteudo:
            print("  ✅ Administração")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_menus():
    """Verifica quais menus estão presentes"""
    arquivo = 'app/templates/base.html'
    
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        print("\n🔍 MENUS ATUAIS:")
        
        menus = [
            ('dashboard.index', '📊 Dashboard'),
            ('ctes.listar', '🚛 CTEs'),
            ('baixas.index', '💰 Baixas'),
            ('analise_financeira.index', '📈 Análise Financeira'),
            ('admin.index', '🛠️ Administração')
        ]
        
        for url, nome in menus:
            if url in conteudo:
                print(f"  ✅ {nome}")
            else:
                print(f"  ❌ {nome} - FALTANDO")

if __name__ == "__main__":
    print("🎯 FIX RÁPIDO PARA NAVEGAÇÃO")
    print("Este script adiciona apenas os menus que estão faltando")
    print("sem alterar a estrutura atual do base.html")
    
    verificar_menus()
    
    resposta = input("\n❓ Adicionar menus faltantes? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        sucesso = fix_navegacao_rapida()
        if sucesso:
            print("\n🎉 MENUS ADICIONADOS!")
            verificar_menus()
    else:
        print("❌ Operação cancelada")