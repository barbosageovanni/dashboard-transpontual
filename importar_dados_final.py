#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Final para Popular Banco de Dados
Backup dados 15set2025.xlsx - VERSAO DEFINITIVA

Importa dados sem problemas de encoding
"""

import os
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging para arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('importacao_log.txt', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
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
        logger.warning(f"Erro ao converter data: {e}")

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
        logger.warning(f"Erro ao converter valor: {e}")
        return None

def importar_dados_definitivo():
    """Importacao definitiva sem problemas de encoding"""
    caminho = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

    print("=" * 60)
    print("IMPORTACAO DEFINITIVA - DASHBOARD BAKER")
    print("=" * 60)

    try:
        from app import create_app, db
        from app.models.cte import CTE

        print("Carregando dados da planilha...")

        # Ler planilha
        df = pd.read_excel(caminho, sheet_name='Dados CTEs')
        print(f"Dados carregados: {len(df)} registros")

        # Criar aplicacao Flask
        app = create_app()

        with app.app_context():
            print(f"\nIniciando processamento de {len(df)} registros...")

            # Identificar colunas por posicao (para evitar problemas de encoding)
            # Baseado na analise anterior:
            # 0: Numero CTE, 1: Cliente, 2: Veiculo, 3: Valor Total
            # 4: Data Emissao, 5: Data Baixa, 6: Numero Fatura
            # 7: Data Inclusao Fatura, 8: Data Envio Processo
            # 9: Primeiro Envio, 10: Data Rq/TMC, 11: Data Atesto
            # 12: Envio Final, 13: Observacoes

            colunas = df.columns.tolist()
            print(f"Colunas identificadas: {len(colunas)} colunas")

            # Verificar CTEs ja existentes
            numeros_cte = df.iloc[:, 0].dropna().astype(int).tolist()  # Primeira coluna = Numero CTE
            ctes_existentes = CTE.obter_ctes_existentes_bulk(numeros_cte)

            print(f"CTEs ja existentes no banco: {len(ctes_existentes)}")

            # Processar registros
            sucessos = 0
            erros = 0
            pulos = 0
            erros_detalhados = []

            for idx, row in df.iterrows():
                try:
                    # Extrair numero CTE (coluna 0)
                    numero_cte = int(row.iloc[0])

                    # Pular se ja existe
                    if numero_cte in ctes_existentes:
                        pulos += 1
                        continue

                    # Preparar dados limpos
                    dados_cte = {
                        'numero_cte': numero_cte,
                        'origem_dados': 'Planilha Backup 15set2025'
                    }

                    # Mapear campos por posicao
                    try:
                        # Cliente (coluna 1)
                        if len(row) > 1 and pd.notna(row.iloc[1]):
                            dados_cte['destinatario_nome'] = str(row.iloc[1]).strip()[:255]

                        # Veiculo (coluna 2)
                        if len(row) > 2 and pd.notna(row.iloc[2]):
                            dados_cte['veiculo_placa'] = str(row.iloc[2]).strip()[:20]

                        # Valor Total (coluna 3)
                        if len(row) > 3 and pd.notna(row.iloc[3]):
                            valor_limpo = limpar_valor_monetario(row.iloc[3])
                            if valor_limpo is not None:
                                dados_cte['valor_total'] = valor_limpo

                        # Data Emissao (coluna 4)
                        if len(row) > 4 and pd.notna(row.iloc[4]):
                            data_limpa = limpar_e_converter_data(row.iloc[4])
                            if data_limpa is not None:
                                dados_cte['data_emissao'] = data_limpa

                        # Data Baixa (coluna 5)
                        if len(row) > 5 and pd.notna(row.iloc[5]):
                            data_limpa = limpar_e_converter_data(row.iloc[5])
                            if data_limpa is not None:
                                dados_cte['data_baixa'] = data_limpa

                        # Numero Fatura (coluna 6)
                        if len(row) > 6 and pd.notna(row.iloc[6]):
                            dados_cte['numero_fatura'] = str(row.iloc[6]).strip()[:100]

                        # Data Inclusao Fatura (coluna 7)
                        if len(row) > 7 and pd.notna(row.iloc[7]):
                            data_limpa = limpar_e_converter_data(row.iloc[7])
                            if data_limpa is not None:
                                dados_cte['data_inclusao_fatura'] = data_limpa

                        # Data Envio Processo (coluna 8)
                        if len(row) > 8 and pd.notna(row.iloc[8]):
                            data_limpa = limpar_e_converter_data(row.iloc[8])
                            if data_limpa is not None:
                                dados_cte['data_envio_processo'] = data_limpa

                        # Primeiro Envio (coluna 9)
                        if len(row) > 9 and pd.notna(row.iloc[9]):
                            data_limpa = limpar_e_converter_data(row.iloc[9])
                            if data_limpa is not None:
                                dados_cte['primeiro_envio'] = data_limpa

                        # Data Rq/TMC (coluna 10)
                        if len(row) > 10 and pd.notna(row.iloc[10]):
                            data_limpa = limpar_e_converter_data(row.iloc[10])
                            if data_limpa is not None:
                                dados_cte['data_rq_tmc'] = data_limpa

                        # Data Atesto (coluna 11)
                        if len(row) > 11 and pd.notna(row.iloc[11]):
                            data_limpa = limpar_e_converter_data(row.iloc[11])
                            if data_limpa is not None:
                                dados_cte['data_atesto'] = data_limpa

                        # Envio Final (coluna 12)
                        if len(row) > 12 and pd.notna(row.iloc[12]):
                            data_limpa = limpar_e_converter_data(row.iloc[12])
                            if data_limpa is not None:
                                dados_cte['envio_final'] = data_limpa

                        # Observacoes (coluna 13)
                        if len(row) > 13 and pd.notna(row.iloc[13]):
                            dados_cte['observacao'] = str(row.iloc[13]).strip()

                    except Exception as e:
                        logger.warning(f"Erro ao mapear dados do CTE {numero_cte}: {e}")

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
                        if len(erros_detalhados) <= 5:  # Mostrar apenas os primeiros 5 erros
                            logger.warning(erro_detalhado)

                except Exception as e:
                    erros += 1
                    erro_msg = f"Erro no registro {idx}: {str(e)}"
                    erros_detalhados.append(erro_msg)
                    if len(erros_detalhados) <= 5:
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

            if (len(df) - pulos) > 0:
                taxa_sucesso = (sucessos / (len(df) - pulos)) * 100
                print(f"Taxa de sucesso:                {taxa_sucesso:.1f}%")

            if erros_detalhados:
                print(f"\nPrimeiros erros encontrados (veja importacao_log.txt para detalhes completos):")
                for i, erro in enumerate(erros_detalhados[:5]):
                    print(f"  {i+1}. {erro}")

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
        sucesso = importar_dados_definitivo()
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