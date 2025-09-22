#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Final para Popular Banco de Dados
Versao corrigida com sintaxe SQL adequada
"""

import os
import sys
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

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

def importar_com_pandas():
    """Importacao usando pandas to_sql (mais simples)"""

    # URL do banco
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    if not all([db_host, db_name, db_user, db_password]):
        print("Erro: Variaveis de ambiente do banco nao encontradas")
        return False

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

        # Preparar DataFrame para insercao
        print("Processando dados...")

        # Limpar e preparar colunas
        df_clean = df.copy()

        # Renomear colunas para corresponder ao schema do banco
        df_clean = df_clean.rename(columns={
            df_clean.columns[0]: 'numero_cte',      # Numero CTE
            df_clean.columns[1]: 'destinatario_nome', # Cliente
            df_clean.columns[2]: 'veiculo_placa',   # Veiculo
            df_clean.columns[3]: 'valor_total',     # Valor Total
            df_clean.columns[4]: 'data_emissao',    # Data Emissao
            df_clean.columns[5]: 'data_baixa',      # Data Baixa
            df_clean.columns[6]: 'numero_fatura',   # Numero Fatura
            df_clean.columns[7]: 'data_inclusao_fatura',  # Data Inclusao Fatura
            df_clean.columns[8]: 'data_envio_processo',   # Data Envio Processo
            df_clean.columns[9]: 'primeiro_envio',  # Primeiro Envio
            df_clean.columns[10]: 'data_rq_tmc',    # Data Rq/TMC
            df_clean.columns[11]: 'data_atesto',    # Data Atesto
            df_clean.columns[12]: 'envio_final',    # Envio Final
            df_clean.columns[13]: 'observacao'      # Observacoes
        })

        # Filtrar apenas registros novos
        df_novos = df_clean[~df_clean['numero_cte'].isin(ctes_existentes)]
        print(f"Registros novos para importar: {len(df_novos)}")

        if len(df_novos) == 0:
            print("Nenhum registro novo para importar")
            return True

        # Limpar e converter tipos de dados
        print("Convertendo tipos de dados...")

        # Converter numero_cte para int
        df_novos = df_novos.copy()
        df_novos['numero_cte'] = df_novos['numero_cte'].astype(int)

        # Limitar tamanhos de string
        df_novos['destinatario_nome'] = df_novos['destinatario_nome'].astype(str).str[:255]
        df_novos['veiculo_placa'] = df_novos['veiculo_placa'].astype(str).str[:20]
        df_novos['numero_fatura'] = df_novos['numero_fatura'].astype(str).str[:100]

        # Converter datas
        colunas_data = ['data_emissao', 'data_baixa', 'data_inclusao_fatura',
                       'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                       'data_atesto', 'envio_final']

        for col in colunas_data:
            if col in df_novos.columns:
                df_novos[col] = df_novos[col].apply(limpar_data)

        # Converter valores monetarios
        df_novos['valor_total'] = df_novos['valor_total'].apply(limpar_valor)

        # Adicionar metadados
        df_novos['origem_dados'] = 'Planilha Backup 15set2025'
        df_novos['created_at'] = datetime.now()
        df_novos['updated_at'] = datetime.now()

        # Selecionar apenas colunas que existem na tabela
        colunas_banco = [
            'numero_cte', 'destinatario_nome', 'veiculo_placa', 'valor_total',
            'data_emissao', 'data_baixa', 'numero_fatura', 'data_inclusao_fatura',
            'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
            'data_atesto', 'envio_final', 'observacao', 'origem_dados',
            'created_at', 'updated_at'
        ]

        df_final = df_novos[colunas_banco]

        # Importar usando pandas to_sql
        print(f"Importando {len(df_final)} registros...")

        df_final.to_sql(
            name='dashboard_baker',
            con=engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=100
        )

        print("Importacao concluida com sucesso!")

        # Verificar resultado
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
            total_final = result.fetchone()[0]
            print(f"Total no banco agora: {total_final}")

        return True

    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("IMPORTACAO FINAL - DASHBOARD BAKER")
    print("=" * 50)

    try:
        sucesso = importar_com_pandas()
        if sucesso:
            print("\n*** IMPORTACAO CONCLUIDA COM SUCESSO! ***")
        else:
            print("\n*** IMPORTACAO FALHOU ***")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print("Finalizado.")