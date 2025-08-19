#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug das variações temporais - SEM ALTERAR DADOS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import pandas as pd

def debug_variacoes():
    """Debug das variações sem alterar nada"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUG DAS VARIAÇÕES TEMPORAIS")
        print("=" * 50)
        
        try:
            # 1. Buscar dados de amostra para análise
            result = db.session.execute(text("""
                SELECT 
                    numero_cte,
                    data_emissao,
                    data_rq_tmc,
                    primeiro_envio,
                    data_atesto,
                    envio_final
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL 
                AND data_rq_tmc IS NOT NULL 
                AND primeiro_envio IS NOT NULL 
                AND data_atesto IS NOT NULL 
                AND envio_final IS NOT NULL
                ORDER BY data_emissao DESC
                LIMIT 10
            """))
            
            dados = result.fetchall()
            print(f"📊 Amostra de 10 CTEs com todas as datas:")
            
            for row in dados:
                cte, emissao, rq_tmc, primeiro, atesto, final = row
                
                # Calcular variações manualmente
                try:
                    # RQ/TMC → 1º Envio
                    if rq_tmc and primeiro:
                        dias_rq_primeiro = (primeiro - rq_tmc).days
                    else:
                        dias_rq_primeiro = None
                    
                    # 1º Envio → Atesto  
                    if primeiro and atesto:
                        dias_primeiro_atesto = (atesto - primeiro).days
                    else:
                        dias_primeiro_atesto = None
                    
                    # Atesto → Envio Final
                    if atesto and final:
                        dias_atesto_final = (final - atesto).days
                    else:
                        dias_atesto_final = None
                    
                    print(f"  CTE {cte}: RQ→1º:{dias_rq_primeiro}d | 1º→At:{dias_primeiro_atesto}d | At→Fin:{dias_atesto_final}d")
                    
                except Exception as e:
                    print(f"  CTE {cte}: Erro no cálculo - {e}")
            
            # 2. Calcular estatísticas gerais
            print(f"\n📈 ESTATÍSTICAS GERAIS:")
            
            result = db.session.execute(text("""
                SELECT 
                    AVG(EXTRACT(days FROM (primeiro_envio - data_rq_tmc))) as media_rq_primeiro,
                    AVG(EXTRACT(days FROM (data_atesto - primeiro_envio))) as media_primeiro_atesto,
                    AVG(EXTRACT(days FROM (envio_final - data_atesto))) as media_atesto_final,
                    COUNT(*) as total_registros
                FROM dashboard_baker 
                WHERE data_rq_tmc IS NOT NULL 
                AND primeiro_envio IS NOT NULL 
                AND data_atesto IS NOT NULL 
                AND envio_final IS NOT NULL
                AND primeiro_envio >= data_rq_tmc
                AND data_atesto >= primeiro_envio
                AND envio_final >= data_atesto
            """))
            
            stats = result.fetchone()
            if stats:
                rq_primeiro, primeiro_atesto, atesto_final, total = stats
                print(f"  ✅ RQ/TMC → 1º Envio: {rq_primeiro:.1f} dias (média)")
                print(f"  ✅ 1º Envio → Atesto: {primeiro_atesto:.1f} dias (média)")  
                print(f"  ✅ Atesto → Envio Final: {atesto_final:.1f} dias (média)")
                print(f"  📊 Total de registros válidos: {total}")
            
            # 3. Verificar se o problema é no frontend
            print(f"\n🌐 VERIFICANDO CÓDIGO DO DASHBOARD:")
            
            # Simular o cálculo que o dashboard faz
            from app.routes.dashboard import calcular_variacoes_tempo
            
            # Carregar dados como DataFrame (como o dashboard faz)
            query = """
                SELECT numero_cte, data_emissao, data_rq_tmc, primeiro_envio, 
                       data_atesto, envio_final, data_baixa, valor_total
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL
                ORDER BY numero_cte DESC
                LIMIT 100
            """
            
            df = pd.read_sql_query(query, db.session.connection())
            
            print(f"  📊 DataFrame carregado: {len(df)} registros")
            print(f"  📅 Colunas de data: {[col for col in df.columns if 'data_' in col or col in ['primeiro_envio', 'envio_final']]}")
            
            # Verificar tipos de dados
            for col in ['data_rq_tmc', 'primeiro_envio', 'data_atesto', 'envio_final']:
                if col in df.columns:
                    print(f"  🔍 {col}: {df[col].dtype} - Valores não nulos: {df[col].notna().sum()}")
            
            # Tentar calcular as variações
            try:
                variacoes = calcular_variacoes_tempo(df)
                print(f"  ✅ Função calcular_variacoes_tempo retornou: {len(variacoes)} variações")
                
                for codigo, dados in variacoes.items():
                    print(f"    - {codigo}: {dados.get('media', 'N/A')} dias")
                    
            except Exception as e:
                print(f"  ❌ Erro na função calcular_variacoes_tempo: {e}")
            
        except Exception as e:
            print(f"❌ Erro no debug: {e}")

if __name__ == "__main__":
    debug_variacoes()