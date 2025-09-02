#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar dados no banco
"""

from app import create_app
from app.models.cte import CTE
from app import db

def testar_dados():
    app = create_app()
    
    with app.app_context():
        try:
            # Testar conexão
            print("🔌 Testando conexão com banco...")
            total_ctes = CTE.query.count()
            print(f"📊 Total de CTEs no banco: {total_ctes}")
            
            if total_ctes > 0:
                # Mostrar algumas estatísticas
                ctes_com_inclusao = CTE.query.filter(CTE.data_inclusao_fatura.isnot(None)).count()
                print(f"📅 CTEs com data_inclusao_fatura: {ctes_com_inclusao}")
                
                # Mostrar algumas amostras
                sample_ctes = CTE.query.limit(3).all()
                print("\n📋 Amostras de CTEs:")
                for cte in sample_ctes:
                    print(f"  - CTE {cte.numero_cte}: {cte.destinatario_nome} - R$ {cte.valor_total}")
                    print(f"    Data emissão: {cte.data_emissao}")
                    print(f"    Data inclusão fatura: {cte.data_inclusao_fatura}")
                    print()
            
            else:
                print("❌ Nenhum CTE encontrado no banco!")
                
        except Exception as e:
            print(f"❌ Erro ao acessar banco: {str(e)}")

if __name__ == "__main__":
    testar_dados()
