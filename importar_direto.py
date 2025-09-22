#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Direto para Importacao
Evita problemas de encoding carregando apenas o minimo necessario
"""

import os
import sys
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar variaveis de ambiente
load_dotenv()

def limpar_data(valor):
    """Converte valores de data"""
    if pd.isna(valor) or valor == '':
        return None

    try:
        if hasattr(valor, 'date'):
            return valor.date()

        if isinstance(valor, str):
            valor = valor.strip()
            if '/' in valor:
                try:
                    return pd.to_datetime(valor, format='%d/%m/%Y').date()
                except:
                    pass
            try:
                return pd.to_datetime(valor).date()
            except:
                pass
    except:
        pass

    return None

def limpar_valor(valor):
    """Converte valores monetarios"""
    if pd.isna(valor) or valor == '':
        return None

    try:
        if isinstance(valor, (int, float)):
            return float(valor)

        if isinstance(valor, str):
            valor = valor.replace('R$', '').replace(' ', '')
            valor = valor.replace('.', '').replace(',', '.')
            return float(valor)

        return float(valor)
    except:
        return None

def importar_com_sqlalchemy():
    """Importacao direta usando SQLAlchemy sem Flask"""

    # Construir URL do banco a partir dos componentes
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    if not all([db_host, db_name, db_user, db_password]):
        print("Erro: Variaveis de ambiente do banco nao encontradas")
        return False

    # Fazer URL encode da senha para escapar caracteres especiais
    from urllib.parse import quote_plus
    password_encoded = quote_plus(db_password)
    database_url = f"postgresql://{db_user}:{password_encoded}@{db_host}:{db_port}/{db_name}"

    print("Conectando ao banco...")
    engine = create_engine(database_url)

    try:
        # Testar conexao
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Conexao com banco OK")

        # Carregar planilha
        caminho = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

        print("Carregando planilha...")
        df = pd.read_excel(caminho, sheet_name='Dados CTEs')
        print(f"Registros carregados: {len(df)}")

        # Verificar CTEs existentes
        with engine.connect() as conn:
            result = conn.execute(text("SELECT numero_cte FROM dashboard_baker"))
            ctes_existentes = {row[0] for row in result}

        print(f"CTEs ja existentes: {len(ctes_existentes)}")

        # Preparar dados para insercao
        dados_para_inserir = []
        sucessos = 0
        erros = 0
        pulos = 0

        for idx, row in df.iterrows():
            try:
                # Numero CTE (coluna 0)
                numero_cte = int(row.iloc[0])

                # Pular se ja existe
                if numero_cte in ctes_existentes:
                    pulos += 1
                    continue

                # Preparar registro
                registro = {
                    'numero_cte': numero_cte,
                    'destinatario_nome': str(row.iloc[1]).strip()[:255] if pd.notna(row.iloc[1]) else None,
                    'veiculo_placa': str(row.iloc[2]).strip()[:20] if pd.notna(row.iloc[2]) else None,
                    'valor_total': limpar_valor(row.iloc[3]) if len(row) > 3 else None,
                    'data_emissao': limpar_data(row.iloc[4]) if len(row) > 4 else None,
                    'data_baixa': limpar_data(row.iloc[5]) if len(row) > 5 else None,
                    'numero_fatura': str(row.iloc[6]).strip()[:100] if len(row) > 6 and pd.notna(row.iloc[6]) else None,
                    'data_inclusao_fatura': limpar_data(row.iloc[7]) if len(row) > 7 else None,
                    'data_envio_processo': limpar_data(row.iloc[8]) if len(row) > 8 else None,
                    'primeiro_envio': limpar_data(row.iloc[9]) if len(row) > 9 else None,
                    'data_rq_tmc': limpar_data(row.iloc[10]) if len(row) > 10 else None,
                    'data_atesto': limpar_data(row.iloc[11]) if len(row) > 11 else None,
                    'envio_final': limpar_data(row.iloc[12]) if len(row) > 12 else None,
                    'observacao': str(row.iloc[13]).strip() if len(row) > 13 and pd.notna(row.iloc[13]) else None,
                    'origem_dados': 'Planilha Backup 15set2025',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }

                dados_para_inserir.append(registro)
                sucessos += 1

                # Inserir em lotes de 100
                if len(dados_para_inserir) >= 100:
                    inserir_lote(engine, dados_para_inserir)
                    print(f"Lote inserido: {sucessos} registros processados")
                    dados_para_inserir = []

            except Exception as e:
                erros += 1
                print(f"Erro no registro {idx}: {e}")

        # Inserir lote final
        if dados_para_inserir:
            inserir_lote(engine, dados_para_inserir)

        # Relatorio final
        print("\n" + "=" * 50)
        print("RELATORIO FINAL:")
        print("=" * 50)
        print(f"Total na planilha:      {len(df)}")
        print(f"Ja existentes (pulados): {pulos}")
        print(f"Importados com sucesso:  {sucessos}")
        print(f"Erros:                   {erros}")

        # Verificar total no banco
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
            total_final = result.fetchone()[0]
            print(f"Total no banco agora:    {total_final}")

        return sucessos > 0

    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def inserir_lote(engine, dados):
    """Insere um lote de dados no banco"""

    sql = """
    INSERT INTO dashboard_baker
    (numero_cte, destinatario_nome, veiculo_placa, valor_total, data_emissao,
     data_baixa, numero_fatura, data_inclusao_fatura, data_envio_processo,
     primeiro_envio, data_rq_tmc, data_atesto, envio_final, observacao,
     origem_dados, created_at, updated_at)
    VALUES
    (%(numero_cte)s, %(destinatario_nome)s, %(veiculo_placa)s, %(valor_total)s, %(data_emissao)s,
     %(data_baixa)s, %(numero_fatura)s, %(data_inclusao_fatura)s, %(data_envio_processo)s,
     %(primeiro_envio)s, %(data_rq_tmc)s, %(data_atesto)s, %(envio_final)s, %(observacao)s,
     %(origem_dados)s, %(created_at)s, %(updated_at)s)
    """

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for registro in dados:
                conn.execute(text(sql), registro)
            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"Erro ao inserir lote: {e}")
            # Tentar inserir um por vez para identificar o problema
            for i, registro in enumerate(dados):
                try:
                    with engine.connect() as conn2:
                        trans2 = conn2.begin()
                        conn2.execute(text(sql), registro)
                        trans2.commit()
                        print(f"Registro {i+1} inserido individualmente")
                except Exception as e2:
                    print(f"Erro no registro {i+1}: {e2}")
                    print(f"Dados: {registro}")
            raise

if __name__ == "__main__":
    print("IMPORTACAO DIRETA - DASHBOARD BAKER")
    print("=" * 50)

    try:
        sucesso = importar_com_sqlalchemy()
        if sucesso:
            print("\n*** IMPORTACAO CONCLUIDA! ***")
        else:
            print("\n*** IMPORTACAO FALHOU ***")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print("Finalizado.")