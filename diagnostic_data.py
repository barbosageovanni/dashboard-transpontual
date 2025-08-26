#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO E CORREÇÃO DE DADOS - SUPABASE
Identifica e corrige problemas na consulta de dados
"""

import os
import sys
from datetime import datetime
import pandas as pd
from sqlalchemy import text

def diagnostico_dados_completo():
    """Diagnóstico completo dos dados do Supabase"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE DADOS - SUPABASE")
    print("=" * 60)
    
    try:
        from app import create_app, db
        from app.models.cte import CTE
        
        app = create_app()
        
        with app.app_context():
            print("\n1️⃣ TESTANDO MODELO CTE...")
            testar_modelo_cte()
            
            print("\n2️⃣ TESTANDO CONSULTA SQL DIRETA...")
            testar_consulta_sql_direta(db)
            
            print("\n3️⃣ TESTANDO CONVERSÕES DE DADOS...")
            testar_conversoes_dados(db)
            
            print("\n4️⃣ TESTANDO API DASHBOARD...")
            testar_api_dashboard_dados()
            
            print("\n5️⃣ TESTANDO API CTEs...")
            testar_api_ctes_dados()
            
            print("\n6️⃣ CORRIGINDO PROBLEMAS ENCONTRADOS...")
            corrigir_problemas_dados(db)
            
    except Exception as e:
        print(f"❌ Erro crítico no diagnóstico: {e}")
        import traceback
        traceback.print_exc()

def testar_modelo_cte():
    """Testa o modelo CTE do SQLAlchemy"""
    try:
        from app.models.cte import CTE
        
        # Teste básico
        total = CTE.query.count()
        print(f"   Total registros via modelo: {total}")
        
        # Teste de um registro específico
        primeiro = CTE.query.first()
        if primeiro:
            print(f"   Primeiro CTE: {primeiro.numero_cte}")
            print(f"   Destinatário: {primeiro.destinatario_nome}")
            print(f"   Valor total (raw): {primeiro.valor_total}")
            print(f"   Tipo valor_total: {type(primeiro.valor_total)}")
            
            # Testar conversão para float
            try:
                valor_float = float(primeiro.valor_total or 0)
                print(f"   Valor convertido: R$ {valor_float:,.2f}")
            except Exception as e:
                print(f"   ❌ Erro na conversão: {e}")
        
        # Teste de agregação
        try:
            from sqlalchemy import func
            soma_total = CTE.query.with_entities(func.sum(CTE.valor_total)).scalar()
            print(f"   Soma total via SQLAlchemy: {soma_total}")
            print(f"   Tipo da soma: {type(soma_total)}")
        except Exception as e:
            print(f"   ❌ Erro na agregação: {e}")
            
    except Exception as e:
        print(f"   ❌ Erro no teste do modelo: {e}")

def testar_consulta_sql_direta(db):
    """Testa consulta SQL direta no banco"""
    try:
        # Consulta SQL direta
        query = text("""
            SELECT 
                COUNT(*) as total_registros,
                SUM(valor_total) as soma_valores,
                AVG(valor_total) as media_valores,
                MIN(valor_total) as menor_valor,
                MAX(valor_total) as maior_valor,
                COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa,
                COUNT(CASE WHEN data_baixa IS NULL THEN 1 END) as sem_baixa
            FROM dashboard_baker
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query).fetchone()
            
        print(f"   Total registros: {result[0]}")
        print(f"   Soma valores: {result[1]}")
        print(f"   Média valores: {result[2]}")
        print(f"   Menor valor: {result[3]}")
        print(f"   Maior valor: {result[4]}")
        print(f"   Com baixa: {result[5]}")
        print(f"   Sem baixa: {result[6]}")
        
        # Teste de alguns registros específicos
        query2 = text("""
            SELECT numero_cte, destinatario_nome, valor_total, data_baixa
            FROM dashboard_baker 
            WHERE valor_total IS NOT NULL 
            ORDER BY numero_cte DESC 
            LIMIT 5
        """)
        
        with db.engine.connect() as conn:
            resultados = conn.execute(query2).fetchall()
        
        print("\n   Exemplos de registros:")
        for row in resultados:
            print(f"     CTE {row[0]}: {row[1]} - Valor: {row[2]} - Baixa: {row[3]}")
            
    except Exception as e:
        print(f"   ❌ Erro na consulta SQL direta: {e}")
        import traceback
        traceback.print_exc()

def testar_conversoes_dados(db):
    """Testa conversões de dados com pandas"""
    try:
        # Query que replica a do dashboard
        sql_query = text("""
            SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                   data_emissao, numero_fatura, data_baixa, observacao,
                   data_inclusao_fatura, data_envio_processo, primeiro_envio,
                   data_rq_tmc, data_atesto, envio_final, origem_dados
            FROM dashboard_baker 
            ORDER BY numero_cte DESC
            LIMIT 100
        """)
        
        with db.engine.connect() as connection:
            df = pd.read_sql_query(sql_query, connection)
        
        print(f"   DataFrame criado: {len(df)} registros")
        print(f"   Colunas: {list(df.columns)}")
        
        if not df.empty:
            print(f"   Tipos de dados:")
            for col in ['numero_cte', 'valor_total', 'data_emissao']:
                if col in df.columns:
                    print(f"     {col}: {df[col].dtype}")
            
            # Testar conversão de valor_total
            print(f"\n   Testando conversão valor_total:")
            print(f"     Valores originais: {df['valor_total'].head().tolist()}")
            
            # Conversão numérica
            valores_numericos = pd.to_numeric(df['valor_total'], errors='coerce')
            print(f"     Após conversão: {valores_numericos.head().tolist()}")
            print(f"     NaNs após conversão: {valores_numericos.isna().sum()}")
            print(f"     Soma total: {valores_numericos.sum()}")
            
            # Testar conversões de data
            if 'data_emissao' in df.columns:
                print(f"\n   Testando conversão data_emissao:")
                datas_orig = df['data_emissao'].head()
                print(f"     Valores originais: {datas_orig.tolist()}")
                
                datas_conv = pd.to_datetime(df['data_emissao'], errors='coerce')
                print(f"     Após conversão: {datas_conv.head().tolist()}")
                
    except Exception as e:
        print(f"   ❌ Erro no teste de conversões: {e}")
        import traceback
        traceback.print_exc()

def testar_api_dashboard_dados():
    """Testa dados da API do dashboard"""
    try:
        from app.routes.dashboard import _carregar_df_cte, _metricas_basicas
        
        # Carregar DataFrame
        df = _carregar_df_cte()
        print(f"   DataFrame API: {len(df)} registros")
        
        if not df.empty:
            # Calcular métricas
            metricas = _metricas_basicas(df)
            
            print(f"   Métricas calculadas:")
            print(f"     Total CTEs: {metricas.get('total_ctes', 'N/A')}")
            print(f"     Valor Total: {metricas.get('valor_total', 'N/A')}")
            print(f"     Valor Pago: {metricas.get('valor_pago', 'N/A')}")
            print(f"     Clientes Únicos: {metricas.get('clientes_unicos', 'N/A')}")
            
        else:
            print("   ❌ DataFrame da API está vazio")
            
    except Exception as e:
        print(f"   ❌ Erro no teste da API dashboard: {e}")
        import traceback
        traceback.print_exc()

def testar_api_ctes_dados():
    """Testa dados da API de CTEs"""
    try:
        from app.models.cte import CTE
        
        # Teste da paginação
        ctes = CTE.query.limit(10).all()
        print(f"   CTEs via query: {len(ctes)} registros")
        
        if ctes:
            cte = ctes[0]
            print(f"   Exemplo CTE serialização:")
            try:
                dados = cte.to_dict() if hasattr(cte, 'to_dict') else {
                    'numero_cte': cte.numero_cte,
                    'destinatario_nome': cte.destinatario_nome,
                    'valor_total': float(cte.valor_total or 0)
                }
                print(f"     Dados: {dados}")
            except Exception as e:
                print(f"     ❌ Erro na serialização: {e}")
        
    except Exception as e:
        print(f"   ❌ Erro no teste da API CTEs: {e}")

def corrigir_problemas_dados(db):
    """Corrige problemas identificados nos dados"""
    try:
        print("   Executando correções...")
        
        # Verificar se há valores NULL que deveriam ser 0
        query_nulls = text("""
            SELECT COUNT(*) FROM dashboard_baker WHERE valor_total IS NULL
        """)
        
        with db.engine.connect() as conn:
            nulls_count = conn.execute(query_nulls).scalar()
        
        if nulls_count > 0:
            print(f"   ⚠️ Encontrados {nulls_count} registros com valor_total NULL")
            
            # Opção: corrigir NULLs para 0
            # update_nulls = text("""
            #     UPDATE dashboard_baker SET valor_total = 0 WHERE valor_total IS NULL
            # """)
            # with db.engine.connect() as conn:
            #     conn.execute(update_nulls)
            #     conn.commit()
            # print("   ✅ Valores NULL corrigidos para 0")
        
        # Verificar encoding de caracteres
        query_encoding = text("""
            SELECT numero_cte, destinatario_nome 
            FROM dashboard_baker 
            WHERE destinatario_nome ~ '[^\x00-\x7F]'
            LIMIT 5
        """)
        
        try:
            with db.engine.connect() as conn:
                encoding_issues = conn.execute(query_encoding).fetchall()
            
            if encoding_issues:
                print(f"   ⚠️ Possíveis problemas de encoding: {len(encoding_issues)} registros")
                for row in encoding_issues[:3]:
                    print(f"     CTE {row[0]}: {row[1]}")
        except:
            print("   Verificação de encoding pulada (regex não suportada)")
        
        print("   ✅ Diagnóstico de correções concluído")
        
    except Exception as e:
        print(f"   ❌ Erro nas correções: {e}")

def gerar_relatorio_final():
    """Gera relatório final com recomendações"""
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL E RECOMENDAÇÕES")
    print("=" * 60)
    
    print("\n🔧 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("\n1. Se valores estão chegando como NULL:")
    print("   - Verificar se o campo valor_total no Supabase está preenchido")
    print("   - Executar: UPDATE dashboard_baker SET valor_total = 0 WHERE valor_total IS NULL")
    
    print("\n2. Se há problemas de encoding:")
    print("   - Verificar charset da conexão (UTF-8)")
    print("   - Verificar se caracteres especiais estão sendo salvos corretamente")
    
    print("\n3. Se DataFrame está vazio:")
    print("   - Verificar se a tabela 'dashboard_baker' tem o nome correto")
    print("   - Verificar permissões do usuário postgres")
    
    print("\n4. Para corrigir imediatamente:")
    print("   - Executar: python fix_data.py")
    print("   - Reiniciar servidor: python run.py")
    print("   - Limpar cache do navegador")

if __name__ == "__main__":
    try:
        diagnostico_dados_completo()
        gerar_relatorio_final()
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()