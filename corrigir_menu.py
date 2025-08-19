#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO ESPECÍFICA DO MENU - Análise Financeira
corrigir_menu.py
"""

import os
import re

def corrigir_menu_base_html():
    """Corrige o menu no base.html"""
    print("🎨 CORRIGINDO MENU NO BASE.HTML...")
    
    try:
        # Ler arquivo atual
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        print("📄 Arquivo base.html lido com sucesso")
        
        # Verificar se já tem o item
        if 'analise_financeira.index' in conteudo or 'Análise Financeira' in conteudo:
            print("✅ Menu já contém Análise Financeira")
            return True
        
        # Item do menu para adicionar
        menu_item = '''                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('analise_financeira.index') }}">
                            <i class="fas fa-chart-line"></i> Análise Financeira
                        </a>
                    </li>'''
        
        print("🔍 Procurando local para inserir item de menu...")
        
        # Estratégia 1: Inserir após CTEs
        if '<i class="fas fa-file-alt"></i> CTEs' in conteudo:
            print("📍 Encontrado item CTEs - inserindo após...")
            
            # Padrão mais específico para CTEs
            padrao_ctes = r'(<li class="nav-item"[^>]*>\s*<a class="nav-link"[^>]*>\s*<i class="fas fa-file-alt"></i> CTEs\s*</a>\s*</li>)'
            
            match = re.search(padrao_ctes, conteudo, re.MULTILINE | re.DOTALL)
            if match:
                # Inserir após o item CTEs
                conteudo = conteudo.replace(match.group(1), match.group(1) + '\n' + menu_item)
                print("✅ Item inserido após CTEs")
            else:
                print("❌ Padrão CTEs não encontrado - tentando método alternativo...")
                return False
        
        # Estratégia 2: Inserir antes do dropdown do usuário
        elif '<ul class="navbar-nav">' in conteudo and 'dropdown' in conteudo:
            print("📍 Inserindo antes do dropdown do usuário...")
            
            # Encontrar o primeiro </ul> antes do dropdown
            lines = conteudo.split('\n')
            for i, line in enumerate(lines):
                if '</ul>' in line and any('dropdown' in lines[j] for j in range(i+1, min(i+10, len(lines)))):
                    # Inserir antes deste </ul>
                    lines.insert(i, menu_item)
                    conteudo = '\n'.join(lines)
                    print("✅ Item inserido antes do dropdown")
                    break
            else:
                print("❌ Local para inserção não encontrado")
                return False
        
        # Estratégia 3: Inserir no final dos itens de navegação
        else:
            print("📍 Inserindo no final dos itens de navegação...")
            
            # Procurar por </ul> que fecha a lista de navegação
            if '</ul>' in conteudo:
                # Inserir antes do primeiro </ul>
                pos = conteudo.find('</ul>')
                conteudo = conteudo[:pos] + menu_item + '\n                ' + conteudo[pos:]
                print("✅ Item inserido no final da navegação")
            else:
                print("❌ Estrutura de navegação não encontrada")
                return False
        
        # Salvar arquivo
        with open('app/templates/base.html', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("💾 Arquivo base.html salvo com sucesso")
        
        # Verificar se foi inserido corretamente
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            conteudo_verificacao = f.read()
        
        if 'Análise Financeira' in conteudo_verificacao or 'analise_financeira.index' in conteudo_verificacao:
            print("✅ MENU CORRIGIDO COM SUCESSO!")
            return True
        else:
            print("❌ Falha na verificação - item não foi inserido")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir menu: {e}")
        return False

def mostrar_estrutura_menu():
    """Mostra a estrutura atual do menu para debug"""
    print("\n🔍 ESTRUTURA ATUAL DO MENU:")
    
    try:
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Extrair seção do menu
        lines = conteudo.split('\n')
        menu_lines = []
        in_menu = False
        
        for line in lines:
            if '<ul class="navbar-nav me-auto">' in line or '<ul class="navbar-nav">' in line:
                in_menu = True
                menu_lines.append(line.strip())
            elif in_menu and '</ul>' in line:
                menu_lines.append(line.strip())
                break
            elif in_menu:
                menu_lines.append(line.strip())
        
        for i, line in enumerate(menu_lines):
            print(f"{i+1:2d}: {line}")
            
    except Exception as e:
        print(f"❌ Erro ao mostrar estrutura: {e}")

def criar_menu_backup():
    """Criar backup do menu atual"""
    print("\n💾 Criando backup do menu...")
    
    try:
        import shutil
        shutil.copy('app/templates/base.html', 'app/templates/base.html.backup')
        print("✅ Backup criado: app/templates/base.html.backup")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def main():
    """Função principal"""
    print("🎨 CORREÇÃO ESPECÍFICA DO MENU - ANÁLISE FINANCEIRA")
    print("="*60)
    
    # Criar backup
    criar_menu_backup()
    
    # Mostrar estrutura atual
    mostrar_estrutura_menu()
    
    # Corrigir menu
    sucesso = corrigir_menu_base_html()
    
    if sucesso:
        print("\n" + "="*60)
        print("🎉 MENU CORRIGIDO COM SUCESSO!")
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Reiniciar aplicação: python iniciar.py")
        print("2. Acessar: http://localhost:5000")
        print("3. Verificar se 'Análise Financeira' aparece no menu")
        print("4. Clicar no item e verificar se a página carrega")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ FALHA NA CORREÇÃO DO MENU")
        print("📋 SOLUÇÕES ALTERNATIVAS:")
        print("1. Abrir app/templates/base.html manualmente")
        print("2. Procurar por '<i class=\"fas fa-file-alt\"></i> CTEs'")
        print("3. Adicionar este código após o item CTEs:")
        print("""
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('analise_financeira.index') }}">
                            <i class="fas fa-chart-line"></i> Análise Financeira
                        </a>
                    </li>""")
        print("4. Salvar o arquivo e reiniciar")
        print("="*60)
    
    return sucesso

if __name__ == '__main__':
    main()