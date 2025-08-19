#!/usr/bin/env python3
"""
Script de teste para verificar se a API de análise financeira está funcionando
"""

import requests
import json
from datetime import datetime

def testar_api_local():
    """Testa a API de análise financeira localmente"""
    
    print("🔍 Testando API de Análise Financeira...")
    print("=" * 50)
    
    # URL base
    base_url = "http://localhost:5000"
    
    # Testar conexão básica
    try:
        print("1️⃣ Testando conexão básica...")
        response = requests.get(base_url, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Servidor respondendo")
        else:
            print("   ❌ Erro na conexão")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # Testar página de análise financeira (pode redirecionar para login)
    try:
        print("\n2️⃣ Testando página de análise financeira...")
        response = requests.get(f"{base_url}/analise-financeira", timeout=5)
        print(f"   Status: {response.status_code}")
        if "login" in response.url.lower():
            print("   ⚠️ Redirecionado para login - precisa autenticação")
        elif response.status_code == 200:
            print("   ✅ Página carregada com sucesso")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar API diretamente (pode falhar por autenticação)
    try:
        print("\n3️⃣ Testando API de análise completa...")
        api_url = f"{base_url}/analise-financeira/api/analise-completa?filtro_dias=180"
        response = requests.get(api_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ API funcionando!")
                print(f"   📊 CTEs encontrados: {data['analise']['resumo_filtro']['total_ctes']}")
                receita = data['analise']['receita_mensal']['receita_mes_corrente']
                print(f"   💰 Receita atual: R$ {receita:,.2f}")
            else:
                print(f"   ❌ API retornou erro: {data.get('error')}")
        elif response.status_code == 302:
            print("   ⚠️ Redirecionamento - provavelmente precisa de login")
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Diagnóstico:")
    print("   - Se vê 'Redirecionado para login': faça login no navegador primeiro")
    print("   - Se vê 'API funcionando': o problema pode estar no JavaScript")
    print("   - Se vê erros de conexão: verifique se o servidor está rodando")

if __name__ == "__main__":
    testar_api_local()
