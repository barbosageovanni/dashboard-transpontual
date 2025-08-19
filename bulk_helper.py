# ========================================================================================
# bulk_helper.py
"""
Helper para facilitar atualizações em lote - PostgreSQL
"""

import pandas as pd
import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.cte import CTE

# Configurações locais (sem importar bulk_config para evitar dependências circulares)
DATE_FIELDS = [
    'data_emissao', 'data_baixa', 'data_inclusao_fatura',
    'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
    'data_atesto', 'envio_final'
]

NUMERIC_FIELDS = ['valor_total']
TEXT_FIELDS = ['destinatario_nome', 'veiculo_placa', 'numero_fatura', 'observacao']

class BulkUpdateHelper:
    """
    Classe auxiliar para facilitar atualizações em lote
    """
    
    def __init__(self):
        self.app = create_app()
        self.folders = {
            'uploads': 'uploads',
            'logs': 'logs', 
            'backups': 'backups',
            'reports': 'reports',
            'templates': 'templates'
        }
        self.create_folders()
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_folders(self):
        """Cria pastas necessárias"""
        for folder in self.folders.values():
            os.makedirs(folder, exist_ok=True)
    
    def generate_sample_template(self, output_path: str = None, num_samples: int = 50) -> str:
        """
        Gera template baseado em dados reais do banco
        
        Args:
            output_path: Caminho para salvar
            num_samples: Número de CTEs de exemplo
            
        Returns:
            Caminho do arquivo gerado
        """
        if not output_path:
            output_path = f"templates/template_atualizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            with self.app.app_context():
                # Busca CTEs reais do banco como exemplo
                ctes_sample = CTE.query.limit(num_samples).all()
                
                if not ctes_sample:
                    # Se não há dados, cria exemplo fictício
                    sample_data = self._create_fictional_template()
                else:
                    # Usa dados reais mascarados
                    sample_data = self._create_real_based_template(ctes_sample)
                
                # Cria DataFrame
                df = pd.DataFrame(sample_data)
                
                # Salva com múltiplas abas
                with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                    # Aba principal com dados
                    df.to_excel(writer, sheet_name='Dados_Atualizacao', index=False)
                    
                    # Aba de instruções
                    instructions_df = self._create_instructions_sheet()
                    instructions_df.to_excel(writer, sheet_name='Instruções', index=False)
                    
                    # Aba de mapeamento de colunas
                    mapping_df = self._create_mapping_sheet()
                    mapping_df.to_excel(writer, sheet_name='Mapeamento_Colunas', index=False)
                    
                    # Aba de exemplos de valores
                    examples_df = self._create_examples_sheet()
                    examples_df.to_excel(writer, sheet_name='Exemplos_Valores', index=False)
                
                self.logger.info(f"✅ Template gerado: {output_path}")
                return output_path
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar template: {str(e)}")
            return None
    
    def _create_fictional_template(self) -> Dict:
        """Cria template com dados fictícios"""
        return {
            'numero_cte': [202410001, 202410002, 202410003, 202410004, 202410005],
            'destinatario_nome': ['Empresa ABC Ltda', 'Comercial XYZ S.A.', 'Indústria DEF', '', 'Loja GHI'],
            'veiculo_placa': ['ABC-1234', 'XYZ-5678', '', 'DEF-9012', 'GHI-3456'],
            'valor_total': [1500.50, 2300.75, 890.00, '', 1200.25],
            'data_emissao': ['2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05'],
            'data_inclusao_fatura': ['2024-10-05', '', '2024-10-07', '2024-10-08', ''],
            'data_envio_processo': ['', '2024-10-06', '2024-10-08', '', '2024-10-10'],
            'primeiro_envio': ['2024-10-06', '', '', '2024-10-09', '2024-10-11'],
            'data_rq_tmc': ['', '2024-10-07', '2024-10-09', '2024-10-10', ''],
            'data_atesto': ['', '', '2024-10-10', '', '2024-10-12'],
            'envio_final': ['', '', '', '2024-10-11', '2024-10-13'],
            'observacao': ['Entrega urgente', '', 'Cliente especial', '', 'Conferir documentos']
        }
    
    def _create_real_based_template(self, ctes: List[CTE]) -> Dict:
        """Cria template baseado em CTEs reais (dados mascarados)"""
        template = {
            'numero_cte': [],
            'destinatario_nome': [],
            'veiculo_placa': [],
            'valor_total': [],
            'data_emissao': [],
            'data_inclusao_fatura': [],
            'data_envio_processo': [],
            'primeiro_envio': [],
            'data_rq_tmc': [],
            'data_atesto': [],
            'envio_final': [],
            'observacao': []
        }
        
        for cte in ctes:
            template['numero_cte'].append(cte.numero_cte)
            template['destinatario_nome'].append(cte.destinatario_nome or '')
            template['veiculo_placa'].append(cte.veiculo_placa or '')
            template['valor_total'].append(float(cte.valor_total) if cte.valor_total else '')
            template['data_emissao'].append(cte.data_emissao.strftime('%Y-%m-%d') if cte.data_emissao else '')
            template['data_inclusao_fatura'].append(cte.data_inclusao_fatura.strftime('%Y-%m-%d') if cte.data_inclusao_fatura else '')
            template['data_envio_processo'].append(cte.data_envio_processo.strftime('%Y-%m-%d') if cte.data_envio_processo else '')
            template['primeiro_envio'].append(cte.primeiro_envio.strftime('%Y-%m-%d') if cte.primeiro_envio else '')
            template['data_rq_tmc'].append(cte.data_rq_tmc.strftime('%Y-%m-%d') if cte.data_rq_tmc else '')
            template['data_atesto'].append(cte.data_atesto.strftime('%Y-%m-%d') if cte.data_atesto else '')
            template['envio_final'].append(cte.envio_final.strftime('%Y-%m-%d') if cte.envio_final else '')
            template['observacao'].append(cte.observacao or '')
        
        return template
    
    def _create_instructions_sheet(self) -> pd.DataFrame:
        """Cria aba de instruções"""
        instructions = [
            {
                'Campo': 'numero_cte',
                'Descrição': 'Número do CTE (obrigatório para identificação)',
                'Formato': 'Número inteiro (ex: 202410001)',
                'Obrigatório': 'Sim',
                'Exemplo': '202410001'
            },
            {
                'Campo': 'destinatario_nome',
                'Descrição': 'Nome do cliente/destinatário',
                'Formato': 'Texto até 255 caracteres',
                'Obrigatório': 'Não',
                'Exemplo': 'Empresa ABC Ltda'
            },
            {
                'Campo': 'veiculo_placa',
                'Descrição': 'Placa do veículo',
                'Formato': 'Padrão brasileiro (ABC-1234 ou ABC1D23)',
                'Obrigatório': 'Não',
                'Exemplo': 'ABC-1234'
            },
            {
                'Campo': 'valor_total',
                'Descrição': 'Valor total do frete',
                'Formato': 'Decimal com ponto (ex: 1500.50)',
                'Obrigatório': 'Não',
                'Exemplo': '1500.50'
            },
            {
                'Campo': 'data_emissao',
                'Descrição': 'Data de emissão do CTE',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-15'
            },
            {
                'Campo': 'data_inclusao_fatura',
                'Descrição': 'Data de inclusão na fatura',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-20'
            },
            {
                'Campo': 'data_envio_processo',
                'Descrição': 'Data de envio do processo',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-22'
            },
            {
                'Campo': 'primeiro_envio',
                'Descrição': 'Data do primeiro envio',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-23'
            },
            {
                'Campo': 'data_rq_tmc',
                'Descrição': 'Data RQ/TMC',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-25'
            },
            {
                'Campo': 'data_atesto',
                'Descrição': 'Data do atesto',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-26'
            },
            {
                'Campo': 'envio_final',
                'Descrição': 'Data do envio final',
                'Formato': 'YYYY-MM-DD',
                'Obrigatório': 'Não',
                'Exemplo': '2024-10-28'
            },
            {
                'Campo': 'observacao',
                'Descrição': 'Observações gerais',
                'Formato': 'Texto até 1000 caracteres',
                'Obrigatório': 'Não',
                'Exemplo': 'Entrega urgente'
            }
        ]
        
        return pd.DataFrame(instructions)
    
    def _create_mapping_sheet(self) -> pd.DataFrame:
        """Cria aba de mapeamento de colunas"""
        mapping_data = []
        
        for excel_col, db_field in COLUMN_MAPPING.items():
            mapping_data.append({
                'Nome_no_Excel': excel_col,
                'Campo_no_Banco': db_field,
                'Aceita_Variações': 'Sim'
            })
        
        return pd.DataFrame(mapping_data)
    
    def _create_examples_sheet(self) -> pd.DataFrame:
        """Cria aba com exemplos de valores"""
        examples = [
            {
                'Tipo': 'Data',
                'Formato_Correto': '2024-10-15',
                'Formatos_Aceitos': '2024-10-15, 15/10/2024, 15-10-2024',
                'Formato_Incorreto': '10/15/2024, 2024/10/15'
            },
            {
                'Tipo': 'Valor Monetário',
                'Formato_Correto': '1500.50',
                'Formatos_Aceitos': '1500.50, 1500,50 (será convertido)',
                'Formato_Incorreto': 'R$ 1.500,50, 1.500.50'
            },
            {
                'Tipo': 'Placa Veículo',
                'Formato_Correto': 'ABC-1234',
                'Formatos_Aceitos': 'ABC-1234, ABC1234, ABC1D23',
                'Formato_Incorreto': 'abc-1234, 1234-ABC'
            },
            {
                'Tipo': 'CTE',
                'Formato_Correto': '202410001',
                'Formatos_Aceitos': 'Apenas números inteiros',
                'Formato_Incorreto': 'CTE202410001, 2024.10.001'
            }
        ]
        
        return pd.DataFrame(examples)
    
    def validate_upload_file(self, file_path: str) -> Dict:
        """
        Valida arquivo antes da atualização
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com resultado da validação
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'statistics': {},
            'preview': {}
        }
        
        try:
            # Carrega arquivo
            if file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
            
            # Estatísticas básicas
            result['statistics'] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns_found': list(df.columns),
                'empty_cells_per_column': df.isnull().sum().to_dict()
            }
            
            # Verifica colunas obrigatórias
            has_cte_column = False
            for col in df.columns:
                if col.lower() in [k.lower() for k in COLUMN_MAPPING.keys() if COLUMN_MAPPING[k] == 'numero_cte']:
                    has_cte_column = True
                    break
            
            if not has_cte_column:
                result['errors'].append("Coluna de identificação CTE não encontrada")
                return result
            
            # Normaliza dados para validação
            from bulk_update_cte import BulkCTEUpdaterDB
            updater = BulkCTEUpdaterDB()
            df_normalized = updater.normalize_data(df)
            
            if df_normalized.empty:
                result['errors'].append("Nenhum dado válido encontrado após normalização")
                return result
            
            # Validações específicas
            if 'numero_cte' in df_normalized.columns:
                # CTEs duplicados
                duplicates = df_normalized[df_normalized.duplicated(subset=['numero_cte'], keep=False)]
                if not duplicates.empty:
                    result['warnings'].append(f"CTEs duplicados: {duplicates['numero_cte'].tolist()}")
                
                # CTEs inválidos
                invalid_ctes = df_normalized[
                    (df_normalized['numero_cte'] <= 0) | 
                    (df_normalized['numero_cte'] > 999999999)
                ]
                if not invalid_ctes.empty:
                    result['errors'].append(f"CTEs com valores inválidos: {invalid_ctes['numero_cte'].tolist()}")
                
                # Verifica quais CTEs existem no banco
                with self.app.app_context():
                    existing_ctes, not_found = updater.check_existing_ctes(df_normalized)
                    result['statistics']['ctes_existing'] = len(existing_ctes)
                    result['statistics']['ctes_not_found'] = len(not_found)
                    
                    if not_found:
                        result['warnings'].append(f"CTEs não encontrados no banco: {not_found[:10]}{'...' if len(not_found) > 10 else ''}")
            
            # Valida datas
            for field in DATE_FIELDS:
                if field in df_normalized.columns:
                    invalid_dates = df_normalized[
                        df_normalized[field].notna() & 
                        pd.to_datetime(df_normalized[field], errors='coerce').isna()
                    ]
                    if not invalid_dates.empty:
                        result['warnings'].append(f"Datas inválidas em {field}: {len(invalid_dates)} registros")
            
            # Valida valores numéricos
            for field in NUMERIC_FIELDS:
                if field in df_normalized.columns:
                    invalid_values = df_normalized[
                        df_normalized[field].notna() & 
                        pd.to_numeric(df_normalized[field], errors='coerce').isna()
                    ]
                    if not invalid_values.empty:
                        result['warnings'].append(f"Valores inválidos em {field}: {len(invalid_values)} registros")
            
            # Preview dos dados
            result['preview'] = {
                'sample_data': df_normalized.head(5).to_dict('records'),
                'column_mapping_applied': {
                    original: mapped for original, mapped in zip(df.columns, df_normalized.columns)
                }
            }
            
            result['valid'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Erro ao processar arquivo: {str(e)}")
        
        return result
    
    def get_database_statistics(self) -> Dict:
        """
        Obtém estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with self.app.app_context():
                stats = {
                    'total_ctes': CTE.query.count(),
                    'ctes_with_baixa': CTE.query.filter(CTE.data_baixa.isnot(None)).count(),
                    'ctes_complete_process': CTE.query.filter(
                        and_(
                            CTE.data_emissao.isnot(None),
                            CTE.primeiro_envio.isnot(None),
                            CTE.data_atesto.isnot(None),
                            CTE.envio_final.isnot(None)
                        )
                    ).count(),
                    'last_update': datetime.now().isoformat(),
                    'fields_completion': {}
                }
                
                # Estatísticas de preenchimento por campo
                all_fields = DATE_FIELDS + NUMERIC_FIELDS + TEXT_FIELDS
                for field in all_fields:
                    if hasattr(CTE, field):
                        filled_count = CTE.query.filter(getattr(CTE, field).isnot(None)).count()
                        stats['fields_completion'][field] = {
                            'filled': filled_count,
                            'empty': stats['total_ctes'] - filled_count,
                            'percentage': round((filled_count / stats['total_ctes']) * 100, 2) if stats['total_ctes'] > 0 else 0
                        }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {'error': str(e)}
    
    def cleanup_old_files(self, days_old: int = 30) -> Dict:
        """
        Remove arquivos antigos das pastas
        
        Args:
            days_old: Arquivos mais antigos que X dias
            
        Returns:
            Resultado da limpeza
        """
        result = {
            'files_removed': 0,
            'space_freed_mb': 0,
            'errors': []
        }
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            for folder in self.folders.values():
                if not os.path.exists(folder):
                    continue
                
                for file_name in os.listdir(folder):
                    file_path = os.path.join(folder, file_name)
                    
                    if os.path.isfile(file_path):
                        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_mod_time < cutoff_date:
                            try:
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                
                                result['files_removed'] += 1
                                result['space_freed_mb'] += file_size / (1024 * 1024)
                                
                            except Exception as e:
                                result['errors'].append(f"Erro ao remover {file_path}: {str(e)}")
            
            result['space_freed_mb'] = round(result['space_freed_mb'], 2)
            self.logger.info(f"🧹 Limpeza concluída: {result['files_removed']} arquivos removidos")
            
        except Exception as e:
            result['errors'].append(f"Erro geral na limpeza: {str(e)}")
        
        return result

