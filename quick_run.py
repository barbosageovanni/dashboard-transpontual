#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface simplificada para atualização CTE - PostgreSQL
Versão corrigida e independente
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Adicionar path do projeto
sys.path.append(os.getcwd())

def testar_ambiente():
    """Testa se o ambiente está configurado"""
    try:
        from app import create_app
        from app.models.cte import CTE
        
        app = create_app()
        with app.app_context():
            total = CTE.query.count()
            return True, total
    except Exception as e:
        return False, str(e)

def gerar_template_simples():
    """Gera template simples baseado no banco"""
    try:
        from app import create_app
        from app.models.cte import CTE
        
        app = create_app()
        
        with app.app_context():
            # Busca CTEs do banco
            num_samples = int(input("Quantos CTEs usar como exemplo? [20]: ") or "20")
            ctes = CTE.query.limit(num_samples).all()
            
            if not ctes:
                print("❌ Nenhum CTE encontrado no banco")
                return None
            
            # Cria dados para template
            template_data = []
            for cte in ctes:
                template_data.append({
                    'numero_cte': cte.numero_cte,
                    'destinatario_nome': cte.destinatario_nome or '',
                    'veiculo_placa': cte.veiculo_placa or '',
                    'valor_total': float(cte.valor_total) if cte.valor_total else '',
                    'data_emissao': cte.data_emissao.strftime('%Y-%m-%d') if cte.data_emissao else '',
                    'data_baixa': cte.data_baixa.strftime('%Y-%m-%d') if cte.data_baixa else '',
                    'numero_fatura': cte.numero_fatura or '',
                    'data_inclusao_fatura': cte.data_inclusao_fatura.strftime('%Y-%m-%d') if cte.data_inclusao_fatura else '',
                    'data_envio_processo': cte.data_envio_processo.strftime('%Y-%m-%d') if cte.data_envio_processo else '',
                    'primeiro_envio': cte.primeiro_envio.strftime('%Y-%m-%d') if cte.primeiro_envio else '',
                    'data_rq_tmc': cte.data_rq_tmc.strftime('%Y-%m-%d') if cte.data_rq_tmc else '',
                    'data_atesto': cte.data_atesto.strftime('%Y-%m-%d') if cte.data_atesto else '',
                    'envio_final': cte.envio_final.strftime('%Y-%m-%d') if cte.envio_final else '',
                    'observacao': cte.observacao or ''
                })
            
            # Salva template
            df = pd.DataFrame(template_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo = f'templates/template_real_{timestamp}.xlsx'
            
            os.makedirs('templates', exist_ok=True)
            df.to_excel(arquivo, index=False)
            
            print(f"✅ Template criado: {arquivo}")
            print(f"📊 {len(template_data)} CTEs incluídos")
            print(f"📋 Colunas: {len(df.columns)} campos disponíveis")
            
            return arquivo
            
    except Exception as e:
        print(f"❌ Erro ao gerar template: {str(e)}")
        return None

def validar_arquivo_simples():
    """Valida arquivo de forma simples"""
    arquivo = input("📄 Caminho do arquivo para validar: ").strip()
    
    if not arquivo:
        print("❌ Caminho não informado")
        return
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return
    
    try:
        # Carrega arquivo
        if arquivo.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(arquivo)
        else:
            df = pd.read_csv(arquivo)
        
        print(f"✅ Arquivo carregado: {len(df)} linhas")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        # Validações básicas
        errors = []
        warnings = []
        
        # Verifica coluna CTE
        cte_columns = ['numero_cte', 'CTE', 'Numero_CTE', 'CTRC']
        has_cte = any(col in df.columns for col in cte_columns)
        
        if not has_cte:
            errors.append("Coluna de identificação CTE não encontrada")
        else:
            cte_col = next(col for col in cte_columns if col in df.columns)
            duplicates = df[df.duplicated(subset=[cte_col], keep=False)]
            if not duplicates.empty:
                warnings.append(f"CTEs duplicados: {len(duplicates)} registros")
        
        # Verifica se há dados
        if df.empty:
            errors.append("Arquivo está vazio")
        
        # Resultados
        print(f"\n📊 RESULTADO DA VALIDAÇÃO:")
        print(f"✅ Válido: {len(errors) == 0}")
        
        if errors:
            print("❌ Erros:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("⚠️ Avisos:")
            for warning in warnings:
                print(f"  - {warning}")
        
        # Estatísticas
        print(f"\n📈 Estatísticas:")
        print(f"  - Total de linhas: {len(df)}")
        print(f"  - Total de colunas: {len(df.columns)}")
        print(f"  - Células vazias: {df.isnull().sum().sum()}")
        
        # Preview
        print(f"\n👁️ Preview (primeiras 3 linhas):")
        print(df.head(3).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Erro ao validar arquivo: {str(e)}")

def estatisticas_simples():
    """Mostra estatísticas simples do banco"""
    try:
        from app import create_app
        from app.models.cte import CTE
        
        app = create_app()
        
        with app.app_context():
            total = CTE.query.count()
            com_baixa = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
            com_cliente = CTE.query.filter(CTE.destinatario_nome.isnot(None)).count()
            com_valor = CTE.query.filter(CTE.valor_total > 0).count()
            
            print(f"\n📊 ESTATÍSTICAS DO BANCO:")
            print(f"  Total de CTEs: {total}")
            print(f"  Com baixa: {com_baixa} ({(com_baixa/total*100):.1f}%)")
            print(f"  Com cliente: {com_cliente} ({(com_cliente/total*100):.1f}%)")
            print(f"  Com valor: {com_valor} ({(com_valor/total*100):.1f}%)")
            
            # Estatísticas de datas
            campos_data = [
                ('data_emissao', 'Data Emissão'),
                ('data_inclusao_fatura', 'Inclusão Fatura'),
                ('primeiro_envio', 'Primeiro Envio'),
                ('data_atesto', 'Atesto'),
                ('envio_final', 'Envio Final')
            ]
            
            print(f"\n📅 Preenchimento de Datas:")
            for campo, nome in campos_data:
                if hasattr(CTE, campo):
                    count = CTE.query.filter(getattr(CTE, campo).isnot(None)).count()
                    pct = (count/total*100) if total > 0 else 0
                    print(f"  {nome}: {count} ({pct:.1f}%)")
            
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {str(e)}")

def executar_atualizacao_simples():
    """Interface simples para executar atualização"""
    arquivo = input("📄 Caminho do arquivo Excel/CSV: ").strip()
    
    if not arquivo:
        print("❌ Arquivo é obrigatório")
        return
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return
    
    print("\n🔄 Modos disponíveis:")
    print("1. empty_only - Preenche apenas campos vazios (SEGURO)")
    print("2. all - Atualiza todos os campos (CUIDADO)")
    
    modo_escolha = input("Escolha o modo [1]: ").strip()
    modo = 'empty_only' if modo_escolha != '2' else 'all'
    
    preview = input("👁️ Apenas preview? (s/N): ").strip().lower()
    apenas_preview = preview in ['s', 'sim', 'y', 'yes']
    
    batch = input("📦 Tamanho do lote [100]: ").strip()
    batch_size = int(batch) if batch.isdigit() else 100
    
    # Monta comando
    cmd_parts = [
        'python bulk_update_cte.py',
        f'--update-file "{arquivo}"',
        f'--mode {modo}',
        f'--batch-size {batch_size}'
    ]
    
    if apenas_preview:
        cmd_parts.append('--preview-only')
    
    comando = ' '.join(cmd_parts)
    
    print(f"\n🔧 Comando a ser executado:")
    print(comando)
    
    confirma = input("\n▶️ Executar? (s/N): ").strip().lower()
    if confirma in ['s', 'sim', 'y', 'yes']:
        print("🚀 Executando...")
        os.system(comando)
    else:
        print("❌ Execução cancelada")

def limpar_arquivos_simples():
    """Limpeza simples de arquivos"""
    pastas = ['uploads', 'logs', 'backups', 'reports']
    
    print("🧹 LIMPEZA DE ARQUIVOS")
    print("="*25)
    
    for pasta in pastas:
        if os.path.exists(pasta):
            arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
            print(f"📁 {pasta}: {len(arquivos)} arquivos")
        else:
            print(f"❌ {pasta}: pasta não existe")
    
    confirma = input("\n🗑️ Remover arquivos de teste/exemplo? (s/N): ").strip().lower()
    
    if confirma in ['s', 'sim', 'y', 'yes']:
        removidos = 0
        
        # Arquivos de teste conhecidos
        arquivos_teste = [
            'uploads/teste_exemplo.xlsx',
            'uploads/teste_real.xlsx',
            'uploads/atualizacao_exemplo.xlsx',
            'templates/template_real_*.xlsx'
        ]
        
        for pasta in pastas:
            if os.path.exists(pasta):
                for arquivo in os.listdir(pasta):
                    if 'teste' in arquivo.lower() or 'exemplo' in arquivo.lower():
                        caminho = os.path.join(pasta, arquivo)
                        try:
                            os.remove(caminho)
                            print(f"🗑️ Removido: {caminho}")
                            removidos += 1
                        except:
                            pass
        
        print(f"✅ {removidos} arquivos removidos")
    else:
        print("ℹ️ Limpeza cancelada")

def main():
    print("🛠️ FERRAMENTAS DE ATUALIZAÇÃO CTE - POSTGRESQL")
    print("="*50)
    
    # Testa ambiente primeiro
    ambiente_ok, info = testar_ambiente()
    
    if not ambiente_ok:
        print(f"❌ Ambiente não configurado: {info}")
        print("💡 Certifique-se de estar no diretório do projeto Flask")
        return
    
    print(f"✅ Ambiente OK - {info} CTEs no banco")
    
    print("\nOpções disponíveis:")
    print("1. 📋 Gerar template baseado no banco")
    print("2. 🔄 Executar atualização")
    print("3. ✅ Validar arquivo")
    print("4. 📊 Estatísticas do banco")
    print("5. 🧹 Limpar arquivos")
    print("0. ❌ Sair")
    
    escolha = input("\nEscolha uma opção: ").strip()
    
    if escolha == '1':
        gerar_template_simples()
        
    elif escolha == '2':
        executar_atualizacao_simples()
        
    elif escolha == '3':
        validar_arquivo_simples()
        
    elif escolha == '4':
        estatisticas_simples()
        
    elif escolha == '5':
        limpar_arquivos_simples()
        
    elif escolha == '0':
        print("👋 Até logo!")
        
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    main()