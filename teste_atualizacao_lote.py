#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da atualização em lote de CTEs
teste_atualizacao_lote.py
"""

import requests
import json
import io
from datetime import date

# Configurações
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
LOTE_URL = f"{BASE_URL}/ctes/api/atualizar-lote"

def criar_csv_teste():
    """Cria um CSV de teste para upload"""
    csv_content = """Número CTE,Cliente,Placa Veículo,Valor Total,Data Emissão,Observação
777777,Teste Lote 1,ABC-1111,1000.50,2025-08-23,Teste via lote
777778,Teste Lote 2,ABC-2222,2000.75,2025-08-23,Segundo teste
"""
    return io.BytesIO(csv_content.encode('utf-8'))

def testar_atualizacao_lote():
    """Testa a atualização em lote de CTEs"""
    
    # Dados de login
    login_data = {
        "username": "admin",
        "password": "Admin123!"
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
        
        # 2. Preparar arquivo CSV
        print("📁 Preparando arquivo CSV de teste...")
        csv_file = criar_csv_teste()
        
        # 3. Testar atualização em lote
        print("📤 Enviando arquivo para atualização em lote...")
        
        files = {
            'arquivo': ('teste_lote.csv', csv_file, 'text/csv')
        }
        
        data = {
            'modo': 'upsert'  # Inserir se não existir, atualizar se existir
        }
        
        lote_response = session.post(
            LOTE_URL,
            files=files,
            data=data
        )
        
        print(f"Lote status: {lote_response.status_code}")
        print(f"Response headers: {dict(lote_response.headers)}")
        
        if lote_response.status_code == 200:
            response_data = lote_response.json()
            print("✅ Resposta da API:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            if response_data.get('sucesso'):
                print("🎉 Atualização em lote executada com sucesso!")
                return True
            else:
                print(f"❌ Erro na atualização: {response_data.get('mensagem')}")
                return False
        else:
            print(f"❌ Erro HTTP {lote_response.status_code}")
            print(f"Response text: {lote_response.text[:500]}...")  # Primeiros 500 chars
            return False
            
    except Exception as e:
        print(f"❌ Erro na execução do teste: {e}")
        return False

def testar_validacao_arquivo():
    """Testa apenas a validação de arquivo"""
    
    # Dados de login
    login_data = {
        "username": "admin",
        "password": "Admin123!"
    }
    
    try:
        session = requests.Session()
        
        print("\n🔍 Testando validação de arquivo...")
        
        # Login
        login_response = session.post(LOGIN_URL, data=login_data)
        if login_response.status_code != 200:
            print("❌ Erro no login para validação")
            return False
        
        # Preparar arquivo
        csv_file = criar_csv_teste()
        
        files = {
            'arquivo': ('teste_validacao.csv', csv_file, 'text/csv')
        }
        
        # Testar validação
        validacao_response = session.post(
            f"{BASE_URL}/ctes/api/validar-arquivo",
            files=files
        )
        
        print(f"Validação status: {validacao_response.status_code}")
        
        if validacao_response.status_code == 200:
            response_data = validacao_response.json()
            print("✅ Validação OK:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ Erro na validação: {validacao_response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DE ATUALIZAÇÃO EM LOTE")
    print("=" * 60)
    
    # Teste 1: Validação de arquivo
    validacao_ok = testar_validacao_arquivo()
    
    # Teste 2: Atualização em lote
    lote_ok = testar_atualizacao_lote()
    
    print("=" * 60)
    print("📊 RESULTADO DOS TESTES:")
    print(f"  VALIDAÇÃO     {'✅ PASSOU' if validacao_ok else '❌ FALHOU'}")
    print(f"  LOTE          {'✅ PASSOU' if lote_ok else '❌ FALHOU'}")
    
    if validacao_ok and lote_ok:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema de lote funcionando.")
    else:
        print("❌ ALGUNS TESTES FALHARAM! Verificar implementação.")
