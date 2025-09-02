#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de autenticação e upload para debug do erro de JSON
"""

import requests
import io
import sys
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
UPLOAD_URL = f"{BASE_URL}/ctes/api/atualizar-lote"

def fazer_login(session, username="teste", password="123456"):
    """Fazer login via POST e capturar cookies"""
    print(f"Fazendo login com {username}...")
    
    # Primeiro GET para pegar possíveis tokens CSRF
    response = session.get(LOGIN_URL)
    print(f"GET login page - Status: {response.status_code}")
    
    # Dados do login
    login_data = {
        "username": username,
        "password": password
    }
    
    # Fazer login
    response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
    print(f"POST login - Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code in [302, 200]:
        print("✓ Login bem-sucedido!")
        return True
    else:
        print(f"✗ Falha no login: {response.text[:200]}")
        return False

def testar_upload_com_autenticacao():
    """Testar upload após fazer login"""
    session = requests.Session()
    
    # Fazer login
    if not fazer_login(session):
        return False
    
    # Verificar se estamos autenticados
    auth_test = session.get(f"{BASE_URL}/ctes/")
    print(f"Teste de auth na página CTEs - Status: {auth_test.status_code}")
    if auth_test.status_code != 200:
        print("✗ Não conseguiu acessar página protegida após login")
        return False
    
    # Criar arquivo CSV de teste
    csv_content = """Número CTE;Destinatário;Placa Veículo;Valor Total;Data Emissão;Data Baixa;Número Fatura;Data Inclusão Fatura;Data Envio Processo;Primeiro Envio;Data RQ/TMC;Data Atesto;Envio Final;Observação;Origem dos Dados
CTE001;Empresa Teste;ABC1234;1500.50;2024-01-15;2024-01-20;FAT001;2024-01-16;2024-01-17;Sim;2024-01-18;2024-01-19;Sim;Teste de importação;Importação Manual"""
    
    # Criar arquivo em memória
    arquivo = io.StringIO(csv_content)
    
    # Preparar dados do upload
    files = {
        'arquivo': ('teste.csv', csv_content, 'text/csv')
    }
    data = {
        'modo': 'alterar'
    }
    
    print("\nFazendo upload do arquivo...")
    response = session.post(UPLOAD_URL, files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"Response length: {len(response.text)}")
    
    # Verificar se é JSON ou HTML
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            json_response = response.json()
            print("✓ Resposta JSON válida:")
            print(json_response)
            return True
        except Exception as e:
            print(f"✗ Erro ao fazer parse do JSON: {e}")
            print(f"Raw response: {response.text[:500]}")
            return False
    else:
        print("✗ Resposta não é JSON!")
        print(f"Content-Type: {content_type}")
        print(f"First 500 chars: {response.text[:500]}")
        
        # Verificar se é redirect para login
        if "login" in response.text.lower() or "<!doctype" in response.text.lower():
            print("Parece ser uma página de login - sessão expirou ou auth falhou")
        
        return False

if __name__ == "__main__":
    print("=== Teste de Autenticação e Upload ===")
    testar_upload_com_autenticacao()
