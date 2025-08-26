#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DAS APIs - Dashboard e CTEs
Execute este script para testar se as APIs estão funcionando
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "senha123"  # Baseado na mensagem do servidor

def testar_apis():
    """Testa todas as APIs do sistema"""
    print("=" * 60)
    print("🔍 TESTANDO APIs - Dashboard e CTEs")
    print("=" * 60)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login
    print("\n1️⃣ FAZENDO LOGIN...")
    login_success = fazer_login(session)
    
    if not login_success:
        print("❌ Não foi possível fazer login. Parando testes.")
        return
    
    # 2. Testar API de debug do dashboard
    print("\n2️⃣ TESTANDO API DE DEBUG DASHBOARD...")
    testar_dashboard_debug(session)
    
    # 3. Testar API de métricas
    print("\n3️⃣ TESTANDO API DE MÉTRICAS...")
    testar_dashboard_metricas(session)
    
    # 4. Testar API de listagem de CTEs
    print("\n4️⃣ TESTANDO API DE CTEs...")
    testar_ctes_api(session)
    
    # 5. Testar APIs de debug de CTEs
    print("\n5️⃣ TESTANDO API DE DEBUG CTEs...")
    testar_ctes_debug(session)
    
    print("\n" + "=" * 60)
    print("🏁 TESTE DE APIs CONCLUÍDO")
    print("=" * 60)

def fazer_login(session):
    """Faz login no sistema"""
    try:
        # Primeiro, pegar a página de login para obter CSRF token se necessário
        login_page = session.get(f"{BASE_URL}/auth/login")
        
        if login_page.status_code != 200:
            print(f"❌ Erro ao acessar página de login: {login_page.status_code}")
            return False
        
        # Tentar fazer login
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect após login bem-sucedido
            print("✅ Login realizado com sucesso")
            return True
        elif response.status_code == 200:
            if "login" in response.text.lower() and "erro" in response.text.lower():
                print("❌ Erro de credenciais")
                print(f"   Tentou: {USERNAME}/{PASSWORD}")
                print("   Verifique se as credenciais estão corretas")
                return False
            else:
                print("✅ Login possivelmente bem-sucedido (status 200)")
                return True
        else:
            print(f"❌ Erro no login: status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return False

def testar_dashboard_debug(session):
    """Testa API de debug do dashboard"""
    try:
        response = session.get(f"{BASE_URL}/dashboard/api/debug")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    debug_info = data.get('debug', {})
                    print("✅ API Debug Dashboard funcionando")
                    print(f"   Total CTEs no DB: {debug_info.get('total_ctes_db', 'N/A')}")
                    print(f"   Exemplos: {len(debug_info.get('exemplos', []))}")
                    print(f"   Métricas Service: {debug_info.get('metricas_service_available', 'N/A')}")
                else:
                    print("❌ API Debug retornou success=False")
                    print(f"   Erro: {data.get('error', 'Desconhecido')}")
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
                print(f"   Conteúdo: {response.text[:200]}...")
        else:
            print(f"❌ Erro na API Debug: {response.status_code}")
            print(f"   Conteúdo: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard debug: {e}")

def testar_dashboard_metricas(session):
    """Testa API de métricas do dashboard"""
    try:
        response = session.get(f"{BASE_URL}/dashboard/api/metricas")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    metricas = data.get('metricas', {})
                    print("✅ API Métricas Dashboard funcionando")
                    print(f"   Total CTEs: {metricas.get('total_ctes', 0)}")
                    print(f"   Valor Total: R$ {metricas.get('valor_total', 0):,.2f}")
                    print(f"   Clientes Únicos: {metricas.get('clientes_unicos', 0)}")
                    print(f"   Faturas Pagas: {metricas.get('faturas_pagas', 0)}")
                    print(f"   Total Registros Processados: {data.get('total_registros', 0)}")
                    
                    # Verificar se há alertas
                    alertas = data.get('alertas', {})
                    total_alertas = sum(alerta.get('qtd', 0) for alerta in alertas.values())
                    print(f"   Total Alertas: {total_alertas}")
                    
                else:
                    print("❌ API Métricas retornou success=False")
                    print(f"   Erro: {data.get('error', 'Desconhecido')}")
                    
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
                print(f"   Conteúdo: {response.text[:200]}...")
        else:
            print(f"❌ Erro na API Métricas: {response.status_code}")
            if response.status_code == 302:
                print("   → Redirecionamento detectado - problema de autenticação?")
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard métricas: {e}")

def testar_ctes_api(session):
    """Testa API de listagem de CTEs"""
    try:
        response = session.get(f"{BASE_URL}/ctes/api/listar?per_page=10")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    ctes = data.get('ctes', [])
                    pagination = data.get('pagination', {})
                    print("✅ API Listagem CTEs funcionando")
                    print(f"   CTEs retornados: {len(ctes)}")
                    print(f"   Total no banco: {pagination.get('total', 0)}")
                    print(f"   Página atual: {pagination.get('current_page', 'N/A')}")
                    
                    # Mostrar exemplo de CTE se houver
                    if ctes:
                        primeiro_cte = ctes[0]
                        print(f"   Exemplo - CTE: {primeiro_cte.get('numero_cte', 'N/A')}")
                        print(f"   Exemplo - Cliente: {primeiro_cte.get('destinatario_nome', 'N/A')}")
                        print(f"   Exemplo - Valor: R$ {primeiro_cte.get('valor_total', 0)}")
                else:
                    print("❌ API CTEs retornou success=False")
                    print(f"   Erro: {data.get('error', 'Desconhecido')}")
                    
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
                print(f"   Conteúdo: {response.text[:200]}...")
        else:
            print(f"❌ Erro na API CTEs: {response.status_code}")
            if response.status_code == 302:
                print("   → Redirecionamento detectado - problema de autenticação?")
                
    except Exception as e:
        print(f"❌ Erro ao testar CTEs API: {e}")

def testar_ctes_debug(session):
    """Testa API de debug dos CTEs"""
    try:
        response = session.get(f"{BASE_URL}/ctes/api/debug")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    sistema = data.get('sistema', {})
                    print("✅ API Debug CTEs funcionando")
                    print(f"   Total CTEs: {sistema.get('total_ctes', 0)}")
                    print(f"   Tabela: {sistema.get('tabela', 'N/A')}")
                    print(f"   Modelo Funcional: {sistema.get('modelo_funcional', False)}")
                    
                    servicos = sistema.get('servicos', {})
                    print(f"   Serviço Importação: {servicos.get('importacao', False)}")
                    print(f"   Serviço Atualização: {servicos.get('atualizacao', False)}")
                else:
                    print("❌ API Debug CTEs retornou success=False")
                    print(f"   Erro: {data.get('error', 'Desconhecido')}")
                    
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
                print(f"   Conteúdo: {response.text[:200]}...")
        else:
            print(f"❌ Erro na API Debug CTEs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar CTEs debug: {e}")

def testar_conexao_simples():
    """Teste básico de conexão"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor respondendo na porta 5000")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Servidor não está respondendo: {e}")
        return False

if __name__ == "__main__":
    print(f"🔗 Testando conexão com {BASE_URL}...")
    
    if not testar_conexao_simples():
        print("\n❌ Servidor não está rodando ou não está acessível")
        print("   Execute: python run.py")
        exit(1)
    
    print("✅ Servidor está rodando\n")
    testar_apis()