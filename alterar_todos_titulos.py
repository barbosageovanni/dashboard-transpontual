#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Completo - Alterar TODOS os Títulos do Sistema
Altera títulos em todos os templates para "Dashboard Transpontual"
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def main():
    print("🚛 ALTERAÇÃO COMPLETA DE TÍTULOS DO SISTEMA")
    print("=" * 60)
    
    # Arquivos a serem alterados
    arquivos_para_alterar = [
        'app/templates/base.html',
        'app/templates/dashboard/index.html',
        'app/templates/analise_financeira/index.html',
        'app/templates/baixas/index.html',
        'app/templates/admin/index.html',
        'app/templates/auth/login.html'
    ]
    
    # Fazer backup de todos os arquivos
    fazer_backup_multiplos(arquivos_para_alterar)
    
    # Aplicar alterações
    total_alteracoes = 0
    
    for arquivo in arquivos_para_alterar:
        if os.path.exists(arquivo):
            print(f"\n🔧 Processando: {arquivo}")
            alteracoes = alterar_arquivo(arquivo)
            total_alteracoes += alteracoes
        else:
            print(f"⚠️ Arquivo não encontrado: {arquivo}")
    
    print(f"\n✅ CONCLUÍDO! {total_alteracoes} alterações realizadas")
    print("🔄 Reinicie o servidor: python iniciar.py")
    print("🌐 Limpe o cache: Ctrl+F5 no navegador")
    
    return total_alteracoes > 0

def fazer_backup_multiplos(arquivos):
    """Faz backup de múltiplos arquivos"""
    print("📦 Fazendo backup dos arquivos...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backup_templates_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            # Manter estrutura de diretórios
            arquivo_path = Path(arquivo)
            backup_path = Path(backup_dir) / arquivo_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(arquivo, backup_path)
            print(f"  ✅ Backup: {arquivo}")
    
    print(f"  📁 Backups salvos em: {backup_dir}")

def alterar_arquivo(arquivo):
    """Altera um arquivo específico"""
    try:
        # Ler arquivo
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo_original = conteudo
        alteracoes_count = 0
        
        # Definir substituições baseadas no tipo de arquivo
        if 'dashboard/index.html' in arquivo:
            substituicoes = obter_substituicoes_dashboard()
        elif 'analise_financeira' in arquivo:
            substituicoes = obter_substituicoes_analise()
        elif 'baixas' in arquivo:
            substituicoes = obter_substituicoes_baixas()
        elif 'admin' in arquivo:
            substituicoes = obter_substituicoes_admin()
        elif 'login.html' in arquivo:
            substituicoes = obter_substituicoes_login()
        else:
            substituicoes = obter_substituicoes_gerais()
        
        # Aplicar cada substituição
        for sub in substituicoes:
            antes = conteudo
            conteudo = re.sub(sub['buscar'], sub['substituir'], conteudo, flags=re.IGNORECASE | re.MULTILINE)
            
            if conteudo != antes:
                alteracoes_count += 1
                print(f"    ✅ {sub['descricao']}")
        
        # Salvar se houve alterações
        if conteudo != conteudo_original:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"    💾 Arquivo salvo com {alteracoes_count} alterações")
        else:
            print(f"    📝 Nenhuma alteração necessária")
        
        return alteracoes_count
        
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return 0

def obter_substituicoes_dashboard():
    """Substituições específicas para dashboard/index.html"""
    return [
        {
            'buscar': r'💰\s*Dashboard Financeiro',
            'substituir': '🚛 Dashboard Transpontual',
            'descricao': 'Título principal H1'
        },
        {
            'buscar': r'Sistema Avançado de Gestão e Análise Financeira',
            'substituir': 'Sistema de Transporte e Logística Avançado',
            'descricao': 'Subtítulo principal'
        },
        {
            'buscar': r'Dashboard Financeiro',
            'substituir': 'Dashboard Transpontual',
            'descricao': 'Outras referências Dashboard Financeiro'
        },
        {
            'buscar': r'fa-chart-line',
            'substituir': 'fa-truck',
            'descricao': 'Ícone do gráfico → caminhão'
        },
        {
            'buscar': r'💰\s*Receita Total',
            'substituir': '💰 Faturamento Total',
            'descricao': 'Card Receita → Faturamento'
        }
    ]

def obter_substituicoes_analise():
    """Substituições para análise financeira"""
    return [
        {
            'buscar': r'Análise Financeira - Dashboard Baker',
            'substituir': 'Análise Financeira - Dashboard Transpontual',
            'descricao': 'Title da página'
        },
        {
            'buscar': r'Dashboard Baker',
            'substituir': 'Dashboard Transpontual',
            'descricao': 'Referências gerais'
        }
    ]

def obter_substituicoes_baixas():
    """Substituições para sistema de baixas"""
    return [
        {
            'buscar': r'Sistema de Baixas - Dashboard Baker',
            'substituir': 'Sistema de Baixas - Dashboard Transpontual',
            'descricao': 'Title da página'
        },
        {
            'buscar': r'Dashboard Baker',
            'substituir': 'Dashboard Transpontual',
            'descricao': 'Referências gerais'
        }
    ]

def obter_substituicoes_admin():
    """Substituições para área administrativa"""
    return [
        {
            'buscar': r'Área de Administração - Dashboard Baker',
            'substituir': 'Área de Administração - Dashboard Transpontual',
            'descricao': 'Title da página'
        },
        {
            'buscar': r'Painel de controle completo do Dashboard Baker',
            'substituir': 'Painel de controle completo do Dashboard Transpontual',
            'descricao': 'Subtítulo admin'
        },
        {
            'buscar': r'Dashboard Baker',
            'substituir': 'Dashboard Transpontual',
            'descricao': 'Referências gerais'
        }
    ]

def obter_substituicoes_login():
    """Substituições para tela de login"""
    return [
        {
            'buscar': r'💰\s*Baker',
            'substituir': '🚛 Transpontual',
            'descricao': 'Logo da empresa'
        },
        {
            'buscar': r'Dashboard Financeiro',
            'substituir': 'Sistema de Transporte',
            'descricao': 'Subtítulo do login'
        }
    ]

def obter_substituicoes_gerais():
    """Substituições gerais para qualquer arquivo"""
    return [
        {
            'buscar': r'Dashboard Financeiro Baker',
            'substituir': 'Dashboard Transpontual',
            'descricao': 'Navbar brand'
        },
        {
            'buscar': r'Dashboard Baker',
            'substituir': 'Dashboard Transpontual',
            'descricao': 'Referências gerais'
        },
        {
            'buscar': r'fa-chart-line',
            'substituir': 'fa-truck',
            'descricao': 'Ícones'
        }
    ]

def verificar_resultados():
    """Verifica se as alterações foram aplicadas"""
    print("\n🔍 VERIFICAÇÃO DOS RESULTADOS:")
    print("-" * 40)
    
    arquivos_verificar = [
        'app/templates/dashboard/index.html',
        'app/templates/base.html'
    ]
    
    for arquivo in arquivos_verificar:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            print(f"\n📄 {arquivo}:")
            
            # Verificar mudanças positivas
            if 'Dashboard Transpontual' in conteudo:
                count = conteudo.count('Dashboard Transpontual')
                print(f"  ✅ {count}x 'Dashboard Transpontual'")
            
            if 'fa-truck' in conteudo:
                print(f"  ✅ Ícone caminhão encontrado")
            
            # Verificar referências antigas
            antigas = conteudo.count('Dashboard Financeiro')
            if antigas > 0:
                print(f"  ⚠️ {antigas}x 'Dashboard Financeiro' ainda presente")
            else:
                print(f"  ✅ Nenhuma referência antiga")

def mostrar_preview():
    """Mostra preview das principais alterações"""
    print("\n👀 PREVIEW DAS PRINCIPAIS ALTERAÇÕES:")
    print("=" * 50)
    
    alteracoes_preview = [
        {
            'local': 'Cabeçalho (base.html)',
            'antes': '📊 Dashboard Financeiro Baker',
            'depois': '🚛 Dashboard Transpontual'
        },
        {
            'local': 'Título Principal (dashboard)',
            'antes': '💰 Dashboard Financeiro',
            'depois': '🚛 Dashboard Transpontual'
        },
        {
            'local': 'Subtítulo (dashboard)',
            'antes': 'Sistema Avançado de Gestão e Análise Financeira',
            'depois': 'Sistema de Transporte e Logística Avançado'
        },
        {
            'local': 'Login (empresa)',
            'antes': '💰 Baker',
            'depois': '🚛 Transpontual'
        }
    ]
    
    for alt in alteracoes_preview:
        print(f"\n📍 {alt['local']}:")
        print(f"   ANTES: {alt['antes']}")
        print(f"   DEPOIS: {alt['depois']}")

if __name__ == "__main__":
    print("🚛 SCRIPT COMPLETO DE ALTERAÇÃO DE TÍTULOS")
    print("Este script irá alterar TODOS os títulos do sistema")
    
    # Mostrar preview
    mostrar_preview()
    
    # Confirmação
    print("\n" + "="*50)
    resposta = input("❓ Deseja continuar com todas as alterações? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        sucesso = main()
        
        if sucesso:
            verificar_resultados()
            print("\n🎉 SISTEMA COMPLETAMENTE ATUALIZADO!")
            print("Agora todos os títulos mostram 'Dashboard Transpontual'")
        else:
            print("\n❌ Problemas durante a execução")
    else:
        print("❌ Operação cancelada pelo usuário")