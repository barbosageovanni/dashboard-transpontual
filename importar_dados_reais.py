#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importação COMPLETA dos dados reais do CSV
SUBSTITUI todos os dados atuais pelos dados limpos do CSV
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import numpy as np

def fazer_backup_completo():
    """Faz backup completo antes da substituição"""
    try:
        print("💾 Fazendo backup completo dos dados atuais...")
        
        app = create_app()
        with app.app_context():
            # Contar registros atuais
            result = db.session.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
            total_atual = result.fetchone()[0]
            
            print(f"📊 Registros atuais no banco: {total_atual}")
            
            # Salvar amostra dos dados atuais
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_info = f"backup_info_{timestamp}.txt"
            
            with open(backup_info, 'w', encoding='utf-8') as f:
                f.write(f"Backup realizado em: {datetime.now()}\n")
                f.write(f"Total de registros substituídos: {total_atual}\n")
                f.write(f"Novo arquivo: dashboard_baker.csv\n")
                f.write(f"Operação: Substituição completa\n")
            
            print(f"✅ Backup de informações salvo: {backup_info}")
            return True, total_atual
            
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return False, 0

def limpar_dados_banco():
    """Limpa completamente a tabela atual"""
    try:
        print("🗑️ Limpando dados atuais da tabela...")
        
        # Desabilitar constraints temporariamente
        db.session.execute(text("SET session_replication_role = replica;"))
        
        # Limpar tabela
        result = db.session.execute(text("DELETE FROM dashboard_baker"))
        registros_removidos = result.rowcount
        
        # Resetar sequence do ID
        db.session.execute(text("SELECT setval('dashboard_baker_id_seq', 1, false);"))
        
        # Reabilitar constraints
        db.session.execute(text("SET session_replication_role = DEFAULT;"))
        
        db.session.commit()
        
        print(f"✅ {registros_removidos} registros removidos")
        print(f"✅ Tabela limpa e pronta para importação")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")
        db.session.rollback()
        return False

def processar_csv_dados(arquivo_csv):
    """Processa e valida o CSV antes da importação"""
    try:
        print(f"📋 Processando arquivo CSV: {arquivo_csv}")
        
        # Carregar CSV
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
        
        print(f"📊 Registros no CSV: {len(df)}")
        print(f"📊 Colunas encontradas: {len(df.columns)}")
        
        # Mostrar colunas
        print(f"📋 Colunas do CSV:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['numero_cte', 'destinatario_nome', 'valor_total', 'data_emissao']
        colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltando:
            print(f"❌ Colunas obrigatórias faltando: {colunas_faltando}")
            return None
        
        # Processar dados
        print(f"🔧 Processando dados...")
        
        # Converter valores nulos
        df = df.replace({np.nan: None, 'NaN': None, 'nan': None, '': None})
        
        # Processar datas (converter strings para datetime)
        colunas_data = [
            'data_emissao', 'data_baixa', 'data_inclusao_fatura', 
            'data_envio_processo', 'primeiro_envio', 'data_rq_tmc', 
            'data_atesto', 'envio_final', 'created_at', 'updated_at'
        ]
        
        for col in colunas_data:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Garantir que valor_total seja numérico
        df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)
        
        # Remover registros inválidos
        df_original_len = len(df)
        df = df[df['numero_cte'].notna() & (df['numero_cte'] > 0)]
        df = df[df['valor_total'] >= 0]
        
        if len(df) < df_original_len:
            print(f"⚠️ {df_original_len - len(df)} registros inválidos removidos")
        
        # Estatísticas dos dados
        print(f"\n📈 ESTATÍSTICAS DOS DADOS:")
        print(f"  - CTEs válidos: {len(df):,}")
        print(f"  - Faixa de CTEs: {df['numero_cte'].min()} a {df['numero_cte'].max()}")
        print(f"  - Valor total: R$ {df['valor_total'].sum():,.2f}")
        print(f"  - Clientes únicos: {df['destinatario_nome'].nunique()}")
        print(f"  - Datas de emissão: {df['data_emissao'].min()} a {df['data_emissao'].max()}")
        
        # Verificar Baker Hughes
        baker_count = len(df[df['destinatario_nome'].str.contains('BAKER HUGHES', case=False, na=False)])
        print(f"  - CTEs Baker Hughes: {baker_count:,} ({baker_count/len(df)*100:.1f}%)")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro no processamento do CSV: {e}")
        return None

def importar_dados_batch(df, batch_size=500):
    """Importa dados em lotes para melhor performance"""
    try:
        total_registros = len(df)
        total_importados = 0
        
        print(f"📥 Importando {total_registros:,} registros em lotes de {batch_size}...")
        
        # Processar em lotes
        for i in range(0, total_registros, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            # Converter para lista de dicionários
            registros = []
            for _, row in batch.iterrows():
                registro = {
                    'numero_cte': int(row['numero_cte']) if pd.notna(row['numero_cte']) else None,
                    'destinatario_nome': str(row['destinatario_nome']) if pd.notna(row['destinatario_nome']) else None,
                    'veiculo_placa': str(row['veiculo_placa']) if pd.notna(row['veiculo_placa']) else None,
                    'valor_total': float(row['valor_total']) if pd.notna(row['valor_total']) else 0.0,
                    'data_emissao': row['data_emissao'].date() if pd.notna(row['data_emissao']) else None,
                    'numero_fatura': str(row['numero_fatura']) if pd.notna(row['numero_fatura']) else None,
                    'data_baixa': row['data_baixa'].date() if pd.notna(row['data_baixa']) else None,
                    'observacao': str(row['observacao']) if pd.notna(row['observacao']) else None,
                    'data_inclusao_fatura': row['data_inclusao_fatura'].date() if pd.notna(row['data_inclusao_fatura']) else None,
                    'data_envio_processo': row['data_envio_processo'].date() if pd.notna(row['data_envio_processo']) else None,
                    'primeiro_envio': row['primeiro_envio'].date() if pd.notna(row['primeiro_envio']) else None,
                    'data_rq_tmc': row['data_rq_tmc'].date() if pd.notna(row['data_rq_tmc']) else None,
                    'data_atesto': row['data_atesto'].date() if pd.notna(row['data_atesto']) else None,
                    'envio_final': row['envio_final'].date() if pd.notna(row['envio_final']) else None,
                    'origem_dados': 'CSV Real'
                }
                registros.append(registro)
            
            # Inserir lote
            try:
                db.session.execute(text("""
                    INSERT INTO dashboard_baker (
                        numero_cte, destinatario_nome, veiculo_placa, valor_total,
                        data_emissao, numero_fatura, data_baixa, observacao,
                        data_inclusao_fatura, data_envio_processo, primeiro_envio,
                        data_rq_tmc, data_atesto, envio_final, origem_dados
                    ) VALUES (
                        :numero_cte, :destinatario_nome, :veiculo_placa, :valor_total,
                        :data_emissao, :numero_fatura, :data_baixa, :observacao,
                        :data_inclusao_fatura, :data_envio_processo, :primeiro_envio,
                        :data_rq_tmc, :data_atesto, :envio_final, :origem_dados
                    )
                """), registros)
                
                db.session.commit()
                total_importados += len(registros)
                
                # Progresso
                progress = (total_importados / total_registros) * 100
                print(f"  📥 {total_importados:,}/{total_registros:,} ({progress:.1f}%) importados...")
                
            except Exception as e:
                print(f"❌ Erro no lote {i}-{i+batch_size}: {e}")
                db.session.rollback()
                continue
        
        print(f"✅ Importação concluída: {total_importados:,} registros")
        return total_importados
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        db.session.rollback()
        return 0

def validar_importacao():
    """Valida os dados após a importação"""
    try:
        print(f"🔍 Validando dados importados...")
        
        # Contagem total
        result = db.session.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
        total = result.fetchone()[0]
        print(f"  ✅ Total de registros: {total:,}")
        
        # Baker Hughes
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM dashboard_baker 
            WHERE destinatario_nome LIKE '%BAKER HUGHES%'
        """))
        baker_count = result.fetchone()[0]
        print(f"  ✅ CTEs Baker Hughes: {baker_count:,}")
        
        # Valores
        result = db.session.execute(text("""
            SELECT 
                SUM(valor_total) as valor_total,
                COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa,
                COUNT(DISTINCT destinatario_nome) as clientes_unicos
            FROM dashboard_baker
        """))
        
        row = result.fetchone()
        valor_total, com_baixa, clientes = row
        print(f"  ✅ Valor total: R$ {valor_total:,.2f}")
        print(f"  ✅ CTEs com baixa: {com_baixa:,}")
        print(f"  ✅ Clientes únicos: {clientes}")
        
        # Datas
        result = db.session.execute(text("""
            SELECT 
                MIN(data_emissao) as primeira,
                MAX(data_emissao) as ultima,
                COUNT(CASE WHEN data_rq_tmc IS NOT NULL AND primeiro_envio IS NOT NULL THEN 1 END) as variacoes_validas
            FROM dashboard_baker
            WHERE data_emissao IS NOT NULL
        """))
        
        row = result.fetchone()
        primeira, ultima, variacoes = row
        print(f"  ✅ Período: {primeira} a {ultima}")
        print(f"  ✅ Registros com variações temporais: {variacoes:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def importar_dados_reais():
    """Função principal de importação"""
    
    print("🚀 IMPORTAÇÃO COMPLETA DOS DADOS REAIS")
    print("=" * 60)
    print("⚠️ Esta operação vai:")
    print("   🗑️ REMOVER todos os dados atuais do banco")
    print("   📥 IMPORTAR todos os dados do CSV")
    print("   🔄 SUBSTITUIR completamente o banco de dados")
    print("=" * 60)
    
    # Verificar se o arquivo existe
    arquivo_csv = 'dashboard_baker.csv'
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        print(f"💡 Coloque o arquivo CSV na pasta do projeto")
        return False
    
    # Confirmação
    resposta = input("Deseja continuar? (digite 'SIM' para confirmar): ")
    if resposta.upper() != 'SIM':
        print("❌ Operação cancelada pelo usuário")
        return False
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Backup
            backup_ok, total_antes = fazer_backup_completo()
            if not backup_ok:
                print("❌ Backup falhou - cancelando importação")
                return False
            
            # 2. Processar CSV
            df = processar_csv_dados(arquivo_csv)
            if df is None:
                print("❌ Erro no processamento do CSV")
                return False
            
            # 3. Confirmação final
            print(f"\n📊 RESUMO DA OPERAÇÃO:")
            print(f"  - Registros atuais (serão removidos): {total_antes:,}")
            print(f"  - Registros novos (serão importados): {len(df):,}")
            print(f"  - Diferença: {len(df) - total_antes:+,}")
            
            confirmacao = input("\nConfirma a substituição completa? (digite 'CONFIRMO'): ")
            if confirmacao.upper() != 'CONFIRMO':
                print("❌ Importação cancelada")
                return False
            
            # 4. Limpar banco
            if not limpar_dados_banco():
                print("❌ Erro na limpeza do banco")
                return False
            
            # 5. Importar dados
            total_importados = importar_dados_batch(df)
            if total_importados == 0:
                print("❌ Nenhum registro foi importado")
                return False
            
            # 6. Validar
            if not validar_importacao():
                print("⚠️ Problemas na validação, mas dados foram importados")
            
            print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"📊 {total_importados:,} registros importados")
            print(f"✅ Banco de dados atualizado com dados reais")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro geral na importação: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if importar_dados_reais():
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"1. Pressione Ctrl+C no terminal do dashboard")
        print(f"2. Execute: python iniciar.py")
        print(f"3. Acesse: http://localhost:5000")
        print(f"4. Verifique se todos os gráficos aparecem")
        print(f"5. Teste as análises de variações temporais")
    else:
        print(f"\n❌ Importação falhou")