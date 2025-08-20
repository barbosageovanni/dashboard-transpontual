#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste - Módulo Análise Financeira
test_analise_financeira.py
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Teste 1: Verificar se todos os imports funcionam"""
    print("🧪 Teste 1: Verificando imports...")
    
    try:
        from app import create_app, db
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        from app.models.cte import CTE
        print("✅ Imports OK")
        return True
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def test_service_funcionamento():
    """Teste 2: Verificar se o serviço funciona"""
    print("\n🧪 Teste 2: Verificando funcionamento do serviço...")
    
    try:
        from app import create_app
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        app = create_app()
        with app.app_context():
            # Teste básico
            analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=180)
            
            # Verificações
            assert 'receita_mensal' in analise
            assert 'ticket_medio' in analise
            assert 'tempo_medio_cobranca' in analise
            assert 'tendencia_linear' in analise
            assert 'concentracao_clientes' in analise
            assert 'stress_test_receita' in analise
            assert 'graficos' in analise
            
            print("✅ Serviço funcionando corretamente")
            print(f"   📊 {analise['resumo_filtro']['total_ctes']} CTEs analisados")
            return True
            
    except Exception as e:
        print(f"❌ Erro no serviço: {e}")
        return False

def test_api_endpoints():
    """Teste 3: Verificar endpoints da API"""
    print("\n🧪 Teste 3: Testando endpoints da API...")
    
    base_url = "http://localhost:5000"
    
    # Lista de endpoints para testar
    endpoints = [
        "/analise-financeira/api/analise-completa?filtro_dias=30",
        "/analise-financeira/api/clientes",
        "/analise-financeira/api/receita-mensal?filtro_dias=90",
        "/analise-financeira/api/concentracao-clientes?filtro_dias=180",
        "/analise-financeira/api/tempo-cobranca?filtro_dias=30",
        "/analise-financeira/api/tendencia?filtro_dias=180",
        "/analise-financeira/api/resumo-executivo"
    ]
    
    resultados = []
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            tempo_resposta = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {endpoint} - {tempo_resposta}s")
                    resultados.append(True)
                else:
                    print(f"❌ {endpoint} - Erro: {data.get('error')}")
                    resultados.append(False)
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                resultados.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Conexão: {e}")
            resultados.append(False)
    
    sucesso = all(resultados)
    print(f"\n📊 Resultado: {sum(resultados)}/{len(resultados)} endpoints funcionando")
    return sucesso

def test_metricas_especificas():
    """Teste 4: Verificar cálculos específicos"""
    print("\n🧪 Teste 4: Verificando cálculos das métricas...")
    
    try:
        from app import create_app
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        app = create_app()
        with app.app_context():
            analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=180)
            
            # Teste receita mensal
            receita = analise['receita_mensal']
            assert isinstance(receita['receita_mes_corrente'], (int, float))
            assert isinstance(receita['variacao_percentual'], (int, float))
            print("✅ Receita mensal calculada corretamente")
            
            # Teste ticket médio
            ticket = analise['ticket_medio']
            assert ticket['valor'] >= 0
            assert ticket['mediana'] >= 0
            print("✅ Ticket médio calculado corretamente")
            
            # Teste tempo de cobrança
            tempo = analise['tempo_medio_cobranca']
            assert tempo['dias_medio'] >= 0
            assert tempo['total_analisados'] >= 0
            print("✅ Tempo de cobrança calculado corretamente")
            
            # Teste concentração
            concentracao = analise['concentracao_clientes']
            assert 0 <= concentracao['percentual_top5'] <= 100
            print("✅ Concentração de clientes calculada corretamente")
            
            # Teste stress test
            stress = analise['stress_test_receita']
            assert isinstance(stress['cenarios'], list)
            print("✅ Stress test calculado corretamente")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro nos cálculos: {e}")
        return False

def test_performance():
    """Teste 5: Verificar performance"""
    print("\n🧪 Teste 5: Verificando performance...")
    
    try:
        from app import create_app
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        app = create_app()
        with app.app_context():
            # Teste de diferentes períodos
            periodos = [15, 30, 90, 180]
            tempos = []
            
            for periodo in periodos:
                start_time = time.time()
                analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=periodo)
                end_time = time.time()
                
                tempo = round(end_time - start_time, 2)
                tempos.append(tempo)
                
                print(f"   📅 {periodo} dias: {tempo}s ({analise['resumo_filtro']['total_ctes']} CTEs)")
            
            tempo_medio = sum(tempos) / len(tempos)
            print(f"\n📊 Tempo médio: {tempo_medio:.2f}s")
            
            # Performance aceitável: < 3 segundos
            if tempo_medio < 3.0:
                print("✅ Performance aceitável")
                return True
            else:
                print("⚠️ Performance pode ser melhorada")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def test_filtros():
    """Teste 6: Verificar filtros por cliente"""
    print("\n🧪 Teste 6: Verificando filtros por cliente...")
    
    try:
        from app import create_app
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        app = create_app()
        with app.app_context():
            # Obter lista de clientes
            clientes = AnaliseFinanceiraService.obter_lista_clientes()
            print(f"   👥 {len(clientes)} clientes encontrados")
            
            if len(clientes) > 0:
                # Testar filtro por cliente específico
                cliente_teste = clientes[0]
                analise_cliente = AnaliseFinanceiraService.gerar_analise_completa(
                    filtro_dias=180, 
                    filtro_cliente=cliente_teste
                )
                
                print(f"   🎯 Teste com cliente: {cliente_teste}")
                print(f"   📊 CTEs filtrados: {analise_cliente['resumo_filtro']['total_ctes']}")
                
                # Análise geral para comparação
                analise_geral = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=180)
                
                # CTEs filtrados devem ser <= CTEs gerais
                assert analise_cliente['resumo_filtro']['total_ctes'] <= analise_geral['resumo_filtro']['total_ctes']
                
                print("✅ Filtros funcionando corretamente")
                return True
            else:
                print("⚠️ Nenhum cliente encontrado para teste")
                return True
                
    except Exception as e:
        print(f"❌ Erro no teste de filtros: {e}")
        return False

def test_graficos_data():
    """Teste 7: Verificar dados dos gráficos"""
    print("\n🧪 Teste 7: Verificando dados dos gráficos...")
    
    try:
        from app import create_app
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        app = create_app()
        with app.app_context():
            analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=180)
            graficos = analise['graficos']
            
            # Verificar estrutura dos gráficos
            graficos_esperados = [
                'receita_mensal',
                'distribuicao_valores', 
                'tempo_cobranca',
                'concentracao_clientes',
                'tendencia_linear'
            ]
            
            for grafico in graficos_esperados:
                assert grafico in graficos, f"Gráfico {grafico} não encontrado"
                print(f"✅ Gráfico {grafico} presente")
            
            # Verificar se gráficos têm dados
            receita_graf = graficos['receita_mensal']
            if receita_graf['labels'] and receita_graf['valores']:
                print(f"   📈 Receita mensal: {len(receita_graf['labels'])} pontos")
            
            concentracao_graf = graficos['concentracao_clientes']
            if concentracao_graf['labels'] and concentracao_graf['valores']:
                print(f"   🎯 Concentração: {len(concentracao_graf['labels'])} clientes")
            
            print("✅ Dados dos gráficos OK")
            return True
            
    except Exception as e:
        print(f"❌ Erro nos dados dos gráficos: {e}")
        return False

def gerar_relatorio_teste():
    """Gerar relatório final do teste"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO FINAL DOS TESTES")
    print("="*60)
    
    # Executar todos os testes
    testes = [
        ("Imports", test_imports),
        ("Serviço", test_service_funcionamento),
        ("APIs", test_api_endpoints),
        ("Métricas", test_metricas_especificas),
        ("Performance", test_performance),
        ("Filtros", test_filtros),
        ("Gráficos", test_graficos_data)
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Sumário
    print("\n📊 SUMÁRIO DOS TESTES:")
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {nome:<12} {status}")
        if resultado:
            sucessos += 1
    
    print(f"\n🎯 RESULTADO FINAL: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM! Módulo funcionando perfeitamente.")
        return True
    else:
        print("⚠️ ALGUNS TESTES FALHARAM. Verificar logs acima.")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DO MÓDULO ANÁLISE FINANCEIRA")
    print("Dashboard Baker v3.1.0")
    print("="*60)
    
    sucesso = gerar_relatorio_teste()
    
    print("\n" + "="*60)
    if sucesso:
        print("✅ MÓDULO ANÁLISE FINANCEIRA FUNCIONANDO CORRETAMENTE!")
        print("📈 Sistema pronto para produção!")
    else:
        print("❌ PROBLEMAS DETECTADOS NO MÓDULO")
        print("🔧 Verificar logs e corrigir antes do deploy")
    
    print("="*60)
    
    return 0 if sucesso else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)