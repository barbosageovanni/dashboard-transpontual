# bulk_config.py
"""
Configurações do Sistema de Atualização CTE - PostgreSQL Supabase
"""

import os
from datetime import datetime

# Configurações do banco de dados (usa as mesmas do sistema principal)
DATABASE_CONFIG = {
    'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'Mariaana953@7334'
}

# Configurações de arquivos
FOLDERS = {
    'uploads': 'uploads',
    'logs': 'logs',
    'backups': 'backups',
    'reports': 'reports',
    'templates': 'templates'
}

# Mapeamento completo de colunas
COLUMN_MAPPING = {
    # Identificação (todas as variações possíveis)
    'CTE': 'numero_cte',
    'Numero_CTE': 'numero_cte',
    'CTRC': 'numero_cte',
    'numero_cte': 'numero_cte',
    'Número CTE': 'numero_cte',
    'Número do CTE': 'numero_cte',
    
    # Dados principais
    'Cliente': 'destinatario_nome',
    'Destinatario': 'destinatario_nome',
    'Destinatário': 'destinatario_nome',
    'Nome Cliente': 'destinatario_nome',
    'destinatario_nome': 'destinatario_nome',
    
    'Veiculo': 'veiculo_placa',
    'Veículo': 'veiculo_placa',
    'Placa': 'veiculo_placa',
    'Placa Veiculo': 'veiculo_placa',
    'veiculo_placa': 'veiculo_placa',
    
    'Valor_Frete': 'valor_total',
    'Valor': 'valor_total',
    'Valor Total': 'valor_total',
    'Vlr_Frete': 'valor_total',
    'valor_total': 'valor_total',
    
    # Datas principais
    'Data_Emissao': 'data_emissao',
    'Data de Emissão': 'data_emissao',
    'Data Emissão': 'data_emissao',
    'Dt_Emissao': 'data_emissao',
    'data_emissao': 'data_emissao',
    
    'Data_Baixa': 'data_baixa',
    'Data de Baixa': 'data_baixa',
    'Data Baixa': 'data_baixa',
    'data_baixa': 'data_baixa',
    
    # Informações de faturamento
    'Numero_Fatura': 'numero_fatura',
    'Número Fatura': 'numero_fatura',
    'Fatura': 'numero_fatura',
    'numero_fatura': 'numero_fatura',
    
    'Data_Inclusao_Fatura': 'data_inclusao_fatura',
    'Data Inclusão Fatura': 'data_inclusao_fatura',
    'Inclusão Fatura': 'data_inclusao_fatura',
    'data_inclusao_fatura': 'data_inclusao_fatura',
    
    'Data_Envio_Processo': 'data_envio_processo',
    'Data Envio Processo': 'data_envio_processo',
    'Envio Processo': 'data_envio_processo',
    'data_envio_processo': 'data_envio_processo',
    
    'Data_Primeiro_Envio': 'primeiro_envio',
    'Data Primeiro Envio': 'primeiro_envio',
    'Primeiro Envio': 'primeiro_envio',
    'primeiro_envio': 'primeiro_envio',
    
    'Data_RQ_TMC': 'data_rq_tmc',
    'Data RQ/TMC': 'data_rq_tmc',
    'RQ/TMC': 'data_rq_tmc',
    'data_rq_tmc': 'data_rq_tmc',
    
    'Data_Atesto': 'data_atesto',
    'Data de Atesto': 'data_atesto',
    'Data Atesto': 'data_atesto',
    'Atesto': 'data_atesto',
    'data_atesto': 'data_atesto',
    
    'Data_Envio_Final': 'envio_final',
    'Data Envio Final': 'envio_final',
    'Envio Final': 'envio_final',
    'envio_final': 'envio_final',
    
    # Observações
    'Observacoes': 'observacao',
    'Observações': 'observacao',
    'Observacao': 'observacao',
    'Observação': 'observacao',
    'Comentarios': 'observacao',
    'Comentários': 'observacao',
    'observacao': 'observacao'
}

# Campos obrigatórios
REQUIRED_FIELDS = ['numero_cte']

# Campos de data para validação
DATE_FIELDS = [
    'data_emissao', 'data_baixa', 'data_inclusao_fatura',
    'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
    'data_atesto', 'envio_final'
]

# Campos numéricos
NUMERIC_FIELDS = ['valor_total']

# Campos de texto
TEXT_FIELDS = ['destinatario_nome', 'veiculo_placa', 'numero_fatura', 'observacao']

# Regras de validação
VALIDATION_RULES = {
    'numero_cte': {
        'type': 'integer',
        'min_value': 1,
        'max_value': 999999999,
        'required': True
    },
    'valor_total': {
        'type': 'decimal',
        'min_value': 0,
        'max_value': 999999.99,
        'format': 'currency'
    },
    'destinatario_nome': {
        'type': 'string',
        'max_length': 255
    },
    'veiculo_placa': {
        'type': 'string',
        'max_length': 20,
        'pattern': r'^[A-Z]{3}-?\d{4}$|^[A-Z]{3}\d[A-Z]\d{2}$'  # Placas brasileiras
    },
    'observacao': {
        'type': 'text',
        'max_length': 1000
    }
}

# Configurações de backup
BACKUP_CONFIG = {
    'enabled': True,
    'auto_backup_before_update': True,
    'max_backups': 15,
    'backup_format': 'json',
    'include_metadata': True
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    'batch_size': 100,
    'max_concurrent_updates': 5,
    'timeout_seconds': 300,
    'retry_attempts': 3,
    'retry_delay': 1
}