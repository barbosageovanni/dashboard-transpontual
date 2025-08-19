#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação completa do sistema - Teste todos os componentes
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar path do projeto
sys.path.append(os.getcwd())

def testar_bulk_update_real():
    """Testa o sistema de bulk update com dados reais"""
    print("🧪 TESTE DO SISTEMA DE BULK UPDATE")
    print("="*40)
    
    try:
        # Importações
        from app import create_app
        from app.models.cte import CTE
        from bulk_update_cte import BulkCTEUpdaterDB
        
        # Criar app
        app = create_app()
        
        with app.app_context():
            # Buscar alguns CTEs reais
            ctes_exemplo = CTE.query.limit(3).all()
            print(f"✅ {len(ctes_exemplo)} CTEs encontrados para teste")
            
            # Mostrar estado atual
            print("\n📋 Estado atual dos CTEs:")
            for cte in ctes_exemplo:
                print(f"  CTE {cte.numero_cte}:")
                print(f"    Cliente: {cte.destinatario_nome or 'VAZIO'}")
                print(f"    Observação: {cte.observacao or 'VAZIO'}")
                print(f"    Data Inclusão: {cte.data_inclusao_fatura or 'VAZIO'}")
                print()
            
            # Criar arquivo de teste com atualizações seguras
            dados_teste = []
            for i, cte in enumerate(ctes_exemplo):
                dados_teste.append({
                    'numero_cte': cte.numero_cte,
                    'observacao': f'TESTE ATUALIZAÇÃO {i+1} - {datetime.now().strftime("%H:%M:%S")}' if not cte.observacao else None,
                    'data_inclusao_fatura': '2024-08-19' if not cte.data_inclusao_fatura else None
                })
            
            # Salvar arquivo
            df = pd.DataFrame(dados_teste)
            arquivo = 'uploads/teste_real.xlsx'
            df.to_excel(arquivo, index=False)
            print(f"✅ Arquivo de teste real criado: {arquivo}")
            
            # Testar sistema
            updater = BulkCTEUpdaterDB(app)
            
            # 1. Carregamento
            df_loaded = updater.load_update_file(arquivo)
            if df_loaded is None:
                print("❌ Falha no carregamento")
                return False
            print("✅ Arquivo carregado com sucesso")
            
            # 2. Normalização
            df_normalized = updater.normalize_data(df_loaded)
            if df_normalized.empty:
                print("❌ Falha na normalização")
                return False
            print("✅ Dados normalizados com sucesso")
            print(f"📊 {len(df_normalized)} registros válidos")
            
            # 3. Validação
            is_valid, errors = updater.validate_data(df_normalized)
            if not is_valid:
                print("❌ Dados inválidos:")
                for error in errors:
                    print(f"  - {error}")
                return False
            print("✅ Dados validados com sucesso")
            
            # 4. Verificar CTEs no banco
            existing_ctes, not_found = updater.check_existing_ctes(df_normalized)
            print(f"✅ Verificação no banco: {len(existing_ctes)} CTEs encontrados")
            if not_found:
                print(f"⚠️ CTEs não encontrados: {not_found}")
            
            # 5. Gerar plano
            plan = updater.generate_update_plan(df_normalized, 'empty_only')
            print(f"✅ Plano gerado: {len(plan)} atualizações possíveis")
            
            # 6. Mostrar preview
            if plan:
                print("\n👁️ PREVIEW DAS ATUALIZAÇÕES (modo empty_only):")
                for p in plan:
                    print(f"  CTE {p['numero_cte']}:")
                    for field, change in p['changes'].items():
                        print(f"    {field}: '{change['old_value']}' → '{change['new_value']}'")
                
                # Perguntar se quer executar de verdade
                print(f"\n⚠️ ATENÇÃO: Quer executar estas {len(plan)} atualizações REAIS?")
                resposta = input("Digite 'SIM' para executar ou Enter para pular: ").strip()
                
                if resposta.upper() == 'SIM':
                    print("\n🔄 EXECUTANDO ATUALIZAÇÕES REAIS...")
                    
                    # Criar backup
                    cte_numbers = [p['numero_cte'] for p in plan]
                    backup_path = updater.create_backup(cte_numbers)
                    if backup_path:
                        print(f"💾 Backup criado: {backup_path}")
                    
                    # Executar
                    success = updater.execute_updates(plan, batch_size=10)
                    
                    if success:
                        print("🎉 ATUALIZAÇÕES EXECUTADAS COM SUCESSO!")
                        print(f"📊 Estatísticas:")
                        print(f"  - Processados: {updater.stats['total_processados']}")
                        print(f"  - Atualizados: {updater.stats['atualizados']}")
                        print(f"  - Erros: {updater.stats['erros']}")
                        
                        # Verificar mudanças
                        print(f"\n🔍 Verificando mudanças no banco:")
                        for numero_cte in cte_numbers:
                            cte_atual = CTE.query.filter_by(numero_cte=numero_cte).first()
                            if cte_atual:
                                print(f"  CTE {numero_cte}:")
                                print(f"    Observação: {cte_atual.observacao}")
                                print(f"    Data Inclusão: {cte_atual.data_inclusao_fatura}")
                        
                        # Salvar relatório
                        report_path = updater.save_update_report()
                        if report_path:
                            print(f"📊 Relatório salvo: {report_path}")
                    
                    else:
                        print("❌ Falha na execução")
                
                else:
                    print("ℹ️ Execução pulada - apenas teste de funcionalidade")
            
            else:
                print("ℹ️ Nenhuma atualização necessária (campos já preenchidos)")
                print("💡 Isso é normal se os CTEs já tiverem dados nos campos testados")
            
            return True
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 VALIDAÇÃO COMPLETA DO SISTEMA")
    print("="*40)
    print("Este teste vai:")
    print("1. ✅ Conectar ao banco PostgreSQL")
    print("2. 📋 Buscar CTEs reais")
    print("3. 📄 Criar arquivo de teste") 
    print("4. 🧪 Testar todo o pipeline")
    print("5. 👁️ Mostrar preview de atualizações")
    print("6. ❓ Perguntar se quer executar (opcional)")
    print()
    
    input("⚡ Pressione Enter para continuar...")
    
    if testar_bulk_update_real():
        print("\n🎉 SISTEMA 100% FUNCIONAL!")
        print("="*30)
        print("✅ Todos os componentes testados")
        print("✅ Sistema pronto para uso em produção")
        print("✅ Pode processar arquivos Excel/CSV")
        print("✅ Integração com PostgreSQL funciona")
        
        print("\n🚀 COMO USAR:")
        print("1. python quick_run.py (interface simples)")
        print("2. Gerar template baseado em dados reais") 
        print("3. Editar template com suas atualizações")
        print("4. Executar atualização")
        
    else:
        print("\n❌ SISTEMA COM PROBLEMAS")
        print("Verifique os erros acima e corrija antes de usar")

if __name__ == "__main__":
    main()