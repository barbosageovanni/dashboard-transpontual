#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir automaticamente o dropdown do usuário
"""

import os
import shutil
from datetime import datetime

def fazer_backup(arquivo):
    """Faz backup do arquivo original"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{arquivo}.backup_{timestamp}"
    shutil.copy2(arquivo, backup_file)
    print(f"✅ Backup criado: {backup_file}")
    return backup_file

def corrigir_dropdown():
    """Corrige o dropdown do usuário no base.html"""
    
    arquivo = "app/templates/base.html"
    
    print("🔧 CORRIGINDO DROPDOWN DO USUÁRIO")
    print("=" * 40)
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    # Fazer backup
    backup_file = fazer_backup(arquivo)
    
    try:
        # Ler arquivo atual
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 Arquivo lido com sucesso")
        
        # Dropdown antigo (o que vimos no script anterior)
        dropdown_antigo = '''                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">
                                <i class="fas fa-sign-out-alt"></i> Sair
                            </a></li>
                        </ul>'''
        
        # Dropdown novo com "Minha Conta" e "Administração"
        dropdown_novo = '''                        <ul class="dropdown-menu dropdown-menu-end">
                            <!-- ✨ Link para perfil do usuário -->
                            <li><a class="dropdown-item" href="{{ url_for('auth.profile') }}">
                                <i class="fas fa-user-circle"></i> Minha Conta
                            </a></li>
                            
                            <!-- ✨ Separador -->
                            <li><hr class="dropdown-divider"></li>
                            
                            <!-- ✨ Link para administração (apenas para admins) -->
                            {% if current_user.tipo_usuario == 'admin' %}
                            <li><a class="dropdown-item" href="{{ url_for('admin.index') }}">
                                <i class="fas fa-cogs"></i> Administração
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            {% endif %}
                            
                            <!-- Logout -->
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">
                                <i class="fas fa-sign-out-alt"></i> Sair
                            </a></li>
                        </ul>'''
        
        # Fazer a substituição
        if dropdown_antigo in content:
            content_novo = content.replace(dropdown_antigo, dropdown_novo)
            print("✅ Dropdown antigo encontrado e substituído")
        else:
            # Tentar uma abordagem mais flexível
            print("⚠️ Dropdown exato não encontrado, tentando abordagem alternativa...")
            
            # Procurar por padrões mais genéricos
            import re
            
            # Padrão: <ul class="dropdown-menu"> ... </ul> que contém "Sair"
            pattern = r'<ul class="dropdown-menu"[^>]*>.*?</ul>'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                if 'Sair' in match and 'auth.logout' in match:
                    print(f"🔍 Encontrado dropdown: {match[:100]}...")
                    content_novo = content.replace(match, dropdown_novo)
                    print("✅ Substituição realizada")
                    break
            else:
                print("❌ Não foi possível localizar o dropdown para substituição")
                return False
        
        # Verificar se houve mudanças
        if content == content_novo:
            print("⚠️ Nenhuma alteração foi feita")
            return False
        
        # Escrever arquivo modificado
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(content_novo)
        
        print("✅ Arquivo atualizado com sucesso!")
        
        # Verificar se as modificações estão presentes
        verificar_modificacoes(arquivo)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        
        # Restaurar backup em caso de erro
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, arquivo)
            print(f"🔄 Backup restaurado: {backup_file} -> {arquivo}")
        
        return False

def verificar_modificacoes(arquivo):
    """Verifica se as modificações foram aplicadas corretamente"""
    
    print("\n🔍 VERIFICANDO MODIFICAÇÕES...")
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificacoes = [
            ("Minha Conta", "Minha Conta"),
            ("Link perfil", "auth.profile"),
            ("Ícone user-circle", "fas fa-user-circle"),
            ("Separador", "dropdown-divider"),
            ("Condicional admin", "current_user.tipo_usuario == 'admin'"),
            ("Link admin", "admin.index"),
            ("Dropdown menu end", "dropdown-menu-end")
        ]
        
        sucesso = 0
        total = len(verificacoes)
        
        for desc, pattern in verificacoes:
            if pattern in content:
                print(f"  ✅ {desc}")
                sucesso += 1
            else:
                print(f"  ❌ {desc}")
        
        print(f"\n📊 RESULTADO: {sucesso}/{total} verificações passaram")
        
        if sucesso >= total * 0.8:  # 80% ou mais
            print("🎉 CORREÇÃO APLICADA COM SUCESSO!")
            return True
        else:
            print("⚠️ Algumas verificações falharam")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    sucesso = corrigir_dropdown()
    
    if sucesso:
        print("\n" + "=" * 50)
        print("🎯 PRÓXIMOS PASSOS:")
        print("1. Atualizar a página no navegador (Ctrl+F5)")
        print("2. Clicar no dropdown do usuário")
        print("3. Verificar se 'Minha Conta' aparece")
        print("4. Testar o link 'Minha Conta'")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ CORREÇÃO FALHOU")
        print("💡 Tente a correção manual ou verifique os logs acima")
        print("=" * 50)