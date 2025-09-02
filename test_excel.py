#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

print("Testing Excel file reading...")
try:
    df = pd.read_excel('template_test.xlsx')
    print('Excel file loaded successfully!')
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')
    print('\nFirst few rows:')
    print(df.head())
    print('\nExcel test passed!')
except Exception as e:
    print(f'Excel test failed: {e}')
    import traceback
    traceback.print_exc()
