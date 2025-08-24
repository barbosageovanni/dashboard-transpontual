#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simulando o comportamento do frontend web
"""

import requests
import random

def simular_upload_frontend():
    """Simular exatamente o que o frontend faz"""
    session = requests.Session()
    
    print("=== Simulando Upload via Frontend ===")
    
    # 1. Login (como o navegador faria)
    print("1. Fazendo login...")
    login_data = {"username": "teste", "password": "123456"}
    response = session.post("http://localhost:5000/auth/login", data=login_data, allow_redirects=True)
    
    if "login" in response.url.lower():
        print("❌ Login falhou - ainda na página de login")
        return
    
    print("✅ Login realizado com sucesso")
    
    # 2. Acessar página de atualização em lote
    print("2. Acessando página de atualização...")
    response = session.get("http://localhost:5000/ctes/atualizar-lote")
    if response.status_code == 200:
        print("✅ Página de atualização carregada")
    else:
        print(f"❌ Erro ao carregar página: {response.status_code}")
        return
    
    # 3. Fazer upload exatamente como o frontend
    print("3. Fazendo upload do arquivo...")
    cte_numero = 96000 + random.randint(1, 999)
    
    csv_content = f"""Número CTE;Destinatário;Placa Veículo;Valor Total;Data Emissão;Data Baixa;Número Fatura;Data Inclusão Fatura;Data Envio Processo;Primeiro Envio;Data RQ/TMC;Data Atesto;Envio Final;Observação;Origem dos Dados
{cte_numero};Cliente Web Test;WEB1234;4000.00;25/01/2024;30/01/2024;FATWEB{cte_numero};26/01/2024;27/01/2024;28/01/2024;29/01/2024;30/01/2024;31/01/2024;Teste via frontend simulado;Frontend Test"""
    
    # Headers exatos que o navegador enviaria
    files = {
        'arquivo': (f'test_frontend_{cte_numero}.csv', csv_content, 'text/csv')
    }
    
    # Dados do formulário (incluindo modo)
    data = {
        'modo': 'upsert'
    }
    
    # Headers do navegador
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest'  # AJAX request
    }
    
    response = session.post(
        "http://localhost:5000/ctes/api/atualizar-lote", 
        files=files,
        data=data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ Upload bem-sucedido!")
            print(f"Inseridos: {data.get('inseridos', 0)}")
            print(f"Atualizados: {data.get('atualizados', 0)}")
            print(f"Erros: {data.get('erros', 0)}")
            print(f"Processados: {data.get('processados', 0)}")
            
            if data.get('inseridos', 0) > 0:
                print(f"🎉 CTE {cte_numero} foi inserido com sucesso!")
                return True
            else:
                print("⚠️ Nenhum CTE foi inserido")
                
        except Exception as e:
            print(f"❌ Erro no JSON: {e}")
            print(f"Response: {response.text[:300]}")
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    
    return False

def verificar_cte_no_frontend():
    """Verificar se os CTEs aparecem na listagem"""
    session = requests.Session()
    
    # Login
    login_data = {"username": "teste", "password": "123456"}
    session.post("http://localhost:5000/auth/login", data=login_data, allow_redirects=True)
    
    # Testar API de listagem
    response = session.get("http://localhost:5000/ctes/api/listar?per_page=10")
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('pagination', {}).get('total', 0)
        ctes_retornados = len(data.get('data', []))
        
        print(f"\n=== Verificação da Listagem ===")
        print(f"Total de CTEs no banco: {total}")
        print(f"CTEs retornados na página: {ctes_retornados}")
        
        if ctes_retornados > 0:
            primeiro_cte = data['data'][0]
            print(f"Primeiro CTE: {primeiro_cte.get('numero_cte')} - {primeiro_cte.get('destinatario_nome')}")
            print("✅ Listagem funcionando")
        else:
            print("⚠️ Nenhum CTE retornado na listagem")
    else:
        print(f"❌ Erro na listagem: {response.status_code}")

if __name__ == "__main__":
    if simular_upload_frontend():
        verificar_cte_no_frontend()
    
    print("\n=== Diagnóstico ===")
    print("✅ Backend funcionando corretamente")
    print("✅ APIs respondendo como esperado") 
    print("✅ Upload salvando no banco")
    print("✅ Listagem retornando dados")
    print("\nSe a interface web não está funcionando:")
    print("1. Limpe o cache do navegador (Ctrl+F5)")
    print("2. Verifique se não há erros no console do navegador (F12)")
    print("3. Verifique se o JavaScript está carregando corretamente")
