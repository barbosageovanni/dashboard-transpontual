#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG: Investigação da API faturamento-inclusao
PROBLEMA: API retornando estrutura de dados diferente da esperada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_api_faturamento():
    """Debug da API de faturamento por inclusão"""
    
    print("🔍 DEBUG DA API FATURAMENTO POR INCLUSÃO")
    print("=" * 60)
    
    try:
        from app import create_app, db
        from app.models.cte import CTE
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        from datetime import datetime, timedelta
        
        app = create_app()
        
        with app.app_context():
            
            # 1. VERIFICAR SE A FUNÇÃO EXISTS
            print("1. VERIFICANDO FUNÇÃO...")
            
            if hasattr(AnaliseFinanceiraService, 'obter_faturamento_por_inclusao'):
                print("✅ Função obter_faturamento_por_inclusao existe")
                
                # 2. TESTAR FUNÇÃO DIRETAMENTE
                print("\n2. TESTANDO FUNÇÃO DIRETAMENTE...")
                
                resultado = AnaliseFinanceiraService.obter_faturamento_por_inclusao(30)
                
                print("Tipo do resultado:", type(resultado))
                print("Chaves do resultado:", list(resultado.keys()) if isinstance(resultado, dict) else "Não é dict")
                
                # Mostrar estrutura completa
                print("\nESTRUTURA COMPLETA DO RESULTADO:")
                print("-" * 40)
                
                if isinstance(resultado, dict):
                    for key, value in resultado.items():
                        print(f"{key}: {value} (tipo: {type(value)})")
                else:
                    print("Resultado não é um dicionário:", resultado)
                    
                # 3. COMPARAR COM O ESPERADO
                print("\n3. VERIFICANDO CAMPOS ESPERADOS...")
                
                campos_esperados = ['faturamento_total', 'quantidade_ctes', 'ticket_medio', 'status']
                campos_encontrados = []
                campos_ausentes = []
                
                if isinstance(resultado, dict):
                    for campo in campos_esperados:
                        if campo in resultado:
                            campos_encontrados.append(campo)
                            print(f"✅ {campo}: {resultado[campo]}")
                        else:
                            campos_ausentes.append(campo)
                            print(f"❌ {campo}: AUSENTE")
                
                print(f"\nResumo: {len(campos_encontrados)}/{len(campos_esperados)} campos corretos")
                
                if campos_ausentes:
                    print(f"Campos ausentes: {campos_ausentes}")
                
                # 4. VERIFICAR SE HÁ CONFLITO COM OUTRAS FUNÇÕES
                print("\n4. VERIFICANDO OUTRAS FUNÇÕES SIMILARES...")
                
                metodos_servico = [m for m in dir(AnaliseFinanceiraService) if not m.startswith('_')]
                funcoes_suspeitas = [m for m in metodos_servico if 'inclusao' in m.lower() or 'faturamento' in m.lower()]
                
                print(f"Métodos do serviço relacionados: {funcoes_suspeitas}")
                
                # 5. VERIFICAR DADOS NO BANCO
                print("\n5. VERIFICANDO DADOS NO BANCO...")
                
                # Total de CTEs
                total_ctes = CTE.query.count()
                print(f"Total CTEs no banco: {total_ctes}")
                
                # CTEs com data_inclusao_fatura
                data_limite = datetime.now().date() - timedelta(days=30)
                ctes_inclusao = CTE.query.filter(
                    CTE.data_inclusao_fatura >= data_limite,
                    CTE.data_inclusao_fatura.isnot(None)
                ).count()
                print(f"CTEs com inclusão (30 dias): {ctes_inclusao}")
                
                # Alguns exemplos
                if ctes_inclusao > 0:
                    exemplos = CTE.query.filter(
                        CTE.data_inclusao_fatura.isnot(None)
                    ).limit(3).all()
                    
                    print("\nExemplos de CTEs com data_inclusao_fatura:")
                    for cte in exemplos:
                        print(f"- CTE {cte.numero_cte}: R$ {cte.valor_total}, inclusão: {cte.data_inclusao_fatura}")
                
            else:
                print("❌ Função obter_faturamento_por_inclusao NÃO EXISTE!")
                
                # Listar funções disponíveis
                metodos = [m for m in dir(AnaliseFinanceiraService) if not m.startswith('_')]
                print(f"Métodos disponíveis: {metodos}")
    
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def testar_rota_diretamente():
    """Testa a rota da API diretamente"""
    
    print("\n" + "=" * 60)
    print("🌐 TESTANDO ROTA DA API DIRETAMENTE")
    print("=" * 60)
    
    try:
        from app import create_app
        from flask import current_app
        
        app = create_app()
        
        with app.app_context():
            with app.test_client() as client:
                
                # Simular login (pode precisar de ajustes)
                print("📡 Enviando requisição para API...")
                
                response = client.get('/analise-financeira/api/faturamento-inclusao?filtro_dias=30')
                
                print(f"Status da resposta: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("\nRESPOSTA DA API:")
                    print("-" * 30)
                    print(f"Success: {data.get('success', 'N/A')}")
                    print(f"Timestamp: {data.get('timestamp', 'N/A')}")
                    
                    if 'dados' in data:
                        print("\nDADOS RETORNADOS:")
                        dados = data['dados']
                        
                        if isinstance(dados, dict):
                            for key, value in dados.items():
                                print(f"  {key}: {value}")
                        else:
                            print(f"  Dados (tipo {type(dados)}): {dados}")
                    
                    if 'error' in data:
                        print(f"\nErro: {data['error']}")
                
                elif response.status_code == 401:
                    print("❌ Erro 401: Não autenticado (esperado em teste)")
                    print("A API requer login, mas o teste confirma que a rota existe")
                    
                else:
                    print(f"❌ Erro HTTP {response.status_code}")
                    print(f"Resposta: {response.get_data(as_text=True)}")
    
    except Exception as e:
        print(f"❌ Erro no teste da rota: {e}")
        import traceback
        traceback.print_exc()

def identificar_funcao_sendo_chamada():
    """Identifica qual função realmente está sendo chamada"""
    
    print("\n" + "=" * 60)
    print("🕵️ IDENTIFICANDO FUNÇÃO SENDO CHAMADA")
    print("=" * 60)
    
    try:
        # Verificar o código da API
        print("📂 Analisando código da API...")
        
        # Simular o que acontece na rota
        filtro_dias = 30
        
        # Isso é o que deveria acontecer:
        print(f"A API deveria chamar: AnaliseFinanceiraService.obter_faturamento_por_inclusao({filtro_dias})")
        
        # Verificar se existe uma função diferente sendo chamada
        from app import create_app
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        app = create_app()
        
        with app.app_context():
            
            # Testar diferentes possibilidades
            funcoes_teste = [
                'obter_faturamento_por_inclusao',
                'gerar_analise_completa',
                '_calcular_receita_por_inclusao_fatura'
            ]
            
            for nome_funcao in funcoes_teste:
                if hasattr(AnaliseFinanceiraService, nome_funcao):
                    print(f"✅ {nome_funcao} existe")
                    
                    try:
                        funcao = getattr(AnaliseFinanceiraService, nome_funcao)
                        
                        if nome_funcao == 'gerar_analise_completa':
                            resultado = funcao(filtro_dias=30)
                        elif nome_funcao.startswith('_'):
                            print(f"   (Função privada - não testando)")
                            continue
                        else:
                            resultado = funcao(30)
                        
                        print(f"   Tipo de retorno: {type(resultado)}")
                        
                        if isinstance(resultado, dict):
                            print(f"   Chaves: {list(resultado.keys())[:5]}...")  # Primeiras 5 chaves
                            
                            # Verificar se tem os campos que aparecem no log
                            campos_suspeitos = ['media_diaria', 'detalhamento_diario', 'receita_por_inclusao_fatura']
                            for campo in campos_suspeitos:
                                if campo in resultado:
                                    print(f"   🔍 Encontrado: {campo} = {resultado[campo]}")
                                elif any(campo in str(k) for k in resultado.keys()):
                                    print(f"   🔍 Similar encontrado em: {[k for k in resultado.keys() if campo in str(k)]}")
                    
                    except Exception as e:
                        print(f"   ❌ Erro ao testar {nome_funcao}: {e}")
                else:
                    print(f"❌ {nome_funcao} NÃO existe")
    
    except Exception as e:
        print(f"❌ Erro na identificação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 INICIANDO DEBUG COMPLETO DA API")
    print("=" * 60)
    
    # 1. Debug da função do serviço
    debug_api_faturamento()
    
    # 2. Teste da rota
    testar_rota_diretamente()
    
    # 3. Identificar função real
    identificar_funcao_sendo_chamada()
    
    print("\n" + "=" * 60)
    print("✅ DEBUG FINALIZADO")
    print("Analise os resultados acima para identificar o problema!")