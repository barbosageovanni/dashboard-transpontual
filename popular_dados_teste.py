#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular dados de teste no Dashboard Baker
Cria CTEs com datas realistas para demonstração
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.cte import CTE
from datetime import datetime, timedelta
import random

def criar_dados_teste():
    """Cria dados de teste realistas"""
    
    app = create_app()
    
    with app.app_context():
        print("🗄️ Criando dados de teste...")
        
        # Verificar se já existem dados
        total_existente = CTE.query.count()
        print(f"📊 CTEs existentes no banco: {total_existente}")
        
        if total_existente >= 50:
            resposta = input(f"Já existem {total_existente} CTEs. Deseja adicionar mais? (s/N): ")
            if resposta.lower() != 's':
                print("⏭️ Mantendo dados existentes.")
                return
        
        # Dados realistas
        clientes = [
            "Transportadora ABC Ltda",
            "Logística XYZ S.A.", 
            "Frete Rápido Express",
            "Carga Pesada Transportes",
            "Via Sul Logística",
            "Norte Transportes",
            "Amazônia Cargas",
            "Pantanal Logística",
            "Serra Transportes",
            "Litoral Cargas",
            "Rotas do Brasil",
            "Express Delivery",
            "Cargo Master",
            "TransBrasil",
            "LogiMax"
        ]
        
        veiculos = [
            "ABC-1234", "XYZ-5678", "DEF-9012", "GHI-3456", "JKL-7890",
            "MNO-2345", "PQR-6789", "STU-0123", "VWX-4567", "YZA-8901",
            "BRA-1111", "LOG-2222", "TRK-3333", "CAR-4444", "VAN-5555"
        ]
        
        # Gerar 80 CTEs com datas dos últimos 12 meses
        base_date = datetime.now() - timedelta(days=365)
        numero_inicial = 22001
        
        # Verificar último número usado
        ultimo_cte = CTE.query.order_by(CTE.numero_cte.desc()).first()
        if ultimo_cte:
            numero_inicial = ultimo_cte.numero_cte + 1
        
        ctes_criados = 0
        
        for i in range(80):
            numero_cte = numero_inicial + i
            
            # Verificar se CTE já existe
            if CTE.buscar_por_numero(numero_cte):
                print(f"⏭️ CTE {numero_cte} já existe, pulando...")
                continue
            
            # Datas progressivas realistas
            data_emissao = base_date + timedelta(days=random.randint(0, 350))
            
            # Processo realista: cada etapa alguns dias após a anterior
            data_inclusao_fatura = data_emissao + timedelta(days=random.randint(1, 5))
            primeiro_envio = data_inclusao_fatura + timedelta(days=random.randint(0, 3))
            data_rq_tmc = primeiro_envio + timedelta(days=random.randint(-2, 2))
            data_atesto = primeiro_envio + timedelta(days=random.randint(3, 14))
            envio_final = data_atesto + timedelta(days=random.randint(1, 4))
            
            # 70% das faturas são pagas
            data_baixa = None
            if random.random() < 0.7:
                data_baixa = envio_final + timedelta(days=random.randint(5, 45))
            
            cte_data = {
                'numero_cte': numero_cte,
                'destinatario_nome': random.choice(clientes),
                'veiculo_placa': random.choice(veiculos),
                'valor_total': round(random.uniform(800, 15000), 2),
                'data_emissao': data_emissao.date(),
                'numero_fatura': f"FAT-{2024000 + i}" if random.random() < 0.8 else None,
                'data_baixa': data_baixa.date() if data_baixa else None,
                'observacao': f"CTE de teste #{i+1} - Dados realistas",
                'data_inclusao_fatura': data_inclusao_fatura.date(),
                'data_envio_processo': data_inclusao_fatura.date(),
                'primeiro_envio': primeiro_envio.date(),
                'data_rq_tmc': data_rq_tmc.date(),
                'data_atesto': data_atesto.date(),
                'envio_final': envio_final.date(),
                'origem_dados': 'Teste Automatizado'
            }
            
            try:
                sucesso, resultado = CTE.criar_cte(cte_data)
                
                if sucesso:
                    ctes_criados += 1
                    if ctes_criados % 10 == 0:
                        print(f"✅ {ctes_criados} CTEs criados...")
                else:
                    print(f"❌ Erro ao criar CTE {numero_cte}: {resultado}")
                    
            except Exception as e:
                print(f"❌ Erro ao criar CTE {numero_cte}: {e}")
        
        print(f"\n🎉 Dados de teste criados com sucesso!")
        print(f"📊 Total de CTEs criados: {ctes_criados}")
        print(f"📊 Total de CTEs no banco: {CTE.query.count()}")
        
        # Estatísticas dos dados criados
        print(f"\n📈 Estatísticas dos dados:")
        total_valor = sum(float(cte.valor_total or 0) for cte in CTE.query.all())
        print(f"💰 Valor total: R$ {total_valor:,.2f}")
        print(f"👥 Clientes únicos: {len(set(cte.destinatario_nome for cte in CTE.query.all() if cte.destinatario_nome))}")
        print(f"🚛 Veículos únicos: {len(set(cte.veiculo_placa for cte in CTE.query.all() if cte.veiculo_placa))}")

if __name__ == "__main__":
    criar_dados_teste()