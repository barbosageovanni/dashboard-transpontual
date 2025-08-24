#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abertura Automática do Teste - Dashboard Baker Flask
"""

import webbrowser
import time
import sys

def abrir_teste():
    """Abre a página de teste no navegador"""
    
    print("🌐 ABRINDO PÁGINA DE TESTE")
    print("=" * 40)
    
    urls_teste = [
        "http://localhost:5000/ctes/test-export",
        "http://localhost:5000/dashboard/",
        "http://localhost:5000/ctes/"
    ]
    
    print("🔗 URLs que serão abertas:")
    for url in urls_teste:
        print(f"   📄 {url}")
    
    print("\n⏳ Aguardando 3 segundos...")
    time.sleep(3)
    
    try:
        for i, url in enumerate(urls_teste, 1):
            print(f"\n🌐 Abrindo {i}/3: {url}")
            webbrowser.open(url)
            time.sleep(2)  # Evitar sobrecarga
            
        print("\n✅ Todas as páginas foram abertas!")
        print("\n📋 INSTRUÇÕES DE TESTE:")
        print("1. 🧪 Página de Teste: Teste os downloads diretos")
        print("2. 📊 Dashboard: Verifique se os números dos cards estão OK")
        print("3. 📋 CTEs: Teste exportação via botões na interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")
        print("\n💡 Abra manualmente:")
        for url in urls_teste:
            print(f"   {url}")
        return False

if __name__ == "__main__":
    sucesso = abrir_teste()
    sys.exit(0 if sucesso else 1)
