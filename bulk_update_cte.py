#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Atualização em Lote de CTEs - PostgreSQL (VERSÃO CORRIGIDA)
Versão robusta para Windows e arquivos Excel reais
"""

import pandas as pd
import logging
from datetime import datetime, date
import json
import os
from typing import Dict, List, Tuple, Optional
import argparse
from pathlib import Path
from decimal import Decimal
import sys
import re

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.cte import CTE
from sqlalchemy import text, and_, or_
from sqlalchemy.exc import IntegrityError
import urllib.parse

# Configuração de logging SEM EMOJIS para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/bulk_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkCTEUpdaterDB:
    """
    Classe principal para atualização em lote de CTEs no PostgreSQL
    Versão robusta para arquivos Excel reais
    """
    
    def __init__(self, app=None):
        """Inicializa o atualizador"""
        self.app = app or create_app()
        self.update_log = []
        self.stats = {
            'total_processados': 0,
            'atualizados': 0,
            'sem_alteracao': 0,
            'nao_encontrados': 0,
            'erros': 0,
            'campos_atualizados': {}
        }
        
        # Mapeamento de colunas do arquivo para campos do banco
        self.column_mapping = {
            # Identificação
            'CTE': 'numero_cte',
            'Numero_CTE': 'numero_cte',
            'CTRC': 'numero_cte',
            'numero_cte': 'numero_cte',
            
            # Dados principais
            'Cliente': 'destinatario_nome',
            'Destinatario': 'destinatario_nome',
            'destinatario_nome': 'destinatario_nome',
            
            'Veiculo': 'veiculo_placa',
            'Placa': 'veiculo_placa',
            'veiculo_placa': 'veiculo_placa',
            
            'Valor_Frete': 'valor_total',
            'Valor': 'valor_total',
            'valor_total': 'valor_total',
            
            # Datas principais
            'Data_Emissao': 'data_emissao',
            'Data_Emissao_CTE': 'data_emissao',
            'data_emissao': 'data_emissao',
            
            'Data_Baixa': 'data_baixa',
            'data_baixa': 'data_baixa',
            
            # Faturamento
            'Numero_Fatura': 'numero_fatura',
            'numero_fatura': 'numero_fatura',
            
            'Data_Inclusao_Fatura': 'data_inclusao_fatura',
            'data_inclusao_fatura': 'data_inclusao_fatura',
            
            'Data_Envio_Processo': 'data_envio_processo',
            'data_envio_processo': 'data_envio_processo',
            
            'Data_Primeiro_Envio': 'primeiro_envio',
            'Primeiro_Envio': 'primeiro_envio',
            'primeiro_envio': 'primeiro_envio',
            
            'Data_RQ_TMC': 'data_rq_tmc',
            'data_rq_tmc': 'data_rq_tmc',
            
            'Data_Atesto': 'data_atesto',
            'data_atesto': 'data_atesto',
            
            'Data_Envio_Final': 'envio_final',
            'Envio_Final': 'envio_final',
            'envio_final': 'envio_final',
            
            # Observações
            'Observacoes': 'observacao',
            'Observacao': 'observacao',
            'observacao': 'observacao',
            'Comentarios': 'observacao'
        }
        
        # Campos de data para conversão
        self.date_fields = [
            'data_emissao', 'data_baixa', 'data_inclusao_fatura',
            'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
            'data_atesto', 'envio_final'
        ]
        
        # Campos numéricos
        self.numeric_fields = ['valor_total']
    
    def clean_column_names(self, df):
        """
        Limpa nomes de colunas inválidos
        """
        try:
            # Renomear colunas inválidas
            new_columns = []
            
            for i, col in enumerate(df.columns):
                # Converter para string e limpar
                col_str = str(col).strip()
                
                # Remover colunas claramente inválidas
                if (col_str.startswith('Unnamed:') or 
                    col_str.isdigit() or 
                    col_str in ['nan', 'NaN', ''] or
                    len(col_str) > 50):
                    # Marcar para remoção
                    new_columns.append(f'_REMOVE_{i}')
                else:
                    new_columns.append(col_str)
            
            # Aplicar novos nomes
            df.columns = new_columns
            
            # Remover colunas marcadas
            cols_to_remove = [col for col in df.columns if col.startswith('_REMOVE_')]
            if cols_to_remove:
                df = df.drop(columns=cols_to_remove)
                logger.info(f"Colunas inválidas removidas: {len(cols_to_remove)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao limpar colunas: {str(e)}")
            return df
    
    def load_update_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Carrega arquivo Excel/CSV para atualização
        Versão robusta para arquivos reais
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado: {file_path}")
                return None
            
            # Detecta extensão e carrega
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # Carregamento robusto do Excel
                df = pd.read_excel(file_path, na_values=['', 'NA', 'N/A', '#N/A', 'NULL'])
            elif file_ext == '.csv':
                # Tenta diferentes encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding, na_values=['', 'NA', 'N/A', '#N/A', 'NULL'])
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.error("Não foi possível ler o arquivo com nenhuma codificação")
                    return None
            else:
                logger.error(f"Formato não suportado: {file_ext}")
                return None
            
            # Limpar colunas inválidas
            df = self.clean_column_names(df)
            
            # Remover linhas completamente vazias
            df = df.dropna(how='all')
            
            logger.info(f"Arquivo carregado: {len(df)} registros")
            logger.info(f"Colunas válidas: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo: {str(e)}")
            return None
    
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza e mapeia dados do DataFrame
        Versão robusta para dados reais
        """
        try:
            # Copia DataFrame
            df_normalized = df.copy()
            
            # Mapeia colunas de forma segura
            mapped_columns = {}
            for col in df_normalized.columns:
                # Converter para string e limpar
                col_clean = str(col).strip()
                
                # Verificar mapeamento direto
                if col_clean in self.column_mapping:
                    mapped_columns[col] = self.column_mapping[col_clean]
                else:
                    # Verificar mapeamento case-insensitive
                    for map_key, map_value in self.column_mapping.items():
                        if col_clean.lower() == map_key.lower():
                            mapped_columns[col] = map_value
                            break
            
            df_normalized = df_normalized.rename(columns=mapped_columns)
            
            # Converte campos de data de forma robusta
            for field in self.date_fields:
                if field in df_normalized.columns:
                    # Converter datas de forma mais robusta
                    try:
                        df_normalized[field] = pd.to_datetime(
                            df_normalized[field], 
                            errors='coerce',
                            dayfirst=True,
                            format=None  # Deixa pandas detectar formato
                        ).dt.date
                    except:
                        logger.warning(f"Erro ao converter datas na coluna {field}")
            
            # Converte campos numéricos de forma robusta
            for field in self.numeric_fields:
                if field in df_normalized.columns:
                    try:
                        # Limpar texto dos valores primeiro
                        df_normalized[field] = df_normalized[field].astype(str).str.replace(',', '.')
                        df_normalized[field] = pd.to_numeric(
                            df_normalized[field], 
                            errors='coerce'
                        )
                    except:
                        logger.warning(f"Erro ao converter números na coluna {field}")
            
            # Remove linhas sem CTE válido
            if 'numero_cte' in df_normalized.columns:
                # Converter CTEs para números
                df_normalized['numero_cte'] = pd.to_numeric(df_normalized['numero_cte'], errors='coerce')
                # Remover CTEs inválidos
                df_normalized = df_normalized.dropna(subset=['numero_cte'])
                df_normalized['numero_cte'] = df_normalized['numero_cte'].astype(int)
            else:
                logger.error("Coluna de identificação (CTE) não encontrada")
                return pd.DataFrame()
            
            logger.info(f"Dados normalizados: {len(df_normalized)} registros válidos")
            return df_normalized
            
        except Exception as e:
            logger.error(f"Erro na normalização: {str(e)}")
            return pd.DataFrame()
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida dados do DataFrame"""
        errors = []
        
        # Verifica se há dados
        if df.empty:
            errors.append("DataFrame está vazio")
            return False, errors
        
        # Verifica coluna obrigatória
        if 'numero_cte' not in df.columns:
            errors.append("Coluna 'numero_cte' não encontrada")
            return False, errors
        
        # Verifica CTEs duplicados
        duplicates = df[df.duplicated(subset=['numero_cte'], keep=False)]
        if not duplicates.empty:
            errors.append(f"CTEs duplicados encontrados: {duplicates['numero_cte'].tolist()}")
        
        # Valida faixa de CTEs
        invalid_ctes = df[(df['numero_cte'] <= 0) | (df['numero_cte'] > 999999999)]
        if not invalid_ctes.empty:
            errors.append(f"CTEs com valores inválidos: {invalid_ctes['numero_cte'].tolist()}")
        
        return len(errors) == 0, errors
    
    def check_existing_ctes(self, df: pd.DataFrame) -> Tuple[List[int], List[int]]:
        """Verifica quais CTEs existem no banco"""
        try:
            with self.app.app_context():
                cte_numbers = df['numero_cte'].tolist()
                
                # Busca CTEs no banco em lotes
                existing_ctes = []
                batch_size = 1000
                
                for i in range(0, len(cte_numbers), batch_size):
                    batch = cte_numbers[i:i + batch_size]
                    results = db.session.query(CTE.numero_cte).filter(
                        CTE.numero_cte.in_(batch)
                    ).all()
                    existing_ctes.extend([r[0] for r in results])
                
                not_found = list(set(cte_numbers) - set(existing_ctes))
                
                logger.info(f"CTEs existentes: {len(existing_ctes)}")
                logger.info(f"CTEs não encontrados: {len(not_found)}")
                
                return existing_ctes, not_found
                
        except Exception as e:
            logger.error(f"Erro ao verificar CTEs: {str(e)}")
            return [], cte_numbers
    
    def generate_update_plan(self, df: pd.DataFrame, update_mode: str = 'empty_only') -> List[Dict]:
        """Gera plano de atualização"""
        update_plan = []
        
        try:
            with self.app.app_context():
                existing_ctes, not_found = self.check_existing_ctes(df)
                
                # Filtra apenas CTEs existentes
                df_to_update = df[df['numero_cte'].isin(existing_ctes)].copy()
                
                for _, row in df_to_update.iterrows():
                    numero_cte = int(row['numero_cte'])
                    
                    # Busca CTE atual no banco
                    current_cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                    if not current_cte:
                        continue
                    
                    changes = {}
                    
                    # Verifica cada campo do DataFrame
                    for col in df.columns:
                        if col == 'numero_cte':  # Não atualiza identificador
                            continue
                        
                        if col not in self.column_mapping.values():
                            continue  # Pula colunas não mapeadas
                        
                        new_value = row[col] if pd.notna(row[col]) else None
                        current_value = getattr(current_cte, col, None)
                        
                        # Converte valores para comparação
                        if col in self.date_fields:
                            if isinstance(current_value, date):
                                current_value_str = current_value.strftime('%Y-%m-%d') if current_value else None
                            else:
                                current_value_str = str(current_value) if current_value else None
                            
                            if isinstance(new_value, date):
                                new_value_str = new_value.strftime('%Y-%m-%d') if new_value else None
                            else:
                                new_value_str = str(new_value) if new_value else None
                        
                        elif col in self.numeric_fields:
                            current_value_str = str(float(current_value)) if current_value else None
                            new_value_str = str(float(new_value)) if new_value else None
                        
                        else:
                            current_value_str = str(current_value) if current_value else None
                            new_value_str = str(new_value) if new_value else None
                        
                        # Decide se deve atualizar
                        should_update = False
                        
                        if update_mode == 'all':
                            should_update = (new_value_str != current_value_str and 
                                           new_value_str not in [None, '', 'nan', 'NaT'])
                        elif update_mode == 'empty_only':
                            should_update = (current_value_str in [None, '', 'nan', 'NaT'] and 
                                           new_value_str not in [None, '', 'nan', 'NaT'])
                        
                        if should_update:
                            changes[col] = {
                                'old_value': current_value_str,
                                'new_value': new_value_str,
                                'raw_new_value': new_value
                            }
                    
                    if changes:
                        update_plan.append({
                            'numero_cte': numero_cte,
                            'changes': changes
                        })
                
                logger.info(f"Plano gerado: {len(update_plan)} CTEs para atualização")
                return update_plan
                
        except Exception as e:
            logger.error(f"Erro ao gerar plano: {str(e)}")
            return []
    
    def preview_updates(self, update_plan: List[Dict], max_preview: int = 10) -> None:
        """Exibe preview das atualizações"""
        print("\n" + "="*80)
        print("PREVIEW DAS ATUALIZAÇÕES")
        print("="*80)
        
        if not update_plan:
            print("Nenhuma atualização será realizada")
            return
        
        for i, plan in enumerate(update_plan[:max_preview], 1):
            print(f"\n{i}. CTE: {plan['numero_cte']}")
            for field, change in plan['changes'].items():
                print(f"   {field}: '{change['old_value']}' -> '{change['new_value']}'")
        
        if len(update_plan) > max_preview:
            print(f"\n... e mais {len(update_plan) - max_preview} atualizações")
        
        # Estatísticas por campo
        field_stats = {}
        for plan in update_plan:
            for field in plan['changes'].keys():
                field_stats[field] = field_stats.get(field, 0) + 1
        
        print(f"\nESTATÍSTICAS:")
        print(f"Total de CTEs: {len(update_plan)}")
        print("Campos mais atualizados:")
        for field, count in sorted(field_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {field}: {count} atualizações")
        
        print("="*80)
    
    def execute_updates(self, update_plan: List[Dict], batch_size: int = 100) -> bool:
        """Executa as atualizações no banco"""
        try:
            with self.app.app_context():
                total_updates = len(update_plan)
                
                for i in range(0, total_updates, batch_size):
                    batch = update_plan[i:i + batch_size]
                    
                    try:
                        for plan in batch:
                            numero_cte = plan['numero_cte']
                            changes = plan['changes']
                            
                            # Busca CTE no banco
                            cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                            if not cte:
                                self.stats['nao_encontrados'] += 1
                                continue
                            
                            # Aplica mudanças
                            updated = False
                            for field, change in changes.items():
                                try:
                                    setattr(cte, field, change['raw_new_value'])
                                    updated = True
                                    
                                    # Atualiza estatísticas
                                    if field not in self.stats['campos_atualizados']:
                                        self.stats['campos_atualizados'][field] = 0
                                    self.stats['campos_atualizados'][field] += 1
                                    
                                except Exception as e:
                                    logger.warning(f"Erro ao atualizar {field} do CTE {numero_cte}: {str(e)}")
                            
                            if updated:
                                cte.updated_at = datetime.utcnow()
                                self.stats['atualizados'] += 1
                                
                                # Log da atualização
                                self.update_log.append({
                                    'timestamp': datetime.now().isoformat(),
                                    'numero_cte': numero_cte,
                                    'changes': {k: {'old': v['old_value'], 'new': v['new_value']} 
                                              for k, v in changes.items()}
                                })
                            else:
                                self.stats['sem_alteracao'] += 1
                            
                            self.stats['total_processados'] += 1
                        
                        # Commit do lote
                        db.session.commit()
                        logger.info(f"Lote {i//batch_size + 1} concluído: {len(batch)} CTEs processados")
                        
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Erro no lote {i//batch_size + 1}: {str(e)}")
                        self.stats['erros'] += len(batch)
                
                logger.info("Atualização concluída!")
                logger.info(f"Processados: {self.stats['total_processados']}")
                logger.info(f"Atualizados: {self.stats['atualizados']}")
                logger.info(f"Sem alteração: {self.stats['sem_alteracao']}")
                logger.info(f"Erros: {self.stats['erros']}")
                
                return True
                
        except Exception as e:
            logger.error(f"Erro geral na execução: {str(e)}")
            return False
    
    def create_backup(self, cte_numbers: List[int] = None) -> str:
        """Cria backup dos CTEs que serão atualizados"""
        try:
            with self.app.app_context():
                backup_name = f"backup_ctes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = os.path.join('backups', backup_name)
                
                os.makedirs('backups', exist_ok=True)
                
                if cte_numbers:
                    ctes = CTE.query.filter(CTE.numero_cte.in_(cte_numbers)).all()
                else:
                    ctes = CTE.query.all()
                
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_ctes': len(ctes),
                    'ctes': [cte.to_dict() for cte in ctes]
                }
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"Backup criado: {backup_path}")
                return backup_path
                
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return None
    
    def save_update_report(self, file_path: str = None) -> str:
        """Salva relatório completo da atualização"""
        if not file_path:
            file_path = f"reports/update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            os.makedirs('reports', exist_ok=True)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'statistics': self.stats,
                'update_log': self.update_log
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório salvo: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")
            return None

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Atualização em lote de CTEs - PostgreSQL')
    parser.add_argument('--update-file', required=True, help='Arquivo Excel/CSV para atualização')
    parser.add_argument('--mode', choices=['all', 'empty_only'], default='empty_only',
                       help='Modo: all (todas) ou empty_only (apenas vazias)')
    parser.add_argument('--preview-only', action='store_true', help='Apenas preview')
    parser.add_argument('--batch-size', type=int, default=100, help='Tamanho do lote')
    parser.add_argument('--no-backup', action='store_true', help='Não criar backup')
    
    args = parser.parse_args()
    
    print("SISTEMA DE ATUALIZAÇÃO EM LOTE - POSTGRESQL")
    print("="*60)
    
    # Cria pastas necessárias
    for folder in ['logs', 'backups', 'reports']:
        os.makedirs(folder, exist_ok=True)
    
    # Inicializa atualizador
    updater = BulkCTEUpdaterDB()
    
    # Carrega arquivo
    print(f"\nCarregando arquivo: {args.update_file}")
    df = updater.load_update_file(args.update_file)
    if df is None:
        return False
    
    # Normaliza dados
    print("\nNormalizando dados...")
    df_normalized = updater.normalize_data(df)
    if df_normalized.empty:
        print("Falha na normalização dos dados")
        return False
    
    # Valida dados
    print("\nValidando dados...")
    is_valid, errors = updater.validate_data(df_normalized)
    if not is_valid:
        print("Dados inválidos:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Gera plano de atualização
    print(f"\nGerando plano (modo: {args.mode})...")
    update_plan = updater.generate_update_plan(df_normalized, args.mode)
    
    if not update_plan:
        print("Nenhuma atualização necessária")
        return True
    
    # Preview
    updater.preview_updates(update_plan)
    
    if args.preview_only:
        print("\nPreview concluído (modo --preview-only)")
        return True
    
    # Confirmação
    confirm = input("\nDeseja continuar? (s/N): ").lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada")
        return False
    
    # Backup
    if not args.no_backup:
        print("\nCriando backup...")
        cte_numbers = [plan['numero_cte'] for plan in update_plan]
        backup_path = updater.create_backup(cte_numbers)
        if backup_path:
            print(f"Backup criado: {backup_path}")
    
    # Executa atualizações
    print(f"\nExecutando atualizações...")
    success = updater.execute_updates(update_plan, args.batch_size)
    
    # Salva relatório
    report_path = updater.save_update_report()
    
    if success:
        print("\nAtualização concluída com sucesso!")
        if report_path:
            print(f"Relatório: {report_path}")
    else:
        print("\nFalha na atualização")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)