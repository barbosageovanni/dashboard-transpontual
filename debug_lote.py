#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da atualização em lote
debug_lote.py
"""

import pandas as pd
import io

# Simular o alias do serviço
ALIAS_COLUNAS = {
    "Número CTE": "numero_cte",
    "Cliente": "destinatario_nome", 
    "Placa Veículo": "veiculo_placa",
    "Valor Total": "valor_total",
    "Data Emissão": "data_emissao",
    "Observação": "observacao",
}

def debug_csv():
    """Debug do processamento CSV"""
    
    print("🔍 DEBUG DO PROCESSAMENTO CSV")
    print("=" * 50)
    
    # CSV original
    csv_content = """Número CTE,Cliente,Placa Veículo,Valor Total,Data Emissão,Observação
777777,Teste Lote 1,ABC-1111,1000.50,2025-08-23,Teste via lote
777778,Teste Lote 2,ABC-2222,2000.75,2025-08-23,Segundo teste
"""
    
    print("📄 CSV original:")
    print(csv_content)
    
    # Ler como DataFrame
    df = pd.read_csv(io.StringIO(csv_content))
    
    print("📊 DataFrame inicial:")
    print(f"Colunas: {list(df.columns)}")
    print(df)
    
    # Aplicar normalização
    print("\n🔄 Aplicando normalização de colunas...")
    mapping = {}
    for col in df.columns:
        mapping[col] = ALIAS_COLUNAS.get(col, col)
    
    print(f"Mapping: {mapping}")
    
    df_norm = df.rename(columns=mapping)
    
    print(f"Colunas após normalização: {list(df_norm.columns)}")
    print(df_norm)
    
    # Verificar se numero_cte existe
    if "numero_cte" in df_norm.columns:
        print("✅ Coluna numero_cte encontrada!")
        print(f"Valores: {df_norm['numero_cte'].tolist()}")
        
        # Testar conversão
        for idx, row in df_norm.iterrows():
            numero = row.get("numero_cte")
            print(f"Linha {idx}: numero_cte = {numero} (tipo: {type(numero)})")
            
            if pd.isna(numero) or numero in (None, ""):
                print(f"  ❌ Linha {idx}: Número vazio/nulo")
            else:
                try:
                    numero_int = int(float(str(numero).strip()))
                    print(f"  ✅ Linha {idx}: Convertido para {numero_int}")
                except Exception as e:
                    print(f"  ❌ Linha {idx}: Erro na conversão: {e}")
    else:
        print("❌ Coluna numero_cte NÃO encontrada!")

if __name__ == "__main__":
    debug_csv()
