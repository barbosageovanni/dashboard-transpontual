#!/usr/bin/env python3

import requests
import io
import pandas as pd

def test_complete_fields():
    """Testa se todos os campos podem ser atualizados via CSV e Excel."""
    
    base_url = "http://localhost:5000"
    
    # Login
    session = requests.Session()
    login_data = {"email": "admin@admin.com", "password": "senha123"}
    session.post(f"{base_url}/auth/login", data=login_data)
    
    # Dados de teste com todos os campos
    test_data = {
        "Número CTE": [12345, 12346],
        "Destinatário": ["Cliente Teste A", "Cliente Teste B"], 
        "Placa Veículo": ["ABC-1234", "XYZ-5678"],
        "Valor Total": [1500.50, 2300.75],
        "Data Emissão": ["2025-01-15", "2025-01-16"],
        "Data Baixa": ["2025-01-20", "2025-01-21"],
        "Número Fatura": ["FAT001", "FAT002"],
        "Data Inclusão Fatura": ["2025-01-22", "2025-01-23"],
        "Data Envio Processo": ["2025-01-25", "2025-01-26"],
        "Primeiro Envio": ["2025-01-26", "2025-01-27"],
        "Data RQ/TMC": ["2025-01-28", "2025-01-29"],
        "Data Atesto": ["2025-01-30", "2025-01-31"],
        "Envio Final": ["2025-02-01", "2025-02-02"],
        "Observação": ["Teste CSV", "Teste Excel"],
        "Origem dos Dados": ["Sistema Teste", "Sistema Teste"]
    }
    
    print("🧪 TESTE CAMPOS COMPLETOS - ATUALIZAÇÃO EM LOTE")
    print("="*70)
    
    # Teste CSV com todos os campos
    print("📄 Testando CSV com todos os campos...")
    df = pd.DataFrame(test_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8')
    csv_content = csv_buffer.getvalue().encode('utf-8')
    
    files = {'arquivo': ('test_complete.csv', io.BytesIO(csv_content), 'text/csv')}
    data = {'modo': 'upsert'}
    
    response = session.post(f"{base_url}/ctes/api/atualizar-lote", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
    print(f"Response text: {response.text[:200]}...")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"✅ CSV processado: {result.get('processados', 0)} registros")
            print(f"   Inseridos: {result.get('inseridos', 0)}")
            print(f"   Atualizados: {result.get('atualizados', 0)}")
            print(f"   Erros: {result.get('erros', 0)}")
        except Exception as e:
            print(f"❌ Erro ao parsear JSON: {e}")
    else:
        print(f"❌ Erro CSV: {response.status_code}")
        print(response.text)
    
    print("\n📊 Testando Excel com todos os campos...")
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    files = {'arquivo': ('test_complete.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    data = {'modo': 'upsert'}
    
    response = session.post(f"{base_url}/ctes/api/atualizar-lote", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Excel processado: {result.get('processados', 0)} registros")
        print(f"   Inseridos: {result.get('inseridos', 0)}")
        print(f"   Atualizados: {result.get('atualizados', 0)}")
        print(f"   Erros: {result.get('erros', 0)}")
    else:
        print(f"❌ Erro Excel: {response.status_code}")
        print(response.text)
    
    print("\n🎯 Teste de campos completos finalizado!")

if __name__ == "__main__":
    try:
        test_complete_fields()
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
