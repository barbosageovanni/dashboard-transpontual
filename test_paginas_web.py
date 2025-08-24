#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das páginas web frontend
"""

import requests

def testar_paginas_web():
    """Testar páginas web do frontend"""
    session = requests.Session()
    
    print("=== Testando Páginas Web ===")
    
    # Login
    login_data = {"username": "teste", "password": "123456"}
    response = session.post("http://localhost:5000/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado")
    
    # Testar páginas principais
    paginas = [
        ("/", "Página principal"),
        ("/dashboard/", "Dashboard"),
        ("/ctes/", "CTEs principal"),
        ("/ctes/listar", "CTEs listar"),
        ("/ctes/atualizar-lote", "CTEs importação"),
        ("/admin/", "Admin (pode dar 403)")
    ]
    
    for url, nome in paginas:
        print(f"\n--- {nome} ({url}) ---")
        try:
            response = session.get(f"http://localhost:5000{url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Página carregada")
                if "<!DOCTYPE html>" in response.text:
                    print("✅ HTML válido")
                else:
                    print("⚠️ Não parece ser HTML")
            elif response.status_code == 302:
                print(f"↪️ Redirect para: {response.headers.get('Location', 'N/A')}")
            elif response.status_code == 403:
                print("🔒 Acesso negado (normal para admin)")
            elif response.status_code == 404:
                print("❌ Página não encontrada")
            else:
                print(f"⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_paginas_web()
