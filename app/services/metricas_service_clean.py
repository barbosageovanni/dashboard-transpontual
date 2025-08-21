#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Métricas - SEM DEBUG EXCESSIVO
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
from sqlalchemy import func, and_, or_

# DESABILITAR LOGS EXCESSIVOS EM PRODUÇÃO
import logging
import os

# Configurar nível de log baseado no ambiente
if os.environ.get('FLASK_ENV') == 'production':
    logging.getLogger().setLevel(logging.ERROR)

class MetricasService:
    '''Serviço de métricas SEM debug excessivo'''
    
    @staticmethod
    def calcular_metricas_resumidas():
        '''Calcula métricas básicas SEM logs excessivos'''
        try:
            # Buscar dados sem debug
            total_ctes = CTE.query.count()
            
            if total_ctes == 0:
                return {
                    'success': True,
                    'metricas': {
                        'total_ctes': 0,
                        'valor_total': 0.0,
                        'valor_pago': 0.0,
                        'valor_pendente': 0.0,
                        'clientes_unicos': 0,
                        'processos_completos': 0,
                        'taxa_conclusao': 0.0
                    },
                    'alertas': {},
                    'variacoes': {}
                }
            
            # Calcular métricas básicas
            ctes = CTE.query.all()
            
            valor_total = sum(float(cte.valor_total or 0) for cte in ctes)
            valor_pago = sum(float(cte.valor_total or 0) for cte in ctes if cte.data_baixa)
            valor_pendente = valor_total - valor_pago
            
            clientes_unicos = len(set(cte.destinatario_nome for cte in ctes if cte.destinatario_nome))
            
            processos_completos = sum(1 for cte in ctes if (
                cte.data_emissao and cte.primeiro_envio and 
                cte.data_atesto and cte.envio_final
            ))
            
            taxa_conclusao = (processos_completos / total_ctes * 100) if total_ctes > 0 else 0
            
            return {
                'success': True,
                'metricas': {
                    'total_ctes': total_ctes,
                    'valor_total': valor_total,
                    'valor_pago': valor_pago,
                    'valor_pendente': valor_pendente,
                    'clientes_unicos': clientes_unicos,
                    'processos_completos': processos_completos,
                    'taxa_conclusao': round(taxa_conclusao, 2)
                },
                'alertas': {},
                'variacoes': {}
            }
            
        except Exception as e:
            # Log apenas erros críticos
            if os.environ.get('FLASK_ENV') != 'production':
                print(f"Erro métricas: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'metricas': {},
                'alertas': {},
                'variacoes': {}
            }
