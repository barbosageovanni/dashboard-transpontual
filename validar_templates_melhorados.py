#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

print("=== VALIDANDO TEMPLATES MELHORADOS ===")

print("\n1. Validando CSV...")
try:
    df_csv = pd.read_csv('template_cte_melhorado.csv', sep=';')
    print(f"   📊 Shape: {df_csv.shape}")
    print(f"   📋 Colunas: {list(df_csv.columns)}")
    print("   📄 Primeiras linhas:")
    print(df_csv.head())
    
    print("\n   📝 CSV com instruções removidas:")
    df_csv_clean = pd.read_csv('template_cte_melhorado.csv', sep=';', skiprows=1)
    print(f"      Shape: {df_csv_clean.shape}")
    print(df_csv_clean.head())
    
except Exception as e:
    print(f"   ❌ Erro CSV: {e}")

print("\n2. Validando Excel...")
try:
    df_excel = pd.read_excel('template_cte_melhorado.xlsx')
    print(f"   📊 Shape: {df_excel.shape}")
    print(f"   📋 Colunas: {list(df_excel.columns)}")
    print("   📄 Primeiras linhas:")
    print(df_excel.head())
    
    print("\n   📝 Excel com instruções removidas:")
    df_excel_clean = pd.read_excel('template_cte_melhorado.xlsx', skiprows=1)
    print(f"      Shape: {df_excel_clean.shape}")
    print(df_excel_clean.head())
    
except Exception as e:
    print(f"   ❌ Erro Excel: {e}")

print("\n🎉 Validação concluída!")
