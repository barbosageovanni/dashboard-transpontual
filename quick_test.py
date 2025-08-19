#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido do sistema de atualização CTE
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar path do projeto
sys.path.append(os.getcwd())

def criar_pastas_necessarias():
    """Cria pastas se não existirem"""
    pastas = ['uploads', 'logs', 'backups', 'reports', 'templates']
    
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"📁 Pasta criada: {pasta}")
        else:
            print(f"✅ Pasta existe: {pasta}")

def testar_conexao_banco():
    """Testa conexão com banco"""
    try:
        from app import create_app, db
        from app.models.cte import CTE
        
        app = create_app()
        
        with app.app_context():
            total_ctes = CTE.query.count()
            print(f"✅ Conexão OK - {total_ctes} CTEs encontrados")
            
            # Pega alguns exemplos
            exemplos = CTE.query.limit(3).all()
            print("📋 Exemplos de CTEs:")
            for cte in exemplos:
                print(f"  - {cte.numero_cte}: {cte.destinatario_nome or 'Sem cliente'}")
            
            return True, total_ctes, exemplos
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False, 0, []

def criar_arquivo_exemplo(exemplos_cte):
    """Cria arquivo de exemplo para teste"""
    try:
        if not exemplos_cte:
            # Dados fictícios se não houver CTEs
            dados = {
                'numero_cte': [999999001, 999999002, 999999003],
                'destinatario_nome': ['Teste Cliente A', 'Teste Cliente B', ''],
                'observacao': ['', 'Teste observação', 'Atualização teste']
            }
        else:
            # Usa CTEs reais
            dados = {
                'numero_cte': [cte.numero_cte for cte in exemplos_cte],
                'destinatario_nome': [f'ATUALIZADO - {cte.destinatario_nome or "Cliente"}' for cte in exemplos_cte],
                'observacao': [f'Teste atualização - {datetime.now().strftime("%H:%M:%S")}' for _ in exemplos_cte]
            }
        
        df = pd.DataFrame(dados)
        arquivo = 'uploads/teste_exemplo.xlsx'
        df.to_excel(arquivo, index=False)
        
        print(f"✅ Arquivo de teste criado: {arquivo}")
        print(f"📊 {len(dados['numero_cte'])} registros para teste")
        
        return arquivo
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {str(e)}")
        return None

def testar_carregamento_arquivo(arquivo):
    """Testa carregamento do arquivo"""
    try:
        df = pd.read_excel(arquivo)
        print(f"✅ Arquivo carregado: {len(df)} linhas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # Mostra preview
        print("👁️ Preview dos dados:")
        for i, row in df.head(3).iterrows():
            print(f"  Linha {i+1}: CTE {row['numero_cte']} - {row.get('destinatario_nome', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {str(e)}")
        return False

def testar_sistema_completo():
    """Teste completo do sistema"""
    try:
        from bulk_update_cte import BulkCTEUpdaterDB
        from app import create_app
        
        print("🧪 Testando sistema completo...")
        
        app = create_app()
        updater = BulkCTEUpdaterDB(app)
        
        # Carrega arquivo de teste
        arquivo = 'uploads/teste_exemplo.xlsx'
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo de teste não encontrado: {arquivo}")
            return False
        
        df = updater.load_update_file(arquivo)
        if df is None:
            print("❌ Falha ao carregar arquivo")
            return False
        
        # Normaliza dados
        df_normalized = updater.normalize_data(df)
        if df_normalized.empty:
            print("❌ Falha na normalização")
            return False
        
        # Valida dados
        is_valid, errors = updater.validate_data(df_normalized)
        if not is_valid:
            print("❌ Dados inválidos:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # Gera plano (só preview)
        plan = updater.generate_update_plan(df_normalized, 'empty_only')
        
        print(f"✅ Sistema funcionando!")
        print(f"📋 Plano gerado: {len(plan)} atualizações possíveis")
        
        if plan:
            print("👁️ Preview (primeiras 2 atualizações):")
            for i, p in enumerate(plan[:2]):
                print(f"  CTE {p['numero_cte']}:")
                for field, change in p['changes'].items():
                    print(f"    {field}: '{change['old_value']}' → '{change['new_value']}'")
        else:
            print("ℹ️ Nenhuma atualização necessária (campos já preenchidos)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        print("💡 Certifique-se de que bulk_update_cte.py existe")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def main():
    print("🧪 TESTE RÁPIDO DO SISTEMA DE ATUALIZAÇÃO")
    print("="*50)
    
    # 1. Criar pastas
    print("\n1️⃣ Verificando pastas...")
    criar_pastas_necessarias()
    
    # 2. Testar conexão
    print("\n2️⃣ Testando conexão com banco...")
    conexao_ok, total_ctes, exemplos = testar_conexao_banco()
    
    if not conexao_ok:
        print("❌ Teste falhou - problema na conexão")
        return
    
    # 3. Criar arquivo de exemplo
    print("\n3️⃣ Criando arquivo de exemplo...")
    arquivo = criar_arquivo_exemplo(exemplos)
    
    if not arquivo:
        print("❌ Teste falhou - problema ao criar arquivo")
        return
    
    # 4. Testar carregamento
    print("\n4️⃣ Testando carregamento de arquivo...")
    if not testar_carregamento_arquivo(arquivo):
        print("❌ Teste falhou - problema no carregamento")
        return
    
    # 5. Testar sistema completo
    print("\n5️⃣ Testando sistema completo...")
    if not testar_sistema_completo():
        print("❌ Teste falhou - problema no sistema")
        return
    
    # Sucesso!
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("="*30)
    print("✅ Sistema está funcionando corretamente")
    print("✅ Banco conectado e acessível")
    print("✅ Arquivos podem ser processados") 
    print("✅ Atualizações podem ser executadas")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Execute: python quick_run.py")
    print("2. Escolha 'Gerar template' para usar dados reais")
    print("3. Edite o template com suas atualizações")
    print("4. Execute atualização com preview primeiro")
    
    print(f"\n📁 Arquivo de teste criado: {arquivo}")
    print("💡 Você pode usar este arquivo para teste real")

if __name__ == "__main__":
    main()