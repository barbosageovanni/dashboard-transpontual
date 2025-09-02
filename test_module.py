#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import importlib.util

print("Testing direct module loading...")

# Test just the file existence and basic loading
spec = importlib.util.spec_from_file_location('atualizacao_service', 'app/services/atualizacao_service.py')
module = importlib.util.module_from_spec(spec)
print('Module spec created successfully')

# Try to execute the module
try:
    spec.loader.exec_module(module)
    print('Module executed successfully')
    if hasattr(module, 'AtualizacaoService'):
        print('AtualizacaoService class found!')
        
        # Test the methods
        service = module.AtualizacaoService()
        csv_template = service.template_csv()
        print(f'CSV template generated: {len(csv_template)} chars')
        
    else:
        print('AtualizacaoService class NOT found')
        print('Available attributes:', [attr for attr in dir(module) if not attr.startswith('_')])
except Exception as e:
    print(f'Module execution failed: {e}')
    import traceback
    traceback.print_exc()
