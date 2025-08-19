#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura dos dados no banco
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def verificar_dados():
    """Verifica dados no banco"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 DIAGNÓSTICO DOS DADOS")
        print("=" * 50)
        
        try:
            # 1. Contagem total
            result = db.session.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
            total_ctes = result.fetchone()[0]
            print(f"📊 Total de CTEs: {total_ctes}")
            
            if total_ctes == 0:
                print("❌ Nenhum CTE encontrado! Execute: python popular_dados_teste.py")
                return
            
            # 2. Verificar datas por coluna
            colunas_data = [
                'data_emissao', 'data_inclusao_fatura', 'primeiro_envio',
                'data_rq_tmc', 'data_atesto', 'envio_final', 'data_baixa'
            ]
            
            print(f"\n📅 ANÁLISE DAS DATAS:")
            for coluna in colunas_data:
                result = db.session.execute(text(f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT({coluna}) as preenchidas,
                        ROUND(COUNT({coluna}) * 100.0 / COUNT(*), 1) as percentual
                    FROM dashboard_baker
                """))
                
                row = result.fetchone()
                total, preenchidas, percentual = row[0], row[1], row[2]
                
                status = "✅" if percentual > 70 else "⚠️" if percentual > 30 else "❌"
                print(f"  {status} {coluna}: {preenchidas}/{total} ({percentual}%)")
            
            # 3. Verificar dados para variações temporais
            print(f"\n🔄 VARIAÇÕES TEMPORAIS POSSÍVEIS:")
            
            variacoes = [
                ('CTE → Inclusão', 'data_emissao', 'data_inclusao_fatura'),
                ('Inclusão → 1º Envio', 'data_inclusao_fatura', 'primeiro_envio'),
                ('RQ/TMC → 1º Envio', 'data_rq_tmc', 'primeiro_envio'),
                ('1º Envio → Atesto', 'primeiro_envio', 'data_atesto'),
                ('Atesto → Envio Final', 'data_atesto', 'envio_final'),
                ('CTE → Baixa', 'data_emissao', 'data_baixa')
            ]
            
            for nome, inicio, fim in variacoes:
                result = db.session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM dashboard_baker 
                    WHERE {inicio} IS NOT NULL AND {fim} IS NOT NULL
                """))
                
                count = result.fetchone()[0]
                status = "✅" if count > 10 else "⚠️" if count > 0 else "❌"
                print(f"  {status} {nome}: {count} registros válidos")
            
            # 4. Verificar dados para gráficos
            print(f"\n📈 DADOS PARA GRÁFICOS:")
            
            # Receita mensal
            result = db.session.execute(text("""
                SELECT COUNT(DISTINCT DATE_TRUNC('month', data_emissao)) as meses_com_dados
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL
            """))
            meses = result.fetchone()[0]
            print(f"  📊 Evolução Mensal: {meses} meses com dados")
            
            # Top clientes
            result = db.session.execute(text("""
                SELECT COUNT(DISTINCT destinatario_nome) as clientes_unicos
                FROM dashboard_baker 
                WHERE destinatario_nome IS NOT NULL
            """))
            clientes = result.fetchone()[0]
            print(f"  👥 Clientes únicos: {clientes}")
            
            # 5. Amostra dos dados
            print(f"\n📋 AMOSTRA DOS DADOS (5 primeiros CTEs):")
            result = db.session.execute(text("""
                SELECT numero_cte, destinatario_nome, valor_total, data_emissao, data_atesto, data_baixa
                FROM dashboard_baker 
                ORDER BY numero_cte 
                LIMIT 5
            """))
            
            for row in result.fetchall():
                cte, cliente, valor, emissao, atesto, baixa = row
                cliente_short = (cliente[:20] + '...') if cliente and len(cliente) > 20 else cliente
                print(f"  CTE {cte}: {cliente_short} - R$ {valor} - {emissao} - {atesto} - {baixa}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_dados()