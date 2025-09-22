#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Popular Banco de Dados com dados da Planilha
Backup dados 15set2025.xlsx

Importa dados da planilha Excel para o banco dashboard_baker
com validação de duplicatas na coluna numero_cte.
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

def analisar_planilha(caminho_planilha):
    """Analisa a estrutura da planilha Excel"""
    try:
        print("📊 Analisando estrutura da planilha...")

        # Ler planilha
        excel_file = pd.ExcelFile(caminho_planilha)
        print(f"📄 Planilhas encontradas: {excel_file.sheet_names}")

        # Usar a primeira planilha por padrão
        df = pd.read_excel(caminho_planilha, sheet_name=0)
        print(f"📋 Dados encontrados: {len(df)} linhas, {len(df.columns)} colunas")

        # Mostrar colunas
        print("\n📝 Colunas encontradas:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")

        # Mostrar preview dos dados
        print("\n👀 Preview dos primeiros 3 registros:")
        print(df.head(3).to_string())

        # Verificar coluna numero_cte
        colunas_cte = [col for col in df.columns if 'cte' in col.lower() or 'número' in col.lower()]
        if colunas_cte:
            print(f"\n🎯 Possíveis colunas de número CTE: {colunas_cte}")

        return df, excel_file.sheet_names

    except Exception as e:
        print(f"❌ Erro ao analisar planilha: {e}")
        return None, []

def mapear_colunas(df):
    """Mapeia colunas da planilha para campos do banco"""

    # Mapeamento automático baseado em palavras-chave
    mapeamento_automatico = {}

    for col in df.columns:
        col_lower = col.lower().strip()

        # Número CTE
        if any(word in col_lower for word in ['cte', 'número', 'num']):
            mapeamento_automatico['numero_cte'] = col

        # Destinatário/Cliente
        elif any(word in col_lower for word in ['destinatario', 'cliente', 'nome']):
            mapeamento_automatico['destinatario_nome'] = col

        # Placa do veículo
        elif any(word in col_lower for word in ['placa', 'veiculo', 'veículo']):
            mapeamento_automatico['veiculo_placa'] = col

        # Valor
        elif any(word in col_lower for word in ['valor', 'total', 'preco', 'preço']):
            mapeamento_automatico['valor_total'] = col

        # Data de emissão
        elif any(word in col_lower for word in ['emissao', 'emissão', 'data']):
            if 'baixa' not in col_lower:
                mapeamento_automatico['data_emissao'] = col

        # Data de baixa
        elif any(word in col_lower for word in ['baixa', 'pagamento']):
            mapeamento_automatico['data_baixa'] = col

        # Fatura
        elif any(word in col_lower for word in ['fatura', 'nota']):
            mapeamento_automatico['numero_fatura'] = col

    print(f"\n🔗 Mapeamento automático sugerido:")
    for campo_db, coluna_excel in mapeamento_automatico.items():
        print(f"  {campo_db} ← {coluna_excel}")

    return mapeamento_automatico

def validar_dados(df, mapeamento):
    """Valida os dados antes da importação"""
    print("\n✅ Validando dados...")

    problemas = []

    # Verificar se temos a coluna obrigatória numero_cte
    if 'numero_cte' not in mapeamento:
        problemas.append("❌ Coluna 'numero_cte' não encontrada")
        return False, problemas

    # Verificar duplicatas na coluna numero_cte
    col_cte = mapeamento['numero_cte']

    # Remover valores nulos/vazios
    df_clean = df[df[col_cte].notna()]
    df_clean = df_clean[df_clean[col_cte] != '']

    # Verificar duplicatas
    duplicatas = df_clean[df_clean[col_cte].duplicated()]
    if not duplicatas.empty:
        problemas.append(f"⚠️ {len(duplicatas)} registros duplicados encontrados na coluna {col_cte}")
        print("Registros duplicados:")
        print(duplicatas[[col_cte]].to_string())

    # Verificar valores inválidos
    try:
        df_clean[col_cte] = pd.to_numeric(df_clean[col_cte], errors='coerce')
        invalidos = df_clean[df_clean[col_cte].isna()]
        if not invalidos.empty:
            problemas.append(f"⚠️ {len(invalidos)} valores inválidos na coluna {col_cte}")
    except Exception:
        problemas.append(f"❌ Erro ao validar tipos de dados na coluna {col_cte}")

    print(f"📊 Registros válidos para importação: {len(df_clean)}")

    if problemas:
        print("\n⚠️ Problemas encontrados:")
        for problema in problemas:
            print(f"  {problema}")

    return len(problemas) == 0 or input("\n❓ Continuar mesmo com problemas? (s/N): ").lower() == 's', problemas

def importar_dados(df, mapeamento):
    """Importa os dados para o banco de dados"""
    try:
        from app import create_app, db
        from app.models.cte import CTE

        print("\n🚀 Iniciando importação...")

        # Criar aplicação
        app = create_app()

        with app.app_context():
            # Preparar dados
            col_cte = mapeamento['numero_cte']
            df_clean = df[df[col_cte].notna()]
            df_clean = df_clean[df_clean[col_cte] != '']

            # Converter numero_cte para inteiro
            df_clean = df_clean.copy()
            df_clean[col_cte] = pd.to_numeric(df_clean[col_cte], errors='coerce')
            df_clean = df_clean[df_clean[col_cte].notna()]

            print(f"📊 Processando {len(df_clean)} registros...")

            # Verificar CTEs existentes no banco
            numeros_cte = df_clean[col_cte].astype(int).tolist()
            ctes_existentes = CTE.obter_ctes_existentes_bulk(numeros_cte)

            print(f"🔍 {len(ctes_existentes)} CTEs já existem no banco")

            # Filtrar apenas novos registros
            df_novos = df_clean[~df_clean[col_cte].isin(ctes_existentes)]
            print(f"✨ {len(df_novos)} CTEs novos serão importados")

            if df_novos.empty:
                print("ℹ️ Nenhum registro novo para importar")
                return True

            # Importar em lotes
            lote_size = 100
            total_importados = 0
            total_erros = 0

            for i in range(0, len(df_novos), lote_size):
                lote = df_novos.iloc[i:i+lote_size]
                print(f"📦 Processando lote {i//lote_size + 1} ({len(lote)} registros)...")

                for _, row in lote.iterrows():
                    try:
                        # Preparar dados para o CTE
                        dados_cte = {}

                        for campo_db, coluna_excel in mapeamento.items():
                            if coluna_excel in row.index:
                                valor = row[coluna_excel]
                                if pd.notna(valor) and valor != '':
                                    dados_cte[campo_db] = valor

                        # Criar CTE
                        sucesso, resultado = CTE.criar_cte(dados_cte)

                        if sucesso:
                            total_importados += 1
                        else:
                            total_erros += 1
                            logger.warning(f"Erro ao criar CTE {dados_cte.get('numero_cte')}: {resultado}")

                    except Exception as e:
                        total_erros += 1
                        logger.error(f"Erro ao processar registro: {e}")

                # Commit do lote
                try:
                    db.session.commit()
                    print(f"✅ Lote {i//lote_size + 1} processado")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Erro ao salvar lote: {e}")

            print(f"\n📈 Importação concluída:")
            print(f"  ✅ Importados com sucesso: {total_importados}")
            print(f"  ❌ Erros: {total_erros}")
            print(f"  🔄 CTEs já existentes (ignorados): {len(ctes_existentes)}")

            return True

    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        print(f"❌ Erro na importação: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 IMPORTADOR DE PLANILHA BAKER DASHBOARD")
    print("=" * 60)

    # Caminho da planilha
    caminho_planilha = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

    if not os.path.exists(caminho_planilha):
        print(f"❌ Planilha não encontrada: {caminho_planilha}")
        return False

    print(f"📁 Planilha: {caminho_planilha}")

    # Passo 1: Analisar planilha
    df, planilhas = analisar_planilha(caminho_planilha)
    if df is None:
        return False

    # Passo 2: Mapear colunas
    mapeamento = mapear_colunas(df)

    # Permitir ajustes manuais do mapeamento
    print("\n❓ Deseja ajustar o mapeamento? (s/N): ", end='')
    if input().lower() == 's':
        print("\nColunas disponíveis:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")

        print("\nDigite o número da coluna para cada campo (Enter para manter atual):")

        campos_db = ['numero_cte', 'destinatario_nome', 'veiculo_placa', 'valor_total',
                    'data_emissao', 'data_baixa', 'numero_fatura']

        for campo in campos_db:
            atual = mapeamento.get(campo, "Não mapeado")
            print(f"{campo} (atual: {atual}): ", end='')
            entrada = input().strip()
            if entrada.isdigit():
                idx = int(entrada)
                if 0 <= idx < len(df.columns):
                    mapeamento[campo] = df.columns[idx]

    # Passo 3: Validar dados
    valido, problemas = validar_dados(df, mapeamento)
    if not valido:
        print("❌ Validação falhou. Abortando importação.")
        return False

    # Passo 4: Confirmar importação
    print(f"\n🎯 Pronto para importar!")
    print(f"📊 Registros na planilha: {len(df)}")
    print("📝 Mapeamento final:")
    for campo_db, coluna_excel in mapeamento.items():
        print(f"  {campo_db} ← {coluna_excel}")

    print("\n❓ Confirmar importação? (s/N): ", end='')
    if input().lower() != 's':
        print("🚫 Importação cancelada pelo usuário")
        return False

    # Passo 5: Importar dados
    sucesso = importar_dados(df, mapeamento)

    if sucesso:
        print("\n🎉 Importação concluída com sucesso!")
    else:
        print("\n❌ Importação falhou")

    return sucesso

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🚫 Importação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {e}")
        print(f"\n💥 Erro inesperado: {e}")
    finally:
        print("\n👋 Finalizando...")