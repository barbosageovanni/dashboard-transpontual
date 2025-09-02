#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from app.services.atualizacao_service import AtualizacaoService
    print("Import ok")
    
    # Teste simples
    if hasattr(AtualizacaoService, '_limpar_valor_monetario'):
        print("Método _limpar_valor_monetario encontrado")
        result = AtualizacaoService._limpar_valor_monetario("R$ 1.500,50")
        print(f"Teste: R$ 1.500,50 -> {result}")
    else:
        print("Método _limpar_valor_monetario NÃO encontrado")
        print("Métodos disponíveis:")
        for attr in dir(AtualizacaoService):
            if not attr.startswith('__'):
                print(f"  - {attr}")
                
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
