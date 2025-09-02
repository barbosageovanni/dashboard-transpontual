#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo CRUD de CTEs via API
teste_crud_completo.py
"""

import requests
import json
from datetime import date

# Configurações
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
LISTAR_URL = f"{BASE_URL}/ctes/api/listar"
INSERIR_URL = f"{BASE_URL}/ctes/api/inserir"
BUSCAR_URL = f"{BASE_URL}/ctes/api/buscar"
ATUALIZAR_URL = f"{BASE_URL}/ctes/api/atualizar"
EXCLUIR_URL = f"{BASE_URL}/ctes/api/excluir"

# Número de CTE para teste
NUMERO_TESTE = 888888

def fazer_login():
    """Faz login e retorna a sessão"""
    session = requests.Session()
    
    login_data = {
        "username": "admin",
        "password": "Admin123!"
    }
    
    print("🔑 Fazendo login...")
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_listar(session):
    """Testa a listagem de CTEs"""
    print("\n📋 Testando LISTAGEM...")
    
    try:
        response = session.get(LISTAR_URL)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listagem OK - {data.get('total', 0)} CTEs encontrados")
            return True
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def testar_inserir(session):
    """Testa a inserção de CTE"""
    print("\n➕ Testando INSERÇÃO...")
    
    cte_data = {
        "numero_cte": NUMERO_TESTE,
        "destinatario_nome": "TESTE CRUD COMPLETO",
        "veiculo_placa": "TST-2024",
        "valor_total": 2500.00,
        "data_emissao": str(date.today()),
        "observacao": "CTE criado para teste CRUD completo"
    }
    
    try:
        response = session.post(INSERIR_URL, json=cte_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Inserção OK - CTE {NUMERO_TESTE} criado")
                return True
            else:
                print(f"❌ Erro na inserção: {data.get('message')}")
                return False
        else:
            print(f"❌ Erro na inserção: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na inserção: {e}")
        return False

def testar_buscar(session):
    """Testa a busca de CTE"""
    print("\n🔍 Testando BUSCA...")
    
    try:
        response = session.get(f"{BUSCAR_URL}/{NUMERO_TESTE}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cte = data.get('cte')
                print(f"✅ Busca OK - CTE {NUMERO_TESTE}: {cte.get('destinatario_nome')}")
                return True
            else:
                print(f"❌ Erro na busca: {data.get('message')}")
                return False
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return False

def testar_atualizar(session):
    """Testa a atualização de CTE"""
    print("\n✏️ Testando ATUALIZAÇÃO...")
    
    update_data = {
        "destinatario_nome": "TESTE CRUD ATUALIZADO",
        "valor_total": 3000.00,
        "observacao": "CTE atualizado no teste CRUD"
    }
    
    try:
        response = session.put(f"{ATUALIZAR_URL}/{NUMERO_TESTE}", json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Atualização OK - CTE {NUMERO_TESTE} atualizado")
                return True
            else:
                print(f"❌ Erro na atualização: {data.get('message')}")
                return False
        else:
            print(f"❌ Erro na atualização: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na atualização: {e}")
        return False

def testar_excluir(session):
    """Testa a exclusão de CTE"""
    print("\n🗑️ Testando EXCLUSÃO...")
    
    try:
        response = session.delete(f"{EXCLUIR_URL}/{NUMERO_TESTE}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Exclusão OK - CTE {NUMERO_TESTE} excluído")
                return True
            else:
                print(f"❌ Erro na exclusão: {data.get('message')}")
                return False
        else:
            print(f"❌ Erro na exclusão: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na exclusão: {e}")
        return False

def main():
    """Executa todos os testes CRUD"""
    print("🧪 TESTE CRUD COMPLETO - CTEs")
    print("=" * 60)
    
    # Fazer login
    session = fazer_login()
    if not session:
        print("❌ Não foi possível fazer login. Abortando testes.")
        return
    
    # Executar testes
    resultados = {}
    
    resultados['listar'] = testar_listar(session)
    resultados['inserir'] = testar_inserir(session)
    resultados['buscar'] = testar_buscar(session)
    resultados['atualizar'] = testar_atualizar(session)
    resultados['excluir'] = testar_excluir(session)
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES:")
    
    total_testes = len(resultados)
    testes_passaram = sum(1 for passou in resultados.values() if passou)
    
    for operacao, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"  {operacao.upper():12} {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! CRUD funcionando 100%")
    else:
        print("⚠️ Alguns testes falharam. Verificar implementação.")

if __name__ == "__main__":
    main()
