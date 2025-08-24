#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do sistema de importação em lote
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
    
    # Fazer login
    login_data = {
        "username": username,
        "password": password
    }
    
    response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
    print(f"POST login - Status: {response.status_code}")
    
    if response.status_code in [302]:
        print("✓ Login bem-sucedido!")
        return True
    else:
        print(f"✗ Falha no login")
        return False

def testar_upload_real():
    """Testar upload com CTE real"""
    session = requests.Session()
    
    # Fazer login
    if not fazer_login(session):
        return False
    
    # Criar arquivo CSV de teste com CTE que deve ser criado
    import random
    cte_numero = 90000 + random.randint(1, 9999)  # Gerar número único
    
    csv_content = f"""Número CTE;Destinatário;Placa Veículo;Valor Total;Data Emissão;Data Baixa;Número Fatura;Data Inclusão Fatura;Data Envio Processo;Primeiro Envio;Data RQ/TMC;Data Atesto;Envio Final;Observação;Origem dos Dados
{cte_numero};Teste Importação Real;TST1234;2500.75;15/01/2024;20/01/2024;FAT{cte_numero};16/01/2024;17/01/2024;18/01/2024;19/01/2024;20/01/2024;21/01/2024;Teste de importação real;Teste Sistema"""
    
    print(f"\n=== Testando com CTE {cte_numero} ===")
    
    # Preparar dados do upload
    files = {
        'arquivo': (f'teste_{cte_numero}.csv', csv_content, 'text/csv')
    }
    data = {
        'modo': 'upsert'  # Usar upsert para criar se não existir
    }
    
    print("Fazendo upload do arquivo...")
    response = session.post(UPLOAD_URL, files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            json_response = response.json()
            print("✓ Resposta JSON:")
            print(json_response)
            
            # Verificar se foi inserido
            if json_response.get('inseridos', 0) > 0:
                print(f"✅ CTE {cte_numero} foi INSERIDO no banco!")
                return cte_numero
            elif json_response.get('atualizados', 0) > 0:
                print(f"✅ CTE {cte_numero} foi ATUALIZADO no banco!")
                return cte_numero
            else:
                print("⚠️ CTE não foi inserido nem atualizado")
                return None
                
        except Exception as e:
            print(f"✗ Erro ao fazer parse do JSON: {e}")
            print(f"Raw response: {response.text[:500]}")
            return None
    else:
        print(f"✗ Erro HTTP: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return None

def verificar_cte_no_banco(cte_numero):
    """Verificar se o CTE foi salvo no banco"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from app import create_app, db
    from app.models.cte import CTE
    
    app = create_app()
    with app.app_context():
        cte = CTE.query.filter_by(numero_cte=cte_numero).first()
        if cte:
            print(f"✅ CTE {cte_numero} encontrado no banco!")
            print(f"   Destinatário: {cte.destinatario_nome}")
            print(f"   Valor: R$ {cte.valor_total}")
            print(f"   Placa: {cte.veiculo_placa}")
            return True
        else:
            print(f"❌ CTE {cte_numero} NÃO encontrado no banco!")
            return False

if __name__ == "__main__":
    print("=== Teste Completo de Importação ===")
    
    cte_numero = testar_upload_real()
    
    if cte_numero:
        print(f"\n=== Verificando CTE {cte_numero} no banco ===")
        if verificar_cte_no_banco(cte_numero):
            print("🎉 SUCESSO! O sistema está salvando no banco corretamente!")
        else:
            print("❌ FALHA! O sistema não está salvando no banco!")
    else:
        print("❌ Upload falhou, não é possível verificar o banco")
