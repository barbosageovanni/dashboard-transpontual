#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico da API de listagem
"""

import requests

def testar_api_listagem():
    """Testar API de listagem de CTEs"""
    session = requests.Session()
    
    print("=== Testando API de Listagem ===")
    
    # Login
    login_data = {"username": "teste", "password": "123456"}
    response = session.post("http://localhost:5000/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado")
    
    # Testar API de listagem
    print("\n--- Testando /ctes/api/listar ---")
    response = session.get("http://localhost:5000/ctes/api/listar")
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ JSON válido retornado")
            print(f"Success: {data.get('success', 'N/A')}")
            print(f"Total CTEs: {data.get('pagination', {}).get('total', 'N/A')}")
            print(f"CTEs retornados: {len(data.get('data', []))}")
            
            if data.get('data'):
                primeiro_cte = data['data'][0]
                print(f"Primeiro CTE: {primeiro_cte.get('numero_cte')} - {primeiro_cte.get('destinatario_nome', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Erro no JSON: {e}")
            print(f"Raw response: {response.text[:500]}")
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    
    # Testar rota de emergência
    print("\n--- Testando rota de emergência ---")
    response = session.get("http://localhost:5000/ctes/api/listar-emergencia")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ Rota de emergência funcionando")
            print(f"CTEs encontrados: {len(data.get('data', []))}")
        except Exception as e:
            print(f"❌ Erro na rota de emergência: {e}")

if __name__ == "__main__":
    testar_api_listagem()
