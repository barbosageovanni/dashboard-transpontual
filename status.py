#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de status do sistema - PostgreSQL (CORRIGIDO)
"""

import sys
import os
sys.path.append(os.getcwd())

def verificar_pastas():
    """Verifica pastas do sistema"""
    folders = ['uploads', 'logs', 'backups', 'reports', 'templates']
    
    for folder in folders:
        if os.path.exists(folder):
            files = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
            print(f"📁 {folder}: {files} arquivos")
        else:
            print(f"❌ {folder}: pasta não existe")

def main():
    try:
        from app import create_app, db
        from app.models.cte import CTE
        
        print("🔍 STATUS DO SISTEMA - POSTGRESQL")
        print("="*40)
        
        app = create_app()
        
        with app.app_context():
            # Testa conexão básica
            total_ctes = CTE.query.count()
            print(f"✅ Banco: Conectado")
            print(f"📊 CTEs: {total_ctes}")
            
            # Estatísticas básicas
            if total_ctes > 0:
                ctes_com_baixa = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
                ctes_com_cliente = CTE.query.filter(CTE.destinatario_nome.isnot(None)).count()
                ctes_com_valor = CTE.query.filter(CTE.valor_total > 0).count()
                
                print(f"📈 Com baixa: {ctes_com_baixa}")
                print(f"👥 Com cliente: {ctes_com_cliente}")
                print(f"💰 Com valor: {ctes_com_valor}")
                
                # Exemplo de CTE
                cte_exemplo = CTE.query.first()
                if cte_exemplo:
                    print(f"\n📋 Exemplo de CTE:")
                    print(f"  - Número: {cte_exemplo.numero_cte}")
                    print(f"  - Cliente: {cte_exemplo.destinatario_nome or 'Não informado'}")
                    print(f"  - Valor: R$ {cte_exemplo.valor_total or 0}")
                    print(f"  - Emissão: {cte_exemplo.data_emissao or 'Não informado'}")
            
            # Verifica estrutura das pastas
            print(f"\n📁 Estrutura de pastas:")
            verificar_pastas()
            
            # Verifica arquivos principais
            print(f"\n📄 Arquivos do sistema:")
            arquivos_principais = [
                'bulk_update_cte.py',
                'bulk_config.py', 
                'bulk_helper.py',
                'quick_run.py'
            ]
            
            for arquivo in arquivos_principais:
                if os.path.exists(arquivo):
                    print(f"✅ {arquivo}")
                else:
                    print(f"❌ {arquivo} - NÃO ENCONTRADO")
            
            print("\n✅ Sistema funcionando normalmente")
            print("\n💡 Próximos passos:")
            print("  1. Execute: python quick_run.py")
            print("  2. Escolha opção 1 para gerar template")
            print("  3. Edite o template com seus dados")
            print("  4. Execute atualização")

    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        print("💡 Verifique se está no diretório correto do projeto Flask")
        print("💡 Certifique-se de que os modelos estão configurados")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print("💡 Verifique a conexão com o banco PostgreSQL")

if __name__ == "__main__":
    main()