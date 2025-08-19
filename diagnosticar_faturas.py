#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico específico das faturas e gráficos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def diagnosticar_faturas():
    """Diagnóstica o problema das faturas"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 DIAGNÓSTICO DAS FATURAS E GRÁFICOS")
        print("=" * 60)
        
        try:
            # 1. Estatísticas gerais
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_ctes,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as ctes_com_fatura,
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as ctes_com_data_inclusao,
                    COUNT(CASE WHEN data_emissao IS NOT NULL AND data_inclusao_fatura IS NOT NULL THEN 1 END) as ctes_calculo_variacao
                FROM dashboard_baker
            """))
            
            stats = result.fetchone()
            total, com_fatura, com_data_inclusao, com_variacao = stats
            
            print(f"📊 ESTATÍSTICAS DAS FATURAS:")
            print(f"  - Total de CTEs: {total:,}")
            print(f"  - CTEs com número de fatura: {com_fatura:,} ({com_fatura/total*100:.1f}%)")
            print(f"  - CTEs com data de inclusão: {com_data_inclusao:,} ({com_data_inclusao/total*100:.1f}%)")
            print(f"  - CTEs para cálculo de variação: {com_variacao:,} ({com_variacao/total*100:.1f}%)")
            
            # 2. Amostras de dados
            print(f"\n📋 AMOSTRA DE DADOS (primeiros 10 CTEs):")
            result = db.session.execute(text("""
                SELECT 
                    numero_cte,
                    destinatario_nome,
                    data_emissao,
                    numero_fatura,
                    data_inclusao_fatura,
                    valor_total
                FROM dashboard_baker 
                ORDER BY numero_cte
                LIMIT 10
            """))
            
            for row in result.fetchall():
                cte, cliente, emissao, fatura, inclusao, valor = row
                cliente_short = (cliente[:25] + '...') if cliente and len(cliente) > 25 else cliente
                fatura_str = fatura if fatura else 'SEM FATURA'
                inclusao_str = inclusao.strftime('%d/%m/%Y') if inclusao else 'SEM DATA'
                print(f"  CTE {cte}: {cliente_short} | {fatura_str} | {inclusao_str} | R$ {valor:,.2f}")
            
            # 3. Verificar dados para gráficos
            print(f"\n📈 DIAGNÓSTICO DOS GRÁFICOS:")
            
            # Evolução mensal
            result = db.session.execute(text("""
                SELECT 
                    DATE_TRUNC('month', data_emissao) as mes,
                    COUNT(*) as qtd_ctes,
                    SUM(valor_total) as receita
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL
                GROUP BY DATE_TRUNC('month', data_emissao)
                ORDER BY mes DESC
                LIMIT 12
            """))
            
            print(f"  📊 Evolução Mensal (últimos 12 meses):")
            meses_count = 0
            for row in result.fetchall():
                mes, qtd, receita = row
                mes_str = mes.strftime('%m/%Y') if mes else 'N/A'
                print(f"    {mes_str}: {qtd} CTEs - R$ {receita:,.2f}")
                meses_count += 1
            
            if meses_count == 0:
                print(f"    ❌ Nenhum dado mensal encontrado!")
            
            # Top clientes
            result = db.session.execute(text("""
                SELECT 
                    destinatario_nome,
                    COUNT(*) as qtd_ctes,
                    SUM(valor_total) as receita_total
                FROM dashboard_baker 
                WHERE destinatario_nome IS NOT NULL
                GROUP BY destinatario_nome
                ORDER BY SUM(valor_total) DESC
                LIMIT 10
            """))
            
            print(f"\n  👥 Top 10 Clientes:")
            clientes_count = 0
            for row in result.fetchall():
                cliente, qtd, receita = row
                cliente_short = (cliente[:40] + '...') if len(cliente) > 40 else cliente
                print(f"    {cliente_short}: {qtd} CTEs - R$ {receita:,.2f}")
                clientes_count += 1
            
            if clientes_count == 0:
                print(f"    ❌ Nenhum cliente encontrado!")
            
            # 4. Verificar tipos de dados
            print(f"\n🔍 VERIFICAÇÃO DE TIPOS DE DADOS:")
            result = db.session.execute(text("""
                SELECT 
                    data_emissao,
                    valor_total,
                    destinatario_nome
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL
                AND valor_total > 0
                AND destinatario_nome IS NOT NULL
                LIMIT 5
            """))
            
            print(f"  📊 Amostra de dados válidos para gráficos:")
            for row in result.fetchall():
                emissao, valor, cliente = row
                print(f"    {emissao} | R$ {valor:,.2f} | {cliente[:30]}")
            
            # 5. Diagnóstico específico das variações
            print(f"\n🔄 DIAGNÓSTICO DAS VARIAÇÕES:")
            
            variacoes = [
                ('CTE → Inclusão Fatura', 'data_emissao', 'data_inclusao_fatura'),
                ('CTE → Baixa', 'data_emissao', 'data_baixa'),
                ('RQ/TMC → 1º Envio', 'data_rq_tmc', 'primeiro_envio'),
                ('1º Envio → Atesto', 'primeiro_envio', 'data_atesto'),
                ('Atesto → Envio Final', 'data_atesto', 'envio_final')
            ]
            
            for nome, inicio, fim in variacoes:
                result = db.session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM dashboard_baker 
                    WHERE {inicio} IS NOT NULL AND {fim} IS NOT NULL
                """))
                
                count = result.fetchone()[0]
                print(f"  {nome}: {count:,} registros válidos")
                
                if count > 0:
                    result = db.session.execute(text(f"""
                        SELECT AVG(EXTRACT(days FROM ({fim} - {inicio}))) as media_dias
                        FROM dashboard_baker 
                        WHERE {inicio} IS NOT NULL AND {fim} IS NOT NULL
                        AND {fim} >= {inicio}
                    """))
                    
                    media = result.fetchone()[0]
                    if media:
                        print(f"    └─ Média: {media:.1f} dias")
            
        except Exception as e:
            print(f"❌ Erro no diagnóstico: {e}")

if __name__ == "__main__":
    diagnosticar_faturas()