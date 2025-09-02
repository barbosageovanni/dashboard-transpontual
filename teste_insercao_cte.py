#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da inserção de CTE via API
teste_insercao_cte.py
"""

import requests
import json
from datetime import date

# Configurações
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
INSERIR_URL = f"{BASE_URL}/ctes/api/inserir"

def testar_insercao_cte():
    """Testa a inserção de um CTE via API"""
    
    # Dados de login
    login_data = {
        "username": "admin",
        "password": "Admin123!"
    }
    
    # Dados do CTE para teste
    import time
    numero_teste = int(time.time()) % 1000000  # Último 6 dígitos do timestamp
    
    cte_data = {
        "numero_cte": numero_teste,  # Número único para teste
        "destinatario_nome": "Teste Inserção",
        "veiculo_placa": "ABC-1234",
        "valor_total": 1500.00,
        "data_emissao": str(date.today()),
        "observacao": "CTE de teste via API"
    }
    
    try:
        # Criar sessão para manter cookies
        session = requests.Session()
        
        print("🔑 Fazendo login...")
        
        # 1. Fazer login
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # 2. Tentar inserir CTE
        print(f"➕ Inserindo CTE {cte_data['numero_cte']}...")
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        inserir_response = session.post(
            INSERIR_URL, 
            json=cte_data,
            headers=headers
        )
        
        print(f"Inserção status: {inserir_response.status_code}")
        print(f"Response headers: {dict(inserir_response.headers)}")
        
        if inserir_response.status_code == 200:
            response_data = inserir_response.json()
            print("✅ Resposta da API:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            if response_data.get('success'):
                print("🎉 CTE inserido com sucesso!")
                return True
            else:
                print(f"❌ Erro na inserção: {response_data.get('message')}")
                return False
        else:
            print(f"❌ Erro HTTP {inserir_response.status_code}")
            print(f"Response text: {inserir_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na execução do teste: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DE INSERÇÃO DE CTE")
    print("=" * 50)
    
    sucesso = testar_insercao_cte()
    
    print("=" * 50)
    if sucesso:
        print("🎉 TESTE PASSOU! Inserção funcionando corretamente.")
    else:
        print("❌ TESTE FALHOU! Verificar logs e implementação.")
