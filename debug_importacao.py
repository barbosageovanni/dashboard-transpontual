#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da importação - identificar problemas específicos
"""

import os
import sys
import pandas as pd
import logging

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_planilha():
    """Debug detalhado da planilha"""
    caminho = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

    print("DEBUG - Analisando planilha detalhadamente")

    try:
        # Ler planilha
        excel_file = pd.ExcelFile(caminho)
        print(f"Planilhas: {excel_file.sheet_names}")

        # Tentar cada planilha
        for sheet_name in excel_file.sheet_names:
            print(f"\nAnalisando planilha: {sheet_name}")
            df = pd.read_excel(caminho, sheet_name=sheet_name)

            print(f"  Dimensoes: {df.shape}")
            print(f"  Colunas ({len(df.columns)}):")

            for i, col in enumerate(df.columns):
                # Estatísticas da coluna
                non_null = df[col].notna().sum()
                null_count = df[col].isna().sum()
                unique_vals = df[col].nunique()

                print(f"    {i+1:2d}. '{col}' -> {non_null} válidos, {null_count} nulos, {unique_vals} únicos")

                # Mostrar sample de valores
                sample_vals = df[col].dropna().head(3).tolist()
                print(f"        Exemplo: {sample_vals}")

                # Verificar se pode ser numero_cte
                if any(word in col.lower() for word in ['cte', 'número', 'num']):
                    print(f"        🎯 POSSÍVEL NUMERO_CTE!")
                    try:
                        # Tentar converter para numérico
                        numeric_vals = pd.to_numeric(df[col], errors='coerce')
                        valid_numbers = numeric_vals.dropna()
                        print(f"        📊 {len(valid_numbers)} valores numéricos válidos")
                        print(f"        🔢 Range: {valid_numbers.min()} - {valid_numbers.max()}")

                        # Verificar duplicatas
                        duplicates = valid_numbers[valid_numbers.duplicated()]
                        print(f"        🔄 Duplicatas: {len(duplicates)}")

                        if len(duplicates) > 0:
                            print(f"        ❌ Números duplicados: {duplicates.head(5).tolist()}")

                    except Exception as e:
                        print(f"        ❌ Erro ao analisar numericamente: {e}")

            print(f"\n👀 Preview da planilha {sheet_name}:")
            print(df.head(2).to_string())
            print("-" * 80)

    except Exception as e:
        print(f"❌ Erro: {e}")

def debug_conexao_db():
    """Debug da conexão com o banco"""
    print("\n🔗 DEBUG - Testando conexão com banco")

    try:
        from app import create_app, db
        from app.models.cte import CTE

        app = create_app()

        with app.app_context():
            print("✅ App criado com sucesso")

            # Testar conexão
            result = db.engine.execute("SELECT 1")
            print("✅ Conexão com banco OK")

            # Verificar tabela
            result = db.engine.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'dashboard_baker'
                ORDER BY ordinal_position
            """)

            print("📋 Estrutura da tabela dashboard_baker:")
            for row in result:
                print(f"  {row[0]} | {row[1]} | Null: {row[2]} | Default: {row[3]}")

            # Contar registros existentes
            count = CTE.query.count()
            print(f"📊 CTEs existentes no banco: {count}")

            # Testar criação de CTE simples
            print("\n🧪 Testando criação de CTE...")
            dados_teste = {
                'numero_cte': 999999,
                'destinatario_nome': 'Teste Debug',
                'valor_total': 100.50,
                'origem_dados': 'Debug'
            }

            sucesso, resultado = CTE.criar_cte(dados_teste)

            if sucesso:
                print("✅ Teste de criação OK")
                # Remover o teste
                cte_teste = CTE.buscar_por_numero(999999)
                if cte_teste:
                    cte_teste.deletar()
                    print("🗑️ CTE de teste removido")
            else:
                print(f"❌ Erro no teste de criação: {resultado}")

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        import traceback
        traceback.print_exc()

def simular_importacao():
    """Simula a importação com apenas 1 registro para debug"""
    print("\n🧪 SIMULAÇÃO - Importação de 1 registro")

    caminho = r'C:\Users\Geovane\Documents\Transpontual\3) Departamento Financeiro\1) Financeiro\1) Relatórios\Sistema Faturamento site\Backup dados 15set2025.xlsx'

    try:
        from app import create_app, db
        from app.models.cte import CTE

        # Ler planilha
        df = pd.read_excel(caminho, sheet_name=0)
        print(f"📊 Planilha carregada: {len(df)} registros")

        # Pegar apenas o primeiro registro
        primeiro_registro = df.iloc[0]
        print("\n📝 Primeiro registro:")
        for col, val in primeiro_registro.items():
            print(f"  {col}: {val} (tipo: {type(val)})")

        # Tentar identificar numero_cte automaticamente
        possible_cte_cols = []
        for col in df.columns:
            if any(word in col.lower() for word in ['cte', 'número', 'num']):
                possible_cte_cols.append(col)

        print(f"\n🎯 Possíveis colunas CTE: {possible_cte_cols}")

        if not possible_cte_cols:
            print("❌ Nenhuma coluna CTE identificada automaticamente")
            print("📝 Todas as colunas disponíveis:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col}")
            return

        # Usar a primeira coluna encontrada
        col_cte = possible_cte_cols[0]
        numero_cte_raw = primeiro_registro[col_cte]

        print(f"\n🔢 Tentando extrair numero_cte de '{col_cte}': {numero_cte_raw}")

        # Tentar converter
        try:
            numero_cte = int(float(str(numero_cte_raw)))
            print(f"✅ Número CTE convertido: {numero_cte}")
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            return

        # Criar app e tentar importar
        app = create_app()
        with app.app_context():
            # Preparar dados mínimos
            dados_cte = {
                'numero_cte': numero_cte,
                'origem_dados': 'Debug Import'
            }

            # Tentar mapear outros campos
            for col, val in primeiro_registro.items():
                if pd.notna(val) and val != '':
                    col_lower = col.lower()

                    if any(word in col_lower for word in ['destinatario', 'cliente', 'nome']) and 'numero_cte' not in dados_cte.get('destinatario_nome', ''):
                        dados_cte['destinatario_nome'] = str(val)[:255]

                    elif any(word in col_lower for word in ['placa', 'veiculo']):
                        dados_cte['veiculo_placa'] = str(val)[:20]

                    elif any(word in col_lower for word in ['valor', 'total']) and col != col_cte:
                        try:
                            valor_str = str(val).replace(',', '.').replace('R$', '').strip()
                            dados_cte['valor_total'] = float(valor_str)
                        except:
                            pass

            print(f"\n📦 Dados preparados para CTE:")
            for campo, valor in dados_cte.items():
                print(f"  {campo}: {valor}")

            # Tentar criar
            print(f"\n🚀 Tentando criar CTE...")
            sucesso, resultado = CTE.criar_cte(dados_cte)

            if sucesso:
                print("✅ CTE criado com sucesso!")
                print(f"📊 CTE: {resultado}")

                # Verificar se foi realmente salvo
                cte_verificacao = CTE.buscar_por_numero(numero_cte)
                if cte_verificacao:
                    print("✅ Verificação: CTE encontrado no banco")
                    print(f"📋 Dados salvos: {cte_verificacao.to_dict()}")
                else:
                    print("❌ Verificação: CTE não encontrado no banco!")

            else:
                print(f"❌ Erro ao criar CTE: {resultado}")

    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG IMPORTACAO DASHBOARD BAKER")
    print("=" * 60)

    debug_planilha()
    debug_conexao_db()
    simular_importacao()

    print("\nDebug concluido!")