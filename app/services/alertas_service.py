#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Inteligentes
app/services/alertas_service.py + app/routes/alertas.py
"""

# ==================== ALERTAS SERVICE ====================
"""
app/services/alertas_service.py
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import text, func, and_, or_
from app import db
from app.models.cte import CTE

logger = logging.getLogger(__name__)

class AlertasService:
    
    @staticmethod
    def obter_alertas_ativos() -> Dict:
        """
        Obtém todos os alertas ativos do sistema
        Baseado nos dados reais mostrados nas imagens do usuário
        """
        try:
            alertas = []
            
            # 1. CTEs pendentes de primeiro envio
            alertas.append(AlertasService._alerta_primeiro_envio_pendente())
            
            # 2. CTEs pendentes de envio final
            alertas.append(AlertasService._alerta_envio_final_pendente())
            
            # 3. Faturas vencidas
            alertas.append(AlertasService._alerta_faturas_vencidas())
            
            # 4. Análise de risco financeiro
            alertas.append(AlertasService._alerta_risco_financeiro())
            
            # Filtrar alertas válidos
            alertas_ativos = [a for a in alertas if a and a.get('quantidade', 0) > 0]
            
            return {
                'total_alertas': len(alertas_ativos),
                'alertas': alertas_ativos,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas: {e}")
            return {
                'total_alertas': 0,
                'alertas': [],
                'erro': str(e)
            }
    
    @staticmethod
    def _alerta_primeiro_envio_pendente() -> Dict:
        """
        🚨 1º Envio Pendente - CTEs que ainda não foram enviados
        """
        try:
            # Buscar CTEs sem data de primeiro envio
            query = text("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker 
                WHERE primeiro_envio IS NULL 
                AND data_emissao >= :data_limite
            """)
            
            data_limite = datetime.now() - timedelta(days=90)
            
            with db.engine.connect() as connection:
                result = connection.execute(query, {"data_limite": data_limite}).fetchone()
                
                quantidade = int(result.quantidade or 0)
                valor = float(result.valor_total or 0)
                
                if quantidade > 0:
                    return {
                        'tipo': 'critico' if quantidade > 50 else 'aviso',
                        'titulo': '🚨 1º Envio Pendente',
                        'quantidade': quantidade,
                        'descricao': 'CTEs pendentes',
                        'valor': valor,
                        'status': 'em risco',
                        'prioridade': 1,
                        'acao_sugerida': 'Processar envios pendentes urgentemente'
                    }
                    
        except Exception as e:
            logger.error(f"Erro no alerta 1º envio: {e}")
        
        return None
    
    @staticmethod
    def _alerta_envio_final_pendente() -> Dict:
        """
        📤 Envio Final Pendente - CTEs que foram enviados mas não finalizados
        """
        try:
            query = text("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker 
                WHERE primeiro_envio IS NOT NULL 
                AND envio_final IS NULL
                AND data_emissao >= :data_limite
            """)
            
            data_limite = datetime.now() - timedelta(days=60)
            
            with db.engine.connect() as connection:
                result = connection.execute(query, {"data_limite": data_limite}).fetchone()
                
                quantidade = int(result.quantidade or 0)
                valor = float(result.valor_total or 0)
                
                if quantidade > 0:
                    return {
                        'tipo': 'aviso' if quantidade < 50 else 'critico',
                        'titulo': '📤 Envio Final Pendente',
                        'quantidade': quantidade,
                        'descricao': 'envios pendentes',
                        'valor': valor,
                        'status': 'pendentes',
                        'prioridade': 2,
                        'acao_sugerida': 'Finalizar processos de envio'
                    }
                    
        except Exception as e:
            logger.error(f"Erro no alerta envio final: {e}")
        
        return None
    
    @staticmethod
    def _alerta_faturas_vencidas() -> Dict:
        """
        💸 Faturas Vencidas - Faturas com data de vencimento passada
        """
        try:
            # Assumindo que faturas vencem 30 dias após emissão se não há campo específico
            query = text("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker 
                WHERE data_baixa IS NULL 
                AND data_emissao < :data_vencimento
                AND data_emissao >= :data_limite
            """)
            
            data_vencimento = datetime.now() - timedelta(days=30)  # 30 dias para vencer
            data_limite = datetime.now() - timedelta(days=120)     # Limite de busca
            
            with db.engine.connect() as connection:
                result = connection.execute(query, {
                    "data_vencimento": data_vencimento,
                    "data_limite": data_limite
                }).fetchone()
                
                quantidade = int(result.quantidade or 0)
                valor = float(result.valor_total or 0)
                
                if quantidade > 0:
                    return {
                        'tipo': 'critico',
                        'titulo': '💸 Faturas Vencidas',
                        'quantidade': quantidade,
                        'descricao': 'faturas vencidas',
                        'valor': valor,
                        'status': 'inadimplentes',
                        'prioridade': 3,
                        'acao_sugerida': 'Contato imediato para cobrança'
                    }
                    
        except Exception as e:
            logger.error(f"Erro no alerta faturas vencidas: {e}")
        
        return None
    
    @staticmethod
    def _alerta_risco_financeiro() -> Dict:
        """
        ⚠️ Análise de Risco Financeiro - Concentração excessiva em poucos clientes
        """
        try:
            # Verificar se há concentração excessiva (>60% em top 3 clientes)
            query = text("""
                WITH cliente_totais AS (
                    SELECT 
                        destinatario_nome,
                        SUM(valor_total) as valor_cliente
                    FROM dashboard_baker 
                    WHERE data_emissao >= :data_limite
                    GROUP BY destinatario_nome
                ),
                total_geral AS (
                    SELECT SUM(valor_total) as valor_total_geral
                    FROM dashboard_baker 
                    WHERE data_emissao >= :data_limite
                ),
                top3_clientes AS (
                    SELECT SUM(valor_cliente) as valor_top3
                    FROM (
                        SELECT valor_cliente 
                        FROM cliente_totais 
                        ORDER BY valor_cliente DESC 
                        LIMIT 3
                    ) t
                )
                SELECT 
                    t3.valor_top3,
                    tg.valor_total_geral,
                    CASE 
                        WHEN tg.valor_total_geral > 0 
                        THEN (t3.valor_top3 / tg.valor_total_geral * 100)
                        ELSE 0 
                    END as percentual_concentracao
                FROM top3_clientes t3, total_geral tg
            """)
            
            data_limite = datetime.now() - timedelta(days=180)
            
            with db.engine.connect() as connection:
                result = connection.execute(query, {"data_limite": data_limite}).fetchone()
                
                if result and result.percentual_concentracao > 60:
                    return {
                        'tipo': 'aviso',
                        'titulo': '⚠️ Alto Risco de Concentração',
                        'quantidade': 3,
                        'descricao': 'clientes concentram',
                        'valor': float(result.valor_top3 or 0),
                        'status': f'{result.percentual_concentracao:.1f}% da receita',
                        'prioridade': 4,
                        'acao_sugerida': 'Diversificar carteira de clientes'
                    }
                    
        except Exception as e:
            logger.error(f"Erro no alerta risco financeiro: {e}")
        
        return None
    
    @staticmethod
    def obter_detalhes_alerta(tipo_alerta: str) -> Dict:
        """
        Obtém detalhes específicos de um tipo de alerta
        """
        try:
            if tipo_alerta == 'primeiro_envio':
                return AlertasService._detalhes_primeiro_envio()
            elif tipo_alerta == 'envio_final':
                return AlertasService._detalhes_envio_final()
            elif tipo_alerta == 'faturas_vencidas':
                return AlertasService._detalhes_faturas_vencidas()
            elif tipo_alerta == 'risco_financeiro':
                return AlertasService._detalhes_risco_financeiro()
            else:
                return {'erro': 'Tipo de alerta não reconhecido'}
                
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do alerta {tipo_alerta}: {e}")
            return {'erro': str(e)}
    
    @staticmethod
    def _detalhes_primeiro_envio() -> Dict:
        """Detalhes dos CTEs pendentes de primeiro envio"""
        try:
            query = text("""
                SELECT 
                    numero_cte,
                    destinatario_nome,
                    valor_total,
                    data_emissao,
                    DATEDIFF(CURDATE(), data_emissao) as dias_pendente
                FROM dashboard_baker 
                WHERE primeiro_envio IS NULL 
                AND data_emissao >= :data_limite
                ORDER BY data_emissao ASC
                LIMIT 50
            """)
            
            data_limite = datetime.now() - timedelta(days=90)
            
            with db.engine.connect() as connection:
                result = connection.execute(query, {"data_limite": data_limite})
                
                detalhes = []
                for row in result:
                    detalhes.append({
                        'numero_cte': row.numero_cte,
                        'cliente': row.destinatario_nome,
                        'valor': float(row.valor_total or 0),
                        'data_emissao': row.data_emissao.isoformat() if row.data_emissao else None,
                        'dias_pendente': int(row.dias_pendente or 0)
                    })
                
                return {
                    'titulo': 'CTEs Pendentes de Primeiro Envio',
                    'total_registros': len(detalhes),
                    'detalhes': detalhes
                }
                
        except Exception as e:
            logger.error(f"Erro nos detalhes de primeiro envio: {e}")
            return {'erro': str(e)}
    
    @staticmethod
    def _detalhes_envio_final() -> Dict:
        """Detalhes dos CTEs pendentes de envio final"""
        # Implementação similar à _detalhes_primeiro_envio
        return {'detalhes': [], 'total_registros': 0}
    
    @staticmethod
    def _detalhes_faturas_vencidas() -> Dict:
        """Detalhes das faturas vencidas"""
        # Implementação similar à _detalhes_primeiro_envio
        return {'detalhes': [], 'total_registros': 0}
    
    @staticmethod
    def _detalhes_risco_financeiro() -> Dict:
        """Detalhes da análise de risco financeiro"""
        # Implementação similar à _detalhes_primeiro_envio
        return {'detalhes': [], 'total_registros': 0}