#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT RÁPIDO - Alteração de Cabeçalho
Versão simplificada para alteração rápida
"""

import os

def alterar_cabecalho_rapido():
    print("🚛 ALTERAÇÃO RÁPIDA DO CABEÇALHO")
    print("=" * 40)
    
    arquivo = 'app/templates/base.html'
    
    if not os.path.exists(arquivo):
        print("❌ Arquivo base.html não encontrado!")
        return
    
    try:
        # Ler arquivo
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Fazer substituição simples
        conteudo_novo = conteudo.replace(
            'Dashboard Financeiro Baker', 
            'Dashboard Transpontual'
        )
        
        conteudo_novo = conteudo_novo.replace(
            'fa-chart-line', 
            'fa-truck'
        )
        
        # Salvar
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        
        print("✅ Cabeçalho alterado com sucesso!")
        print("🔄 Reinicie o servidor")
        print("🌐 Pressione Ctrl+F5 no navegador")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    alterar_cabecalho_rapido()