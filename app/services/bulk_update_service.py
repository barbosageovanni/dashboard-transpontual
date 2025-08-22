#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Atualização em Lote - Integrado ao Flask
app/services/bulk_update_service.py
"""

import pandas as pd
import logging
from datetime import datetime, date
import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from decimal import Decimal
import io

from app import db
from app.models.cte import CTE
from sqlalchemy import text, and_, or_
from sqlalchemy.exc import IntegrityError
from flask import current_app

class BulkUpdateService:
    '''Serviço de atualização em lote integrado ao Flask'''
    
    def __init__(self):
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
        
        
        self.date_fields = [
            'data_emissao', 'data_baixa', 'data_inclusao_fatura',
            'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
            'data_atesto', 'envio_final'
        ]
        
        self.numeric_fields = ['valor_total']
    
    def processar_arquivo_web(self, arquivo_upload, modo_atualizacao='empty_only'):
        '''Processa arquivo enviado via web'''
        try:
            # Ler arquivo diretamente do upload
            if arquivo_upload.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(arquivo_upload.read()), encoding='utf-8')
            elif arquivo_upload.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(arquivo_upload.read()))
            else:
                return {'sucesso': False, 'erro': 'Formato não suportado'}
            
            # Processar dados
            df_normalized = self.normalize_data(df)
            
            # Validar
            is_valid, errors = self.validate_data(df_normalized)
            if not is_valid:
                return {'sucesso': False, 'erro': f'Dados inválidos: {errors}'}
            
            # Gerar plano
            update_plan = self.generate_update_plan(df_normalized, modo_atualizacao)
            
            if not update_plan:
                return {
                    'sucesso': True, 
                    'mensagem': 'Nenhuma atualização necessária',
                    'stats': self.stats
                }
            
            # Executar atualizações
            success = self.execute_updates(update_plan)
            
            return {
                'sucesso': success,
                'stats': self.stats,
                'update_log': self.update_log,
                'plano_executado': len(update_plan)
            }
            
        except Exception as e:
            current_app.logger.error(f'Erro no processamento: {str(e)}')
            return {'sucesso': False, 'erro': str(e)}
    
    def clean_column_names(self, df):
        '''Limpa nomes de colunas inválidos'''
        try:
            new_columns = []
            for i, col in enumerate(df.columns):
                col_str = str(col).strip()
                if (col_str.startswith('Unnamed:') or 
                    col_str.isdigit() or 
                    col_str in ['nan', 'NaN', ''] or
                    len(col_str) > 50):
                    new_columns.append(f'_REMOVE_{i}')
                else:
                    new_columns.append(col_str)
            
            df.columns = new_columns
            cols_to_remove = [col for col in df.columns if col.startswith('_REMOVE_')]
            if cols_to_remove:
                df = df.drop(columns=cols_to_remove)
            
            return df
        except Exception as e:
            current_app.logger.error(f'Erro ao limpar colunas: {str(e)}')
            return df
    
    def normalize_data(self, df):
        '''Normaliza dados do DataFrame'''
        try:
            df_normalized = df.copy()
            df_normalized = self.clean_column_names(df_normalized)
            
            # Mapear colunas
            mapped_columns = {}
            for col in df_normalized.columns:
                col_clean = str(col).strip()
                if col_clean in self.column_mapping:
                    mapped_columns[col] = self.column_mapping[col_clean]
                else:
                    for map_key, map_value in self.column_mapping.items():
                        if col_clean.lower() == map_key.lower():
                            mapped_columns[col] = map_value
                            break
            
            df_normalized = df_normalized.rename(columns=mapped_columns)
            
            # Converter datas
            for field in self.date_fields:
                if field in df_normalized.columns:
                    try:
                        df_normalized[field] = pd.to_datetime(
                            df_normalized[field], 
                            errors='coerce',
                            dayfirst=True
                        ).dt.date
                    except:
                        current_app.logger.warning(f'Erro ao converter datas na coluna {field}')
            
            # Converter números
            for field in self.numeric_fields:
                if field in df_normalized.columns:
                    try:
                        df_normalized[field] = df_normalized[field].astype(str).str.replace(',', '.')
                        df_normalized[field] = pd.to_numeric(df_normalized[field], errors='coerce')
                    except:
                        current_app.logger.warning(f'Erro ao converter números na coluna {field}')
            
            # Validar CTEs
            if 'numero_cte' in df_normalized.columns:
                df_normalized['numero_cte'] = pd.to_numeric(df_normalized['numero_cte'], errors='coerce')
                df_normalized = df_normalized.dropna(subset=['numero_cte'])
                df_normalized['numero_cte'] = df_normalized['numero_cte'].astype(int)
            else:
                raise Exception('Coluna numero_cte não encontrada')
            
            return df_normalized
            
        except Exception as e:
            current_app.logger.error(f'Erro na normalização: {str(e)}')
            return pd.DataFrame()
    
    def validate_data(self, df):
        '''Valida dados do DataFrame'''
        errors = []
        
        if df.empty:
            errors.append('DataFrame está vazio')
            return False, errors
        
        if 'numero_cte' not in df.columns:
            errors.append('Coluna numero_cte não encontrada')
            return False, errors
        
        duplicates = df[df.duplicated(subset=['numero_cte'], keep=False)]
        if not duplicates.empty:
            errors.append(f'CTEs duplicados: {duplicates["numero_cte"].tolist()}')
        
        return len(errors) == 0, errors
    
    def generate_update_plan(self, df, update_mode='empty_only'):
        '''Gera plano de atualização'''
        update_plan = []
        
        try:
            # Verificar CTEs existentes
            cte_numbers = df['numero_cte'].tolist()
            existing_ctes = db.session.query(CTE.numero_cte).filter(
                CTE.numero_cte.in_(cte_numbers)
            ).all()
            existing_numbers = [r[0] for r in existing_ctes]
            
            df_to_update = df[df['numero_cte'].isin(existing_numbers)].copy()
            
            for _, row in df_to_update.iterrows():
                numero_cte = int(row['numero_cte'])
                current_cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                
                if not current_cte:
                    continue
                
                changes = {}
                
                for col in df.columns:
                    if col == 'numero_cte':
                        continue
                    
                    if col not in self.column_mapping.values():
                        continue
                    
                    new_value = row[col] if pd.notna(row[col]) else None
                    current_value = getattr(current_cte, col, None)
                    
                    # Decidir se atualizar
                    should_update = False
                    
                    if update_mode == 'all':
                        should_update = (new_value != current_value and 
                                       new_value not in [None, '', 'nan'])
                    elif update_mode == 'empty_only':
                        should_update = (current_value in [None, '', 'nan'] and 
                                       new_value not in [None, '', 'nan'])
                    
                    if should_update:
                        changes[col] = {
                            'old_value': str(current_value) if current_value else None,
                            'new_value': str(new_value) if new_value else None,
                            'raw_new_value': new_value
                        }
                
                if changes:
                    update_plan.append({
                        'numero_cte': numero_cte,
                        'changes': changes
                    })
            
            return update_plan
            
        except Exception as e:
            current_app.logger.error(f'Erro ao gerar plano: {str(e)}')
            return []
    
    def execute_updates(self, update_plan, batch_size=100):
        '''Executa atualizações no banco'''
        try:
            total_updates = len(update_plan)
            
            for i in range(0, total_updates, batch_size):
                batch = update_plan[i:i + batch_size]
                
                try:
                    for plan in batch:
                        numero_cte = plan['numero_cte']
                        changes = plan['changes']
                        
                        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                        if not cte:
                            self.stats['nao_encontrados'] += 1
                            continue
                        
                        updated = False
                        for field, change in changes.items():
                            try:
                                setattr(cte, field, change['raw_new_value'])
                                updated = True
                                
                                if field not in self.stats['campos_atualizados']:
                                    self.stats['campos_atualizados'][field] = 0
                                self.stats['campos_atualizados'][field] += 1
                                
                            except Exception as e:
                                current_app.logger.warning(f'Erro ao atualizar {field}: {str(e)}')
                        
                        if updated:
                            cte.updated_at = datetime.utcnow()
                            self.stats['atualizados'] += 1
                            
                            self.update_log.append({
                                'timestamp': datetime.now().isoformat(),
                                'numero_cte': numero_cte,
                                'changes': {k: {'old': v['old_value'], 'new': v['new_value']} 
                                          for k, v in changes.items()}
                            })
                        else:
                            self.stats['sem_alteracao'] += 1
                        
                        self.stats['total_processados'] += 1
                    
                    db.session.commit()
                    current_app.logger.info(f'Lote {i//batch_size + 1} concluído')
                    
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f'Erro no lote: {str(e)}')
                    self.stats['erros'] += len(batch)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f'Erro na execução: {str(e)}')
            return False
