#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

print('Testing manual templates...')

print('\n1. Testing manual CSV...')
try:
    df = pd.read_csv('manual_template.csv', sep=';')
    print(f'   ✅ CSV loaded successfully')
    print(f'   📊 Shape: {df.shape}')
    print(f'   📋 Columns: {list(df.columns)}')
    print('   📄 Data:')
    print(df)
except Exception as e:
    print(f'   ❌ CSV error: {e}')

print('\n2. Testing manual Excel...')
try:
    df_xl = pd.read_excel('manual_template.xlsx')
    print(f'   ✅ Excel loaded successfully')
    print(f'   📊 Shape: {df_xl.shape}')
    print(f'   📋 Columns: {list(df_xl.columns)}')
    print('   📄 Data:')
    print(df_xl)
except Exception as e:
    print(f'   ❌ Excel error: {e}')

print('\n🎉 Template validation completed!')
