#!/usr/bin/env python3
# Correção do frontend - força atualização dos templates

import os
import re

def corrigir_templates():
    # Procurar arquivos de template
    for root, dirs, files in os.walk('app/templates'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                print(f"Verificando: {filepath}")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Adicionar data attributes para facilitar JavaScript
                if 'id="totalCtes"' in content:
                    content = content.replace('id="totalCtes"', 'id="totalCtes" data-metric="total_ctes"')
                
                # Salvar se modificado
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

if __name__ == "__main__":
    corrigir_templates()