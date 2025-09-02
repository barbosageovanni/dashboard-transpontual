#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os

def testar_upload_direto():
    """Testa o upload direto via API"""
    
    print("=== TESTE DE UPLOAD DIRETO ===")
    
    # Usar um dos templates criados
    if os.path.exists("template_cte_melhorado.csv"):
        arquivo_teste = "template_cte_melhorado.csv"
    elif os.path.exists("manual_template.csv"):
        arquivo_teste = "manual_template.csv"
    else:
        print("❌ Nenhum arquivo de teste encontrado")
        return
    
    print(f"📁 Usando arquivo: {arquivo_teste}")
    
    # Tentar fazer upload sem autenticação (para ver o erro)
    print("\n1. Teste sem autenticação...")
    try:
        with open(arquivo_teste, 'rb') as f:
            files = {'arquivo': f}
            data = {'modo': 'alterar'}
            response = requests.post(
                'http://localhost:5000/ctes/api/atualizar-lote',
                files=files,
                data=data
            )
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Tamanho resposta: {len(response.text)}")
        
        if response.headers.get('Content-Type', '').startswith('application/json'):
            print("   Resposta JSON:")
            print(f"   {response.json()}")
        else:
            print("   Resposta HTML (primeiros 200 chars):")
            print(f"   {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Tentar com sessão autenticada
    print("\n2. Teste com sessão autenticada...")
    try:
        session = requests.Session()
        
        # Fazer login primeiro
        login_data = {'username': 'admin', 'password': 'senha123'}
        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        # Agora tentar upload
        with open(arquivo_teste, 'rb') as f:
            files = {'arquivo': f}
            data = {'modo': 'alterar'}
            response = session.post(
                'http://localhost:5000/ctes/api/atualizar-lote',
                files=files,
                data=data
            )
        
        print(f"   Upload status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.headers.get('Content-Type', '').startswith('application/json'):
            print("   ✅ Resposta JSON:")
            result = response.json()
            print(f"   Sucesso: {result.get('sucesso')}")
            print(f"   Mensagem: {result.get('mensagem')}")
            if 'detalhes' in result:
                print(f"   Detalhes: {len(result.get('detalhes', []))} itens")
        else:
            print("   ❌ Resposta HTML (primeiros 200 chars):")
            print(f"   {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    testar_upload_direto()
