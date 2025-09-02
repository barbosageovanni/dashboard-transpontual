#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def listar_rotas_disponiveis():
    """Lista rotas que retornam 200 ou 4xx para identificar endpoints válidos"""
    
    base_url = "http://localhost:5000"
    
    # Rotas para testar
    rotas_teste = [
        "/ctes/api/atualizar-lote",
        "/ctes/atualizar-lote", 
        "/api/ctes/atualizar-lote",
        "/ctes/upload",
        "/ctes/api/upload",
        "/ctes/api/bulk-update",
        "/ctes/bulk-update"
    ]
    
    print("=== TESTANDO ROTAS DISPONÍVEIS ===\n")
    
    for rota in rotas_teste:
        try:
            # Teste GET
            response_get = requests.get(f"{base_url}{rota}")
            print(f"GET {rota}")
            print(f"   Status: {response_get.status_code}")
            print(f"   Content-Type: {response_get.headers.get('Content-Type', 'N/A')}")
            
            # Teste POST
            response_post = requests.post(f"{base_url}{rota}")
            print(f"POST {rota}")
            print(f"   Status: {response_post.status_code}")
            print(f"   Content-Type: {response_post.headers.get('Content-Type', 'N/A')}")
            print()
            
        except Exception as e:
            print(f"   ❌ Erro testando {rota}: {e}")
            print()

def testar_endpoints_debug():
    """Testa endpoints que sabemos que funcionam"""
    
    print("=== TESTANDO ENDPOINTS CONHECIDOS ===\n")
    
    endpoints = [
        "/ctes/debug/service-status",
        "/ctes/template-atualizacao.csv",
        "/ctes/template-atualizacao.xlsx"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}")
            print(f"GET {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            if response.status_code == 200:
                if 'json' in response.headers.get('Content-Type', ''):
                    print(f"   ✅ JSON Response")
                elif 'text/csv' in response.headers.get('Content-Type', ''):
                    print(f"   ✅ CSV Response ({len(response.text)} chars)")
                elif 'spreadsheet' in response.headers.get('Content-Type', ''):
                    print(f"   ✅ Excel Response ({len(response.content)} bytes)")
                else:
                    print(f"   ⚠️  Unexpected content type")
            print()
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            print()

if __name__ == "__main__":
    testar_endpoints_debug()
    listar_rotas_disponiveis()
