#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das rotas de download/export
"""

import requests

def testar_downloads():
    """Testar endpoints de download"""
    session = requests.Session()
    
    # Login
    login_data = {"username": "teste", "password": "123456"}
    response = session.post("http://localhost:5000/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado")
    
    # Testar downloads
    endpoints = [
        ("/ctes/api/download/csv", "CSV"),
        ("/ctes/api/download/excel", "Excel"),
        ("/ctes/api/download/pdf", "PDF")
    ]
    
    for endpoint, tipo in endpoints:
        try:
            response = session.get(f"http://localhost:5000{endpoint}")
            print(f"\n=== {tipo} Download ===")
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                if 'json' in response.headers.get('Content-Type', ''):
                    data = response.json()
                    if data.get('success', True):
                        print(f"✅ {tipo} gerado com sucesso!")
                    else:
                        print(f"⚠️ {tipo}: {data.get('message', 'Erro')}")
                else:
                    print(f"✅ {tipo} baixado ({len(response.content)} bytes)")
            elif response.status_code == 501:
                print(f"ℹ️ {tipo} não implementado (esperado)")
            else:
                print(f"❌ {tipo} erro: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro no {tipo}: {e}")

if __name__ == "__main__":
    testar_downloads()
