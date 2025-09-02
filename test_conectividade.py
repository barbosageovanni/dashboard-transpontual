#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste básico de endpoint de debug para verificar se servidor está OK
"""

import requests

def test_debug_endpoint():
    """Testar o endpoint debug simples"""
    try:
        response = requests.get("http://localhost:5000/ctes/debug/service-status")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ Response JSON válida:")
                print(data)
                
                # Verificar se os serviços estão OK
                if data.get('atualizacao_service_ok') and data.get('importacao_service_ok'):
                    print("✓ Serviços de importação e atualização funcionando")
                    return True
                else:
                    print("✗ Problemas nos serviços")
                    return False
                    
            except Exception as e:
                print(f"✗ Erro ao parsear JSON: {e}")
                return False
        else:
            print(f"✗ Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Erro na requisição: {e}")
        return False

def test_template_endpoints():
    """Testar endpoints de template sem autenticação"""
    print("\n=== Testando Templates ===")
    
    # CSV template
    try:
        response = requests.get("http://localhost:5000/ctes/api/template-csv")
        print(f"CSV Template - Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Endpoint protegido por autenticação (esperado)")
        elif response.status_code == 200:
            print("⚠️ Endpoint não protegido")
    except Exception as e:
        print(f"Erro CSV: {e}")
    
    # Excel template
    try:
        response = requests.get("http://localhost:5000/ctes/api/template-excel")
        print(f"Excel Template - Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Endpoint protegido por autenticação (esperado)")
        elif response.status_code == 200:
            print("⚠️ Endpoint não protegido")
    except Exception as e:
        print(f"Erro Excel: {e}")

if __name__ == "__main__":
    print("=== Teste Básico de Conectividade ===")
    
    if test_debug_endpoint():
        test_template_endpoints()
    else:
        print("✗ Servidor não está respondendo corretamente")
