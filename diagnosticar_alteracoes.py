#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico das alterações nos dados reais
APENAS LEITURA - NÃO ALTERA NADA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def diagnosticar_alteracoes():
    """Diagnóstica alterações nos dados - SEM MODIFICAR"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 DIAGNÓSTICO DE ALTERAÇÕES NOS DADOS")
        print("=" * 60)
        
        try:
            # 1. Estatísticas gerais
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_ctes,
                    COUNT(DISTINCT destinatario_nome) as clientes_unicos,
                    COUNT(DISTINCT veiculo_placa) as veiculos_unicos,
                    SUM(valor_total) as valor_total,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as ctes_com_baixa,
                    COUNT(CASE WHEN origem_dados LIKE '%Teste%' OR observacao LIKE '%teste%' THEN 1 END) as registros_teste
                FROM dashboard_baker
            """))
            
            stats = result.fetchone()
            total, clientes, veiculos, valor, baixas, testes = stats
            
            print(f"📊 ESTATÍSTICAS ATUAIS:")
            print(f"  - Total de CTEs: {total:,}")
            print(f"  - Clientes únicos: {clientes}")
            print(f"  - Veículos únicos: {veiculos}")
            print(f"  - Valor total: R$ {valor:,.2f}")
            print(f"  - CTEs com baixa: {baixas}")
            print(f"  - Registros de teste identificados: {testes}")
            
            # 2. Verificar dados suspeitos
            print(f"\n🔍 DADOS SUSPEITOS:")
            
            # Registros com origem_dados = teste
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM dashboard_baker 
                WHERE origem_dados IN ('Teste Automatizado', 'Auto-Setup')
                OR observacao LIKE '%teste%'
                OR observacao LIKE '%Teste%'
            """))
            teste_count = result.fetchone()[0]
            print(f"  - Registros com origem 'Teste': {teste_count}")
            
            # CTEs com números muito altos (possivelmente gerados)
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM dashboard_baker 
                WHERE numero_cte > 22000
            """))
            ctes_altos = result.fetchone()[0]
            print(f"  - CTEs com números > 22000: {ctes_altos}")
            
            # Dados de clientes genéricos
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM dashboard_baker 
                WHERE destinatario_nome IN (
                    'Transportadora ABC Ltda', 'Logística XYZ S.A.', 'Frete Rápido Express',
                    'Cliente Exemplo', 'Usuário Demo'
                )
            """))
            clientes_genericos = result.fetchone()[0]
            print(f"  - Clientes genéricos (não Baker Hughes): {clientes_genericos}")
            
            # 3. Analisar período dos dados
            print(f"\n📅 ANÁLISE TEMPORAL:")
            result = db.session.execute(text("""
                SELECT 
                    MIN(data_emissao) as primeira_data,
                    MAX(data_emissao) as ultima_data,
                    COUNT(CASE WHEN data_emissao >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as ultimos_30_dias
                FROM dashboard_baker
                WHERE data_emissao IS NOT NULL
            """))
            
            temporal = result.fetchone()
            primeira, ultima, recentes = temporal
            print(f"  - Primeira emissão: {primeira}")
            print(f"  - Última emissão: {ultima}")
            print(f"  - CTEs dos últimos 30 dias: {recentes}")
            
            # 4. Clientes principais (Baker Hughes deveria dominar)
            print(f"\n👥 TOP 10 CLIENTES:")
            result = db.session.execute(text("""
                SELECT 
                    destinatario_nome,
                    COUNT(*) as qtd_ctes,
                    SUM(valor_total) as valor_total
                FROM dashboard_baker
                WHERE destinatario_nome IS NOT NULL
                GROUP BY destinatario_nome
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """))
            
            for row in result.fetchall():
                cliente, qtd, valor = row
                cliente_short = (cliente[:30] + '...') if len(cliente) > 30 else cliente
                print(f"  - {cliente_short}: {qtd:,} CTEs - R$ {valor:,.0f}")
            
            # 5. Verificar dados originais vs. gerados
            print(f"\n🏭 ANÁLISE DOS DADOS BAKER HUGHES:")
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM dashboard_baker 
                WHERE destinatario_nome LIKE '%BAKER HUGHES%'
            """))
            baker_hughes_count = result.fetchone()[0]
            print(f"  - CTEs da Baker Hughes: {baker_hughes_count}")
            
            # CTEs com padrão de numeração original (baixos)
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM dashboard_baker 
                WHERE numero_cte < 23000
                AND destinatario_nome LIKE '%BAKER HUGHES%'
            """))
            baker_originais = result.fetchone()[0]
            print(f"  - CTEs Baker Hughes com numeração original (< 23000): {baker_originais}")
            
            # 6. Recomendações
            print(f"\n💡 ANÁLISE:")
            if teste_count > 0:
                print(f"  ⚠️ Encontrados {teste_count} registros de teste que devem ser removidos")
            
            if clientes_genericos > 0:
                print(f"  ⚠️ Encontrados {clientes_genericos} clientes genéricos (não reais)")
            
            if ctes_altos > 100:
                print(f"  ⚠️ Muitos CTEs com numeração alta ({ctes_altos}) - possivelmente gerados")
            
            if baker_hughes_count < total * 0.8:
                print(f"  ⚠️ Baker Hughes representa menos de 80% dos dados - dados misturados")
            
            print(f"\n📋 PRÓXIMOS PASSOS SUGERIDOS:")
            if teste_count > 0 or clientes_genericos > 0:
                print(f"  1. Executar limpeza dos dados de teste")
                print(f"  2. Manter apenas dados reais da Baker Hughes")
                print(f"  3. Fazer backup antes da limpeza")
            else:
                print(f"  1. Dados parecem estar limpos")
                print(f"  2. Investigar por que gráficos não aparecem")
            
        except Exception as e:
            print(f"❌ Erro no diagnóstico: {e}")

if __name__ == "__main__":
    diagnosticar_alteracoes()