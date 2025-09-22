#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Corrigido para Popular Banco de Dados
Backup dados 15set2025.xlsx - VERSAO CORRIGIDA

Corrige problemas de encoding e mapeamento identificados
"""

import os
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def limpar_e_converter_data(valor):
    """Converte valores de data de formatos mistos para date"""
    if pd.isna(valor) or valor == '':
        return None

    try:
        # Se ja eh datetime, converter para date
        if hasattr(valor, 'date'):
            return valor.date()

        # Se eh string, tentar parsear
        if isinstance(valor, str):
            valor = valor.strip()

            # Formato brasileiro dd/mm/yyyy
            if '/' in valor:
                try:
                    return pd.to_datetime(valor, format='%d/%m/%Y').date()
                except:
                    pass

            # Outros formatos
            try:
                return pd.to_datetime(valor).date()
            except:
                pass

    except Exception as e:
        logger.warning(f"Erro ao converter data '{valor}': {e}")

    return None

def limpar_valor_monetario(valor):
    """Limpa e converte valores monetarios"""
    if pd.isna(valor) or valor == '':
        return None

    try:
        if isinstance(valor, (int, float)):
            return Decimal(str(valor))

        if isinstance(valor, str):
            # Remover formatacao
            valor = valor.replace('R$', '').replace(' ', '')
            valor = valor.replace('.', '').replace(',', '.')
            return Decimal(valor)

        return Decimal(str(valor))

    except Exception as e:
        logger.warning(f"Erro ao converter valor '{valor}': {e}")
        return None

def importar_dados_corrigido():
    """Importacao corrigida com tratamento adequado dos dados"""
    caminho = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

    print("=" * 60)
    print("IMPORTACAO CORRIGIDA - DASHBOARD BAKER")
    print("=" * 60)

    try:
        from app import create_app, db
        from app.models.cte import CTE

        print("Carregando dados da planilha...")

        # Ler planilha com encoding correto
        df = pd.read_excel(caminho, sheet_name='Dados CTEs')
        print(f"Dados carregados: {len(df)} registros")

        # Mapeamento correto das colunas (com encoding real)
        mapeamento_colunas = {
            'N�mero CTE': 'numero_cte',           # Numero CTE
            'Cliente': 'destinatario_nome',        # Cliente
            'Veiculo': 'veiculo_placa',           # Veiculo
            'Valor Total': 'valor_total',          # Valor Total
            'Data Emiss�o': 'data_emissao',       # Data Emissao
            'Data Baixa': 'data_baixa',           # Data Baixa
            'N�mero Fatura': 'numero_fatura',     # Numero Fatura
            'Data Inclus�o Fatura': 'data_inclusao_fatura',  # Data Inclusao Fatura
            'Data Envio Processo': 'data_envio_processo',     # Data Envio Processo
            'Primeiro Envio': 'primeiro_envio',    # Primeiro Envio
            'Data Rq/TMC': 'data_rq_tmc',         # Data Rq/TMC
            'Data Atesto': 'data_atesto',         # Data Atesto
            'Envio Final': 'envio_final',         # Envio Final
            'Observa��es': 'observacao'           # Observacoes
        }

        print("Mapeamento de colunas:")
        for col_excel, col_db in mapeamento_colunas.items():
            print(f"  {col_excel} -> {col_db}")

        # Criar aplicacao Flask
        app = create_app()

        with app.app_context():
            print(f"\nIniciando processamento de {len(df)} registros...")

            # Verificar CTEs ja existentes (otimizado)
            numeros_cte = df['N�mero CTE'].dropna().astype(int).tolist()
            ctes_existentes = CTE.obter_ctes_existentes_bulk(numeros_cte)

            print(f"CTEs ja existentes no banco: {len(ctes_existentes)}")

            # Processar registros
            sucessos = 0
            erros = 0
            pulos = 0
            erros_detalhados = []

            for idx, row in df.iterrows():
                try:
                    # Extrair numero CTE
                    numero_cte = int(row['N�mero CTE'])

                    # Pular se ja existe
                    if numero_cte in ctes_existentes:
                        pulos += 1
                        continue

                    # Preparar dados limpos
                    dados_cte = {
                        'numero_cte': numero_cte,
                        'origem_dados': 'Planilha Backup 15set2025'
                    }

                    # Mapear e limpar cada campo
                    for col_excel, col_db in mapeamento_colunas.items():
                        if col_excel in row.index and pd.notna(row[col_excel]):
                            valor = row[col_excel]

                            if col_db == 'destinatario_nome':
                                dados_cte[col_db] = str(valor).strip()[:255]

                            elif col_db == 'veiculo_placa':
                                dados_cte[col_db] = str(valor).strip()[:20]

                            elif col_db == 'numero_fatura':
                                dados_cte[col_db] = str(valor).strip()[:100]

                            elif col_db == 'observacao':
                                dados_cte[col_db] = str(valor).strip()

                            elif col_db == 'valor_total':
                                valor_limpo = limpar_valor_monetario(valor)
                                if valor_limpo is not None:
                                    dados_cte[col_db] = valor_limpo

                            elif col_db.startswith('data_') or col_db in ['primeiro_envio', 'envio_final']:
                                data_limpa = limpar_e_converter_data(valor)
                                if data_limpa is not None:
                                    dados_cte[col_db] = data_limpa

                    # Tentar criar CTE
                    sucesso, resultado = CTE.criar_cte(dados_cte)

                    if sucesso:
                        sucessos += 1
                        if sucessos % 100 == 0:
                            print(f"  Processados: {sucessos} registros...")
                    else:
                        erros += 1
                        erro_detalhado = f"CTE {numero_cte}: {resultado}"
                        erros_detalhados.append(erro_detalhado)
                        if len(erros_detalhados) <= 10:  # Mostrar apenas os primeiros 10 erros
                            logger.warning(erro_detalhado)

                except Exception as e:
                    erros += 1
                    erro_msg = f"Erro no registro {idx}: {str(e)}"
                    erros_detalhados.append(erro_msg)
                    if len(erros_detalhados) <= 10:
                        logger.error(erro_msg)

            # Commit final
            try:
                db.session.commit()
                print("Transacao finalizada com sucesso!")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erro no commit final: {e}")

            # Relatorio final
            print(f"\n" + "=" * 50)
            print("RELATORIO FINAL:")
            print("=" * 50)
            print(f"Total de registros na planilha: {len(df)}")
            print(f"CTEs ja existentes (pulados):   {pulos}")
            print(f"Importados com sucesso:         {sucessos}")
            print(f"Erros durante importacao:       {erros}")
            print(f"Taxa de sucesso:                {(sucessos/(len(df)-pulos)*100):.1f}%" if (len(df)-pulos) > 0 else "N/A")

            if erros_detalhados and len(erros_detalhados) <= 10:
                print(f"\nPrimeiros erros encontrados:")
                for erro in erros_detalhados[:10]:
                    print(f"  - {erro}")
            elif erros > 10:
                print(f"\n{erros} erros encontrados (mostrando apenas os primeiros 10 nos logs)")

            # Verificar resultado
            total_final = CTE.query.count()
            print(f"\nCTEs no banco apos importacao: {total_final}")

            return sucessos > 0

    except Exception as e:
        logger.error(f"Erro geral na importacao: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        sucesso = importar_dados_corrigido()
        if sucesso:
            print("\n*** IMPORTACAO CONCLUIDA COM SUCESSO! ***")
        else:
            print("\n*** IMPORTACAO FALHOU ***")
    except KeyboardInterrupt:
        print("\nImportacao cancelada pelo usuario")
    except Exception as e:
        logger.error(f"Erro nao tratado: {e}")
        print(f"Erro inesperado: {e}")
    finally:
        print("Finalizando...")