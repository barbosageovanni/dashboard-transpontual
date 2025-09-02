#!/usr/bin/env python3

import requests
import io
import pandas as pd

def testar_templates():
    """Testa o download e validação dos templates CSV e Excel."""
    
    base_url = "http://localhost:5000"
    
    # Login
    session = requests.Session()
    login_data = {"email": "admin@admin.com", "password": "senha123"}
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print("❌ Erro no login")
        return False
    
    print("🧪 TESTE DOS TEMPLATES - CSV E EXCEL")
    print("="*50)
    
    # Teste template CSV
    print("📄 Testando template CSV...")
    csv_response = session.get(f"{base_url}/ctes/template-csv")
    
    if csv_response.status_code == 200:
        csv_content = csv_response.text
        print(f"✅ Template CSV baixado ({len(csv_content)} caracteres)")
        print("Conteúdo:")
        lines = csv_content.strip().split('\n')
        for i, line in enumerate(lines):
            print(f"  Linha {i+1}: {line}")
        
        # Verificar se tem dados de exemplo
        if len(lines) >= 2:
            headers = lines[0].split(';')
            dados = lines[1].split(';')
            print(f"✅ Headers: {len(headers)} colunas")
            print(f"✅ Dados exemplo: {len(dados)} campos")
            
            # Verificar se todas as colunas importantes estão presentes
            colunas_obrigatorias = ["Número CTE", "Destinatário", "Valor Total"]
            colunas_presentes = all(col in headers for col in colunas_obrigatorias)
            if colunas_presentes:
                print("✅ Todas as colunas obrigatórias presentes")
            else:
                print("❌ Faltam colunas obrigatórias")
        else:
            print("❌ Template CSV sem dados de exemplo")
    else:
        print(f"❌ Erro ao baixar template CSV: {csv_response.status_code}")
    
    print("\n📊 Testando template Excel...")
    excel_response = session.get(f"{base_url}/ctes/template-excel")
    
    if excel_response.status_code == 200:
        excel_size = len(excel_response.content)
        print(f"✅ Template Excel baixado ({excel_size} bytes)")
        
        # Tentar ler o Excel para verificar se está válido
        try:
            excel_buffer = io.BytesIO(excel_response.content)
            df = pd.read_excel(excel_buffer, sheet_name=0)
            
            print(f"✅ Excel válido: {len(df)} linhas, {len(df.columns)} colunas")
            print("Colunas:", list(df.columns))
            
            if len(df) > 0:
                print("✅ Template Excel contém dados de exemplo")
                print("Primeira linha de exemplo:")
                for col in df.columns:
                    valor = df.iloc[0][col]
                    print(f"  {col}: {valor}")
            else:
                print("⚠️ Template Excel sem dados de exemplo")
                
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {e}")
    else:
        print(f"❌ Erro ao baixar template Excel: {excel_response.status_code}")
    
    print("\n🎯 Teste dos templates concluído!")

if __name__ == "__main__":
    try:
        testar_templates()
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
