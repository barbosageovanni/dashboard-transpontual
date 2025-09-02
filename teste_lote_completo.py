#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo da atualização em lote - CSV e Excel
teste_lote_completo.py
"""

import requests
import json
import io
import pandas as pd
from datetime import date

# Configurações
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
LOTE_URL = f"{BASE_URL}/ctes/api/atualizar-lote"
VALIDACAO_URL = f"{BASE_URL}/ctes/api/validar-arquivo"

def criar_csv_completo():
    """Cria um CSV com TODOS os campos disponíveis"""
    csv_content = """Número CTE,Cliente,Placa Veículo,Valor Total,Data Emissão,Data Baixa,Número Fatura,Data Inclusão Fatura,Data Envio Processo,Primeiro Envio,Data RQ/TMC,Data Atesto,Envio Final,Observação,Origem dos Dados
555001,Cliente Teste 1,ABC-1111,1500.50,2025-08-23,2025-08-25,FAT-001,2025-08-24,2025-08-26,2025-08-27,2025-08-28,2025-08-29,2025-08-30,Teste completo CSV,Sistema
555002,Cliente Teste 2,XYZ-2222,2750.75,2025-08-23,,FAT-002,2025-08-24,,,,,,"Em processamento",Sistema
555003,Cliente Teste 3,DEF-3333,999.99,2025-08-23,,,,,,,,,Apenas emitido,Importação
"""
    return io.BytesIO(csv_content.encode('utf-8'))

def criar_excel_completo():
    """Cria um arquivo Excel com TODOS os campos disponíveis"""
    data = {
        'Número CTE': [666001, 666002, 666003],
        'Cliente': ['Cliente Excel 1', 'Cliente Excel 2', 'Cliente Excel 3'],
        'Placa Veículo': ['ABC-1111', 'XYZ-2222', 'DEF-3333'],
        'Valor Total': [1800.50, 3200.75, 1200.00],
        'Data Emissão': ['2025-08-23', '2025-08-23', '2025-08-23'],
        'Data Baixa': ['2025-08-25', '', ''],
        'Número Fatura': ['FAT-E001', 'FAT-E002', ''],
        'Data Inclusão Fatura': ['2025-08-24', '2025-08-24', ''],
        'Data Envio Processo': ['2025-08-26', '', ''],
        'Primeiro Envio': ['2025-08-27', '', ''],
        'Data RQ/TMC': ['2025-08-28', '', ''],
        'Data Atesto': ['2025-08-29', '', ''],
        'Envio Final': ['2025-08-30', '', ''],
        'Observação': ['Teste completo Excel', 'Em processamento Excel', 'Apenas emitido Excel'],
        'Origem dos Dados': ['Sistema', 'Sistema', 'Importação']
    }
    
    df = pd.DataFrame(data)
    
    # Salvar em buffer de memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='CTEs')
    
    buffer.seek(0)
    return buffer

def fazer_login():
    """Faz login e retorna a sessão"""
    session = requests.Session()
    
    login_data = {
        "username": "admin",
        "password": "Admin123!"
    }
    
    login_response = session.post(LOGIN_URL, data=login_data)
    if login_response.status_code == 200:
        return session
    else:
        raise Exception(f"Erro no login: {login_response.status_code}")

def testar_validacao(session, arquivo, nome_arquivo, tipo):
    """Testa a validação de um arquivo"""
    print(f"\n🔍 Testando validação {tipo}...")
    
    files = {
        'arquivo': (nome_arquivo, arquivo, 'application/octet-stream')
    }
    
    validacao_response = session.post(VALIDACAO_URL, files=files)
    
    print(f"Validação {tipo} status: {validacao_response.status_code}")
    
    if validacao_response.status_code == 200:
        response_data = validacao_response.json()
        print(f"✅ Validação {tipo} OK:")
        print(f"  - Linhas: {response_data.get('linhas', 0)}")
        print(f"  - Colunas: {len(response_data.get('colunas', []))}")
        print(f"  - Campos: {', '.join(response_data.get('colunas', [])[:5])}...")
        return True
    else:
        print(f"❌ Erro na validação {tipo}:")
        print(f"  {validacao_response.text[:200]}...")
        return False

def testar_processamento(session, arquivo, nome_arquivo, tipo):
    """Testa o processamento de um arquivo"""
    print(f"\n📤 Testando processamento {tipo}...")
    
    files = {
        'arquivo': (nome_arquivo, arquivo, 'application/octet-stream')
    }
    
    data = {
        'modo': 'upsert'
    }
    
    lote_response = session.post(LOTE_URL, files=files, data=data)
    
    print(f"Processamento {tipo} status: {lote_response.status_code}")
    
    if lote_response.status_code == 200:
        response_data = lote_response.json()
        print(f"✅ Processamento {tipo} OK:")
        print(f"  - Processados: {response_data.get('processados', 0)}")
        print(f"  - Inseridos: {response_data.get('inseridos', 0)}")
        print(f"  - Atualizados: {response_data.get('atualizados', 0)}")
        print(f"  - Erros: {response_data.get('erros', 0)}")
        
        # Mostrar alguns detalhes
        detalhes = response_data.get('detalhes', [])
        if detalhes:
            print(f"  - Primeiros resultados:")
            for i, detalhe in enumerate(detalhes[:3]):
                status = "✅" if detalhe.get('sucesso') else "❌"
                print(f"    {status} CTE {detalhe.get('cte')}: {detalhe.get('mensagem')}")
        
        return response_data.get('sucesso', False)
    else:
        print(f"❌ Erro no processamento {tipo}:")
        print(f"  {lote_response.text[:200]}...")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE COMPLETO - ATUALIZAÇÃO EM LOTE")
    print("=" * 70)
    
    try:
        # 1. Fazer login
        print("🔑 Fazendo login...")
        session = fazer_login()
        print("✅ Login realizado com sucesso!")
        
        # 2. Testar CSV
        print("\n" + "="*50)
        print("📄 TESTANDO ARQUIVO CSV")
        print("="*50)
        
        csv_arquivo = criar_csv_completo()
        csv_validacao_ok = testar_validacao(session, csv_arquivo, 'teste_completo.csv', 'CSV')
        
        csv_arquivo.seek(0)  # Reset do buffer
        csv_processamento_ok = testar_processamento(session, csv_arquivo, 'teste_completo.csv', 'CSV')
        
        # 3. Testar Excel
        print("\n" + "="*50)
        print("📊 TESTANDO ARQUIVO EXCEL")
        print("="*50)
        
        excel_arquivo = criar_excel_completo()
        excel_validacao_ok = testar_validacao(session, excel_arquivo, 'teste_completo.xlsx', 'Excel')
        
        excel_arquivo.seek(0)  # Reset do buffer  
        excel_processamento_ok = testar_processamento(session, excel_arquivo, 'teste_completo.xlsx', 'Excel')
        
        # 4. Resultado final
        print("\n" + "="*70)
        print("📊 RESULTADO FINAL DOS TESTES:")
        print("="*70)
        
        resultados = {
            "CSV - Validação": csv_validacao_ok,
            "CSV - Processamento": csv_processamento_ok,
            "Excel - Validação": excel_validacao_ok,
            "Excel - Processamento": excel_processamento_ok
        }
        
        for teste, resultado in resultados.items():
            status = "✅ PASSOU" if resultado else "❌ FALHOU"
            print(f"  {teste:<25} {status}")
        
        total_sucessos = sum(resultados.values())
        total_testes = len(resultados)
        
        print(f"\n🎯 RESULTADO GERAL: {total_sucessos}/{total_testes} testes passaram")
        
        if total_sucessos == total_testes:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema de lote 100% funcional.")
        else:
            print("⚠️ Alguns testes falharam. Verificar implementação.")
            
    except Exception as e:
        print(f"❌ Erro na execução dos testes: {e}")

if __name__ == "__main__":
    main()
