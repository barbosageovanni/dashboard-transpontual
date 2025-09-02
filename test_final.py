#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')

try:
    print("Importing AtualizacaoService...")
    from app.services.atualizacao_service import AtualizacaoService
    print("Import successful!")
    
    print("Testing CSV template...")
    csv = AtualizacaoService.template_csv()
    print(f"CSV template: {len(csv)} chars")
    
    print("Testing Excel template...")
    excel = AtualizacaoService.template_excel()
    print(f"Excel template: {excel.getbuffer().nbytes} bytes")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
