#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    print("1. Testing basic imports...")
    from app.services.atualizacao_service import AtualizacaoService
    print("2. Import successful!")
    
    print("3. Testing CSV template...")
    csv_content = AtualizacaoService.template_csv()
    print(f"4. CSV template length: {len(csv_content)}")
    
    print("5. CSV content preview:")
    lines = csv_content.strip().split('\n')
    for i, line in enumerate(lines[:3]):
        print(f"   Line {i+1}: {line}")
    
    print("6. Testing Excel template...")
    excel_buffer = AtualizacaoService.template_excel()
    print(f"7. Excel buffer size: {excel_buffer.getbuffer().nbytes} bytes")
    
    print("8. All tests passed!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
