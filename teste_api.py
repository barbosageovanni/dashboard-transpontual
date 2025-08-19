#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da API de análise financeira
"""

from app import create_app
from app.services.analise_financeira_service import AnaliseFinanceiraService

def testar_api():
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testando serviço de análise financeira...")
            
            # Testar análise completa
            analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=180)
            print("✅ Análise completa gerada!")
            print(f"📊 Total CTEs analisados: {analise['resumo_filtro']['total_ctes']}")
            print(f"💰 Receita mês atual: R$ {analise['receita_mensal']['receita_mes_corrente']:.2f}")
            print(f"📈 Variação mensal: {analise['receita_mensal']['variacao_percentual']:.1f}%")
            
            # Testar nova métrica
            print("\n🆕 Testando faturamento por inclusão...")
            faturamento_inclusao = AnaliseFinanceiraService.obter_faturamento_por_inclusao(30)
            print("✅ Faturamento por inclusão calculado!")
            print(f"💰 Faturamento total (30d): R$ {faturamento_inclusao['faturamento_total']:.2f}")
            print(f"📊 CTEs com inclusão: {faturamento_inclusao['quantidade_ctes']}")
            print(f"🎯 Status: {faturamento_inclusao['status']}")
            
        except Exception as e:
            print(f"❌ Erro na API: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    testar_api()
