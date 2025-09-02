#!/usr/bin/env python3

# Simple test of the service file
print("Loading atualizacao_service...")

try:
    with open('app/services/atualizacao_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"File length: {len(content)} characters")
        print(f"Has 'class AtualizacaoService': {'class AtualizacaoService' in content}")
        
    # Try to exec the file directly
    namespace = {}
    exec(content, namespace)
    print(f"Namespace after exec: {list(namespace.keys())}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
