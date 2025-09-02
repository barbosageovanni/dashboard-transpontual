#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste dos endpoints corretos de template
"""

import requests

def test_correct_endpoints():
    """Testar os endpoints corretos"""
    
    print("=== Testando Endpoints Corretos ===")
    
    # CSV (endpoint API)
    try:
        response = requests.get("http://localhost:5000/ctes/api/template-csv")
        print(f"CSV API - Status: {response.status_code}")
        if response.status_code == 200:
            print("⚠️ CSV endpoint não protegido!")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content preview: {response.text[:100]}...")
        elif response.status_code == 401:
            print("✓ CSV protegido por autenticação")
    except Exception as e:
        print(f"Erro CSV: {e}")
    
    # Excel (endpoint de download)
    try:
        response = requests.get("http://localhost:5000/ctes/template-atualizacao.xlsx")
        print(f"Excel Download - Status: {response.status_code}")
        if response.status_code == 200:
            print("⚠️ Excel endpoint não protegido!")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content length: {len(response.content)} bytes")
        elif response.status_code == 401:
            print("✓ Excel protegido por autenticação")
        elif response.status_code == 302:
            print("✓ Excel redirect (provavelmente para login)")
            print(f"Location: {response.headers.get('Location')}")
    except Exception as e:
        print(f"Erro Excel: {e}")
    
    # Testar upload endpoint
    try:
        response = requests.post("http://localhost:5000/ctes/api/atualizar-lote")
        print(f"Upload endpoint - Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Upload protegido por autenticação")
        elif response.status_code == 405:
            print("✓ Upload requer POST e dados")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Content: {response.text[:100]}")
    except Exception as e:
        print(f"Erro Upload: {e}")

if __name__ == "__main__":
    test_correct_endpoints()
