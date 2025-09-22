#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da importacao - identificar problemas especificos
"""

import os
import sys
import pandas as pd
import logging

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_planilha():
    """Debug detalhado da planilha"""
    caminho = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

    print("DEBUG - Analisando planilha detalhadamente")

    try:
        # Ler planilha
        excel_file = pd.ExcelFile(caminho)
        print(f"Planilhas: {excel_file.sheet_names}")

        # Tentar cada planilha
        for sheet_name in excel_file.sheet_names:
            print(f"\nAnalisando planilha: {sheet_name}")
            df = pd.read_excel(caminho, sheet_name=sheet_name)

            print(f"  Dimensoes: {df.shape}")
            print(f"  Colunas ({len(df.columns)}):")

            for i, col in enumerate(df.columns):
                # Estatisticas da coluna
                non_null = df[col].notna().sum()
                null_count = df[col].isna().sum()
                unique_vals = df[col].nunique()

                print(f"    {i+1:2d}. '{col}' -> {non_null} validos, {null_count} nulos, {unique_vals} unicos")

                # Mostrar sample de valores
                sample_vals = df[col].dropna().head(3).tolist()
                print(f"        Exemplo: {sample_vals}")

                # Verificar se pode ser numero_cte
                if any(word in col.lower() for word in ['cte', 'numero', 'num']):
                    print(f"        >>> POSSIVEL NUMERO_CTE!")
                    try:
                        # Tentar converter para numerico
                        numeric_vals = pd.to_numeric(df[col], errors='coerce')
                        valid_numbers = numeric_vals.dropna()
                        print(f"        >>> {len(valid_numbers)} valores numericos validos")
                        if len(valid_numbers) > 0:
                            print(f"        >>> Range: {valid_numbers.min()} - {valid_numbers.max()}")

                            # Verificar duplicatas
                            duplicates = valid_numbers[valid_numbers.duplicated()]
                            print(f"        >>> Duplicatas: {len(duplicates)}")

                            if len(duplicates) > 0:
                                print(f"        >>> Numeros duplicados: {duplicates.head(5).tolist()}")

                    except Exception as e:
                        print(f"        >>> Erro ao analisar numericamente: {e}")

            print(f"\nPreview da planilha {sheet_name}:")
            print(df.head(2).to_string())
            print("-" * 80)

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG IMPORTACAO DASHBOARD BAKER")
    print("=" * 60)

    debug_planilha()

    print("\nDebug concluido!")