#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da Exportação Corrigida - Dashboard Baker Flask
Testa as rotas de exportação CSV e Excel após correções
"""

import requests
import sys
import time
from datetime import datetime

def testar_exportacao():
    """Testa as exportações CSV e Excel"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTE DA EXPORTAÇÃO CORRIGIDA")
    print("=" * 50)
    
    # Session para manter cookies
    session = requests.Session()
    
    try:
        # 1. LOGIN
        print("\n1. 🔑 Fazendo login...")
        login_data = {
            'email': 'admin@transpontual.com',
            'password': 'Admin@2024!'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False
            
        print("✅ Login realizado com sucesso")
        
        # 2. TESTAR DOWNLOAD CSV
        print("\n2. 📋 Testando download CSV...")
        csv_url = f"{base_url}/ctes/api/download/csv"
        
        csv_response = session.get(csv_url)
        print(f"Status CSV: {csv_response.status_code}")
        
        if csv_response.status_code == 200:
            print("✅ Download CSV funcionando")
            print(f"Content-Type: {csv_response.headers.get('Content-Type')}")
            print(f"Content-Disposition: {csv_response.headers.get('Content-Disposition')}")
            
            # Verificar primeiras linhas do CSV
            content = csv_response.content.decode('utf-8')
            linhas = content.split('\n')[:3]  # Primeiras 3 linhas
            print(f"Primeiras linhas do CSV:")
            for i, linha in enumerate(linhas):
                print(f"  Linha {i+1}: {linha[:80]}...")
        else:
            print(f"❌ Erro no download CSV: {csv_response.status_code}")
            print(f"Resposta: {csv_response.text[:200]}")
        
        # 3. TESTAR DOWNLOAD EXCEL
        print("\n3. 📊 Testando download Excel...")
        excel_url = f"{base_url}/ctes/api/download/excel"
        
        excel_response = session.get(excel_url)
        print(f"Status Excel: {excel_response.status_code}")
        
        if excel_response.status_code == 200:
            print("✅ Download Excel funcionando")
            print(f"Content-Type: {excel_response.headers.get('Content-Type')}")
            print(f"Content-Disposition: {excel_response.headers.get('Content-Disposition')}")
            print(f"Tamanho do arquivo: {len(excel_response.content)} bytes")
        else:
            print(f"❌ Erro no download Excel: {excel_response.status_code}")
            print(f"Resposta: {excel_response.text[:200]}")
            
        # 4. TESTAR DOWNLOAD PDF (deve retornar 501)
        print("\n4. 📄 Testando download PDF...")
        pdf_url = f"{base_url}/ctes/api/download/pdf"
        
        pdf_response = session.get(pdf_url)
        print(f"Status PDF: {pdf_response.status_code}")
        
        if pdf_response.status_code == 501:
            print("✅ PDF retorna 501 conforme esperado (não implementado)")
        else:
            print(f"⚠️ PDF não retornou 501: {pdf_response.status_code}")
            
        # 5. TESTAR COM FILTROS
        print("\n5. 🎯 Testando com filtros...")
        filtros = {
            'texto': 'teste',
            'data_inicio': '2024-01-01',
            'data_fim': '2024-12-31'
        }
        
        csv_filtered_response = session.get(csv_url, params=filtros)
        print(f"CSV com filtros: {csv_filtered_response.status_code}")
        
        excel_filtered_response = session.get(excel_url, params=filtros)
        print(f"Excel com filtros: {excel_filtered_response.status_code}")
        
        # RESUMO
        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES:")
        print(f"✅ CSV: {'OK' if csv_response.status_code == 200 else 'ERRO'}")
        print(f"✅ Excel: {'OK' if excel_response.status_code == 200 else 'ERRO'}")
        print(f"✅ PDF: {'OK (501)' if pdf_response.status_code == 501 else 'ERRO'}")
        print(f"✅ Filtros: {'OK' if csv_filtered_response.status_code == 200 else 'ERRO'}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o Flask está rodando em localhost:5000")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_exportacao()
    sys.exit(0 if sucesso else 1)
