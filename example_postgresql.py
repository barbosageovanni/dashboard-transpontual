# example_postgresql.py
"""
Exemplo prático de uso do sistema de atualização em lote - PostgreSQL Supabase
Demonstra uso completo com o banco de dados existente
"""

import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.cte import CTE
from bulk_update_cte import BulkCTEUpdaterDB
from bulk_helper import BulkUpdateHelper

def demonstracao_completa():
    """
    Demonstra fluxo completo de atualização no PostgreSQL
    """
    
    print("🎯 DEMONSTRAÇÃO COMPLETA - POSTGRESQL SUPABASE")
    print("="*60)
    
    # ============================================================================
    # PASSO 1: VERIFICAR CONEXÃO E DADOS EXISTENTES
    # ============================================================================
    print("\n📊 PASSO 1: Verificando banco de dados...")
    
    app = create_app()
    
    try:
        with app.app_context():
            # Testa conexão
            total_ctes = CTE.query.count()
            print(f"✅ Conectado ao Supabase PostgreSQL")
            print(f"📊 Total de CTEs no banco: {total_ctes}")
            
            if total_ctes == 0:
                print("⚠️ Banco vazio - criando dados de exemplo...")
                criar_dados_exemplo()
                total_ctes = CTE.query.count()
                print(f"✅ {total_ctes} CTEs de exemplo criados")
            
            # Mostra estatísticas
            helper = BulkUpdateHelper()
            stats = helper.get_database_statistics()
            
            print(f"📈 Estatísticas:")
            print(f"  - CTEs com baixa: {stats['ctes_with_baixa']}")
            print(f"  - Processos completos: {stats['ctes_complete_process']}")
            
            # Mostra alguns CTEs de exemplo
            print(f"\n📋 Exemplos de CTEs no banco:")
            sample_ctes = CTE.query.limit(5).all()
            for cte in sample_ctes:
                print(f"  - CTE {cte.numero_cte}: {cte.destinatario_nome or 'Sem cliente'}")
                print(f"    Valor: R$ {cte.valor_total or 0}")
                print(f"    Emissão: {cte.data_emissao or 'Não informado'}")
                print(f"    Baixa: {cte.data_baixa or 'Pendente'}")
                print()
                
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        print("🔧 Verifique se o servidor Flask está configurado corretamente")
        return False
    
    # ============================================================================
    # PASSO 2: GERAR TEMPLATE BASEADO EM DADOS REAIS
    # ============================================================================
    print("\n📋 PASSO 2: Gerando template baseado no banco...")
    
    helper = BulkUpdateHelper()
    template_path = helper.generate_sample_template(
        output_path='uploads/template_exemplo_real.xlsx',
        num_samples=20
    )
    
    if template_path:
        print(f"✅ Template gerado: {template_path}")
        print("📄 O template contém:")
        print("  - Dados reais mascarados do seu banco")
        print("  - Instruções detalhadas")
        print("  - Mapeamento de colunas")
        print("  - Exemplos de formatos")
    
    # ============================================================================
    # PASSO 3: CRIAR ARQUIVO DE ATUALIZAÇÃO DE EXEMPLO
    # ============================================================================
    print("\n🔄 PASSO 3: Criando arquivo de atualização de exemplo...")
    
    # Pega alguns CTEs reais para usar como base
    with app.app_context():
        ctes_para_atualizar = CTE.query.limit(10).all()
        
        dados_atualizacao = []
        
        for i, cte in enumerate(ctes_para_atualizar):
            # Simula atualizações típicas
            dados_atualizacao.append({
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome or f'Cliente Atualizado {i+1}',
                'veiculo_placa': cte.veiculo_placa or f'ABC-{1000+i}',
                'valor_total': float(cte.valor_total or 0) + (i * 100),  # Simula correção de valor
                'data_inclusao_fatura': (datetime.now() - timedelta(days=i*2)).strftime('%Y-%m-%d') if not cte.data_inclusao_fatura else None,
                'primeiro_envio': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') if not cte.primeiro_envio else None,
                'data_atesto': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') if not cte.data_atesto else None,
                'observacao': f'Atualização exemplo {i+1} - {datetime.now().strftime("%d/%m/%Y")}'
            })
    
    # Salva arquivo de exemplo
    df_exemplo = pd.DataFrame(dados_atualizacao)
    arquivo_exemplo = 'uploads/atualizacao_exemplo.xlsx'
    df_exemplo.to_excel(arquivo_exemplo, index=False)
    
    print(f"✅ Arquivo de exemplo criado: {arquivo_exemplo}")
    print(f"📊 {len(dados_atualizacao)} CTEs preparados para atualização")
    
    # ============================================================================
    # PASSO 4: VALIDAR ARQUIVO
    # ============================================================================
    print("\n🔍 PASSO 4: Validando arquivo de atualização...")
    
    resultado_validacao = helper.validate_upload_file(arquivo_exemplo)
    
    print(f"✅ Arquivo válido: {resultado_validacao['valid']}")
    
    if resultado_validacao['errors']:
        print("❌ Erros encontrados:")
        for erro in resultado_validacao['errors']:
            print(f"  - {erro}")
        return False
    
    if resultado_validacao['warnings']:
        print("⚠️ Avisos:")
        for aviso in resultado_validacao['warnings']:
            print(f"  - {aviso}")
    
    print("📊 Estatísticas do arquivo:")
    stats = resultado_validacao['statistics']
    print(f"  - Total de linhas: {stats['total_rows']}")
    print(f"  - CTEs existentes no banco: {stats['ctes_existing']}")
    print(f"  - CTEs não encontrados: {stats['ctes_not_found']}")
    
    # ============================================================================
    # PASSO 5: PREVIEW DA ATUALIZAÇÃO
    # ============================================================================
    print("\n👁️ PASSO 5: Preview da atualização...")
    
    updater = BulkCTEUpdaterDB(app)
    
    # Carrega e normaliza dados
    df = updater.load_update_file(arquivo_exemplo)
    df_normalized = updater.normalize_data(df)
    
    # Gera plano (modo apenas vazios)
    plano_atualizacao = updater.generate_update_plan(df_normalized, 'empty_only')
    
    if plano_atualizacao:
        print(f"📋 Plano gerado: {len(plano_atualizacao)} CTEs serão atualizados")
        
        # Mostra preview
        updater.preview_updates(plano_atualizacao, max_preview=5)
        
        # ========================================================================
        # PASSO 6: EXECUÇÃO (COM CONFIRMAÇÃO)
        # ========================================================================
        print("\n⚠️ PASSO 6: Execução da atualização...")
        
        executar = input("▶️ Deseja executar as atualizações? (s/N): ").lower()
        
        if executar in ['s', 'sim', 'y', 'yes']:
            # Cria backup
            print("💾 Criando backup...")
            cte_numbers = [plan['numero_cte'] for plan in plano_atualizacao]
            backup_path = updater.create_backup(cte_numbers)
            
            if backup_path:
                print(f"✅ Backup criado: {backup_path}")
            
            # Executa atualizações
            print("🔄 Executando atualizações...")
            sucesso = updater.execute_updates(plano_atualizacao, batch_size=50)
            
            if sucesso:
                print("🎉 Atualizações concluídas com sucesso!")
                
                # Mostra estatísticas finais
                print(f"\n📊 ESTATÍSTICAS FINAIS:")
                print(f"  - Processados: {updater.stats['total_processados']}")
                print(f"  - Atualizados: {updater.stats['atualizados']}")
                print(f"  - Sem alteração: {updater.stats['sem_alteracao']}")
                print(f"  - Erros: {updater.stats['erros']}")
                
                if updater.stats['campos_atualizados']:
                    print(f"\n📋 Campos mais atualizados:")
                    for campo, count in updater.stats['campos_atualizados'].items():
                        print(f"  - {campo}: {count} atualizações")
                
                # Gera relatório
                relatorio_path = updater.save_update_report()
                if relatorio_path:
                    print(f"📊 Relatório salvo: {relatorio_path}")
                
                # Verifica dados atualizados
                print(f"\n🔍 Verificando atualizações no banco...")
                verificar_atualizacoes(app, cte_numbers[:5])  # Verifica primeiros 5
                
            else:
                print("❌ Falha na execução das atualizações")
                print("📄 Verifique os logs para mais detalhes")
        
        else:
            print("⏸️ Execução cancelada pelo usuário")
    
    else:
        print("ℹ️ Nenhuma atualização necessária com o modo 'empty_only'")
        print("💡 Tente o modo 'all' para forçar atualizações")
    
    print("\n✅ Demonstração concluída!")

def criar_dados_exemplo():
    """
    Cria dados de exemplo no banco se estiver vazio
    """
    try:
        # Dados fictícios para demonstração
        ctes_exemplo = []
        
        for i in range(1, 21):  # 20 CTEs de exemplo
            cte = CTE(
                numero_cte=202410000 + i,
                destinatario_nome=f'Empresa Exemplo {i}' if i % 3 != 0 else None,
                veiculo_placa=f'ABC-{1000+i}' if i % 4 != 0 else None,
                valor_total=Decimal(f'{1000 + (i * 123.45):.2f}'),
                data_emissao=datetime.now().date() - timedelta(days=i),
                data_baixa=datetime.now().date() - timedelta(days=i//2) if i % 5 == 0 else None,
                numero_fatura=f'FAT{2024}{str(i).zfill(4)}' if i % 3 == 0 else None,
                observacao=f'CTE de exemplo {i}' if i % 6 == 0 else None,
                origem_dados='Exemplo Sistema'
            )
            ctes_exemplo.append(cte)
        
        # Salva no banco
        for cte in ctes_exemplo:
            db.session.add(cte)
        
        db.session.commit()
        
        print(f"✅ {len(ctes_exemplo)} CTEs de exemplo criados")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar dados de exemplo: {str(e)}")

def verificar_atualizacoes(app, cte_numbers):
    """
    Verifica se as atualizações foram aplicadas corretamente
    """
    try:
        with app.app_context():
            print("🔍 Verificando atualizações aplicadas:")
            
            for numero_cte in cte_numbers:
                cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                if cte:
                    print(f"\n📋 CTE {numero_cte}:")
                    print(f"  - Cliente: {cte.destinatario_nome}")
                    print(f"  - Placa: {cte.veiculo_placa}")
                    print(f"  - Valor: R$ {cte.valor_total}")
                    print(f"  - Inclusão Fatura: {cte.data_inclusao_fatura}")
                    print(f"  - Primeiro Envio: {cte.primeiro_envio}")
                    print(f"  - Atesto: {cte.data_atesto}")
                    print(f"  - Observação: {cte.observacao}")
                    print(f"  - Última atualização: {cte.updated_at}")
                else:
                    print(f"❌ CTE {numero_cte} não encontrado")
    
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")

def teste_performance():
    """
    Testa performance com volume maior de dados
    """
    print("\n🚀 TESTE DE PERFORMANCE")
    print("="*40)
    
    app = create_app()
    
    try:
        with app.app_context():
            # Conta total de CTEs
            total_ctes = CTE.query.count()
            print(f"📊 Total de CTEs no banco: {total_ctes}")
            
            if total_ctes < 100:
                print("⚠️ Banco com poucos registros para teste de performance")
                return
            
            # Cria arquivo de teste com mais registros
            sample_size = min(100, total_ctes)
            ctes_sample = CTE.query.limit(sample_size).all()
            
            dados_performance = []
            for i, cte in enumerate(ctes_sample):
                dados_performance.append({
                    'numero_cte': cte.numero_cte,
                    'observacao': f'Teste performance {i+1} - {datetime.now().strftime("%H:%M:%S")}'
                })
            
            # Salva arquivo
            df_performance = pd.DataFrame(dados_performance)
            arquivo_performance = 'uploads/teste_performance.xlsx'
            df_performance.to_excel(arquivo_performance, index=False)
            
            print(f"📄 Arquivo de teste criado: {arquivo_performance}")
            print(f"📊 {len(dados_performance)} registros para teste")
            
            # Testa atualização
            inicio = datetime.now()
            
            updater = BulkCTEUpdaterDB(app)
            df = updater.load_update_file(arquivo_performance)
            df_normalized = updater.normalize_data(df)
            plano = updater.generate_update_plan(df_normalized, 'all')  # Força atualizações
            
            if plano:
                # Executa sem backup para medir performance pura
                sucesso = updater.execute_updates(plano, batch_size=25)
                
                fim = datetime.now()
                duracao = (fim - inicio).total_seconds()
                
                print(f"\n⏱️ RESULTADOS DO TESTE:")
                print(f"  - Duração total: {duracao:.2f} segundos")
                print(f"  - CTEs processados: {updater.stats['total_processados']}")
                print(f"  - CTEs por segundo: {updater.stats['total_processados'] / duracao:.2f}")
                print(f"  - Sucesso: {'✅' if sucesso else '❌'}")
            
            else:
                print("ℹ️ Nenhuma atualização necessária para teste")
    
    except Exception as e:
        print(f"❌ Erro no teste de performance: {str(e)}")

def demonstracao_modos():
    """
    Demonstra diferença entre modos 'empty_only' e 'all'
    """
    print("\n🎯 DEMONSTRAÇÃO DOS MODOS DE ATUALIZAÇÃO")
    print("="*50)
    
    app = create_app()
    
    try:
        with app.app_context():
            # Pega um CTE de exemplo
            cte_exemplo = CTE.query.first()
            if not cte_exemplo:
                print("❌ Nenhum CTE encontrado no banco")
                return
            
            print(f"📋 Usando CTE {cte_exemplo.numero_cte} como exemplo")
            print(f"Estado atual:")
            print(f"  - Cliente: {cte_exemplo.destinatario_nome}")
            print(f"  - Observação: {cte_exemplo.observacao}")
            
            # Cria dois arquivos de teste
            dados_teste = [{
                'numero_cte': cte_exemplo.numero_cte,
                'destinatario_nome': 'CLIENTE NOVO TESTE',
                'observacao': 'OBSERVAÇÃO NOVA TESTE'
            }]
            
            df_teste = pd.DataFrame(dados_teste)
            arquivo_teste = 'uploads/teste_modos.xlsx'
            df_teste.to_excel(arquivo_teste, index=False)
            
            updater = BulkCTEUpdaterDB(app)
            df = updater.load_update_file(arquivo_teste)
            df_normalized = updater.normalize_data(df)
            
            # Teste modo empty_only
            print(f"\n🔍 MODO 'empty_only':")
            plano_empty = updater.generate_update_plan(df_normalized, 'empty_only')
            if plano_empty:
                print(f"  - {len(plano_empty)} atualizações previstas")
                for plan in plano_empty:
                    for field, change in plan['changes'].items():
                        print(f"    {field}: '{change['old_value']}' → '{change['new_value']}'")
            else:
                print("  - Nenhuma atualização (campos já preenchidos)")
            
            # Teste modo all
            print(f"\n🔍 MODO 'all':")
            plano_all = updater.generate_update_plan(df_normalized, 'all')
            if plano_all:
                print(f"  - {len(plano_all)} atualizações previstas")
                for plan in plano_all:
                    for field, change in plan['changes'].items():
                        print(f"    {field}: '{change['old_value']}' → '{change['new_value']}'")
            else:
                print("  - Nenhuma atualização necessária")
            
            print(f"\n💡 RESUMO:")
            print(f"  - 'empty_only': Só preenche campos vazios/nulos")
            print(f"  - 'all': Atualiza todos os campos que forem diferentes")
    
    except Exception as e:
        print(f"❌ Erro na demonstração: {str(e)}")

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    
    print("🛠️ SISTEMA DE ATUALIZAÇÃO CTE - DEMONSTRAÇÕES POSTGRESQL")
    print("="*65)
    print("1. 🎬 Demonstração completa")
    print("2. 🚀 Teste de performance") 
    print("3. 🎯 Demonstração dos modos")
    print("4. 📊 Estatísticas do banco")
    print("5. 🧹 Limpeza de arquivos de teste")
    print("0. ❌ Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == '1':
        demonstracao_completa()
    
    elif opcao == '2':
        teste_performance()
    
    elif opcao == '3':
        demonstracao_modos()
    
    elif opcao == '4':
        try:
            helper = BulkUpdateHelper()
            stats = helper.get_database_statistics()
            
            if 'error' in stats:
                print(f"❌ Erro ao obter estatísticas: {stats['error']}")
            else:
                print("\n📊 ESTATÍSTICAS DO BANCO POSTGRESQL:")
                print(f"  Total de CTEs: {stats['total_ctes']}")
                print(f"  CTEs com baixa: {stats['ctes_with_baixa']}")
                print(f"  Processos completos: {stats['ctes_complete_process']}")
                
                print(f"\n📋 Preenchimento dos campos:")
                for field, data in stats.get('fields_completion', {}).items():
                    print(f"  {field}: {data['percentage']}% ({data['filled']}/{data['filled'] + data['empty']})")
        
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {str(e)}")
    
    elif opcao == '5':
        try:
            # Remove arquivos de teste
            test_files = [
                'uploads/template_exemplo_real.xlsx',
                'uploads/atualizacao_exemplo.xlsx', 
                'uploads/teste_performance.xlsx',
                'uploads/teste_modos.xlsx'
            ]
            
            removed = 0
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed += 1
                    print(f"🗑️ Removido: {file_path}")
            
            if removed > 0:
                print(f"✅ {removed} arquivos de teste removidos")
            else:
                print("ℹ️ Nenhum arquivo de teste encontrado")
        
        except Exception as e:
            print(f"❌ Erro na limpeza: {str(e)}")
    
    elif opcao == '0':
        print("👋 Até logo!")
    
    else:
        print("❌ Opção inválida")
    
    print("\n🔚 Fim da execução")