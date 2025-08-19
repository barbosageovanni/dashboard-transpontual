#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige e preenche dados de teste com datas realistas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
from datetime import datetime, timedelta
import random

def corrigir_dados():
    """Corrige dados existentes preenchendo datas faltantes"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 CORRIGINDO DADOS DE TESTE")
        print("=" * 50)
        
        try:
            # 1. Buscar CTEs sem datas completas
            result = db.session.execute(text("""
                SELECT numero_cte, data_emissao, destinatario_nome, valor_total
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL
                ORDER BY numero_cte
            """))
            
            ctes = result.fetchall()
            total_ctes = len(ctes)
            print(f"📊 CTEs para corrigir: {total_ctes}")
            
            if total_ctes == 0:
                print("❌ Nenhum CTE encontrado! Execute: python popular_dados_teste.py")
                return
            
            # 2. Lista de clientes realistas
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
            
            # 3. Corrigir cada CTE
            corrigidos = 0
            for cte_data in ctes:
                numero_cte, data_emissao, destinatario_nome, valor_total = cte_data
                
                # Se não tem data de emissão, pular
                if not data_emissao:
                    continue
                
                # Gerar datas realistas baseadas na emissão
                data_emissao = data_emissao if isinstance(data_emissao, datetime) else datetime.strptime(str(data_emissao), '%Y-%m-%d')
                
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
                
                # Atualizar destinatário se não tiver
                if not destinatario_nome or destinatario_nome.strip() == '':
                    destinatario_nome = random.choice(clientes)
                
                # Veículo aleatório
                veiculo_placa = random.choice(veiculos)
                
                # Fatura
                numero_fatura = f"FAT-{2024000 + numero_cte}" if random.random() < 0.8 else None
                
                try:
                    # Atualizar no banco
                    db.session.execute(text("""
                        UPDATE dashboard_baker SET 
                            destinatario_nome = :destinatario_nome,
                            veiculo_placa = :veiculo_placa,
                            numero_fatura = :numero_fatura,
                            data_inclusao_fatura = :data_inclusao_fatura,
                            data_envio_processo = :data_envio_processo,
                            primeiro_envio = :primeiro_envio,
                            data_rq_tmc = :data_rq_tmc,
                            data_atesto = :data_atesto,
                            envio_final = :envio_final,
                            data_baixa = :data_baixa,
                            updated_at = NOW()
                        WHERE numero_cte = :numero_cte
                    """), {
                        'numero_cte': numero_cte,
                        'destinatario_nome': destinatario_nome,
                        'veiculo_placa': veiculo_placa,
                        'numero_fatura': numero_fatura,
                        'data_inclusao_fatura': data_inclusao_fatura.date(),
                        'data_envio_processo': data_inclusao_fatura.date(),
                        'primeiro_envio': primeiro_envio.date(),
                        'data_rq_tmc': data_rq_tmc.date(),
                        'data_atesto': data_atesto.date(),
                        'envio_final': envio_final.date(),
                        'data_baixa': data_baixa.date() if data_baixa else None
                    })
                    
                    corrigidos += 1
                    if corrigidos % 10 == 0:
                        print(f"✅ {corrigidos} CTEs corrigidos...")
                        
                except Exception as e:
                    print(f"❌ Erro ao corrigir CTE {numero_cte}: {e}")
            
            # Commit final
            db.session.commit()
            
            print(f"\n🎉 Correção concluída!")
            print(f"📊 Total de CTEs corrigidos: {corrigidos}")
            
            # 4. Verificar resultado
            print(f"\n📈 VERIFICAÇÃO PÓS-CORREÇÃO:")
            
            variacoes = [
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
                print(f"  ✅ {nome}: {count} registros válidos")
            
            # Verificar receita por mês
            result = db.session.execute(text("""
                SELECT 
                    DATE_TRUNC('month', data_emissao) as mes,
                    COUNT(*) as ctes,
                    SUM(valor_total) as receita
                FROM dashboard_baker 
                WHERE data_emissao IS NOT NULL
                GROUP BY DATE_TRUNC('month', data_emissao)
                ORDER BY mes DESC
                LIMIT 6
            """))
            
            print(f"\n📊 RECEITA POR MÊS (6 meses mais recentes):")
            for row in result.fetchall():
                mes, ctes, receita = row
                mes_str = mes.strftime('%m/%Y') if mes else 'N/A'
                print(f"  {mes_str}: {ctes} CTEs - R$ {receita:,.2f}")
            
        except Exception as e:
            print(f"❌ Erro na correção: {e}")
            db.session.rollback()

if __name__ == "__main__":
    corrigir_dados()