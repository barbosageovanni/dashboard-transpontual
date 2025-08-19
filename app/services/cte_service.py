#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para operações com CTEs - Dashboard Baker Flask
"""

from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
import pandas as pd
from typing import Tuple, Dict
from sqlalchemy import func, and_, or_

class CTEService:
    """Serviço para operações com CTEs"""

    @staticmethod
    def buscar_cte(numero_cte: int):
        """Busca CTE por número"""
        return CTE.query.filter_by(numero_cte=numero_cte).first()

    @staticmethod
    def criar_cte(dados: Dict) -> Tuple[bool, any]:
        """Cria novo CTE"""
        try:
            cte = CTE(**dados)
            db.session.add(cte)
            db.session.commit()
            return True, cte
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def atualizar_cte(numero_cte: int, dados: Dict) -> Tuple[bool, str]:
        """Atualiza CTE existente"""
        try:
            cte = CTE.query.filter_by(numero_cte=numero_cte).first()
            if not cte:
                return False, "CTE não encontrado"
            
            for key, value in dados.items():
                if hasattr(cte, key) and value is not None:
                    setattr(cte, key, value)
            
            cte.updated_at = datetime.utcnow()
            db.session.commit()
            return True, "CTE atualizado com sucesso"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def calcular_variacoes_tempo() -> Dict:
        """
        Calcula as variações de tempo entre processos
        Migrado do sistema Streamlit
        """
        variacoes = {}
        
        try:
            # Configurações das variações
            configs_variacoes = [
                {
                    'nome': 'CTE → Inclusão Fatura',
                    'campo_inicio': 'data_emissao',
                    'campo_fim': 'data_inclusao_fatura',
                    'meta_dias': 2,
                    'codigo': 'cte_inclusao_fatura'
                },
                {
                    'nome': 'Inclusão → 1º Envio',
                    'campo_inicio': 'data_inclusao_fatura',
                    'campo_fim': 'primeiro_envio',
                    'meta_dias': 1,
                    'codigo': 'inclusao_primeiro_envio'
                },
                {
                    'nome': 'RQ/TMC → 1º Envio',
                    'campo_inicio': 'data_rq_tmc',
                    'campo_fim': 'primeiro_envio',
                    'meta_dias': 3,
                    'codigo': 'rq_tmc_primeiro_envio'
                },
                {
                    'nome': '1º Envio → Atesto',
                    'campo_inicio': 'primeiro_envio',
                    'campo_fim': 'data_atesto',
                    'meta_dias': 7,
                    'codigo': 'primeiro_envio_atesto'
                },
                {
                    'nome': 'Atesto → Envio Final',
                    'campo_inicio': 'data_atesto',
                    'campo_fim': 'envio_final',
                    'meta_dias': 2,
                    'codigo': 'atesto_envio_final'
                }
            ]
            
            for config in configs_variacoes:
                # Query para calcular diferenças
                query = f"""
                SELECT 
                    EXTRACT(DAY FROM ({config['campo_fim']} - {config['campo_inicio']})) as dias
                FROM dashboard_baker 
                WHERE {config['campo_inicio']} IS NOT NULL 
                AND {config['campo_fim']} IS NOT NULL
                AND {config['campo_fim']} >= {config['campo_inicio']}
                """
                
                result = db.session.execute(query).fetchall()
                
                if result:
                    dias = [row[0] for row in result if row[0] is not None]
                    
                    if dias:
                        media = sum(dias) / len(dias)
                        
                        # Classificar performance
                        if media <= config['meta_dias']:
                            performance = 'excelente'
                        elif media <= config['meta_dias'] * 1.5:
                            performance = 'bom'
                        elif media <= config['meta_dias'] * 2:
                            performance = 'atencao'
                        else:
                            performance = 'critico'
                        
                        variacoes[config['codigo']] = {
                            'nome': config['nome'],
                            'media': media,
                            'qtd': len(dias),
                            'meta_dias': config['meta_dias'],
                            'performance': performance,
                            'min': min(dias),
                            'max': max(dias)
                        }
        
        except Exception as e:
            print(f"Erro ao calcular variações: {str(e)}")
        
        return variacoes

    @staticmethod
    def obter_metricas_expandidas() -> Dict:
        """Gera métricas expandidas do sistema"""
        try:
            # Métricas básicas
            total_ctes = CTE.query.count()
            clientes_unicos = db.session.query(func.count(func.distinct(CTE.destinatario_nome))).scalar()
            valor_total = db.session.query(func.sum(CTE.valor_total)).scalar() or 0
            veiculos_ativos = db.session.query(func.count(func.distinct(CTE.veiculo_placa))).scalar()

            # Métricas de pagamento
            faturas_pagas = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
            faturas_pendentes = CTE.query.filter(CTE.data_baixa.is_(None)).count()
            valor_pago = db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.isnot(None)).scalar() or 0
            valor_pendente = db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.is_(None)).scalar() or 0

            # Processos completos
            processos_completos = CTE.query.filter(
                and_(
                    CTE.data_emissao.isnot(None),
                    CTE.primeiro_envio.isnot(None),
                    CTE.data_atesto.isnot(None),
                    CTE.envio_final.isnot(None)
                )
            ).count()

            # Ticket médio
            ticket_medio = float(valor_total) / total_ctes if total_ctes > 0 else 0

            return {
                'total_ctes': total_ctes,
                'clientes_unicos': clientes_unicos,
                'valor_total': float(valor_total),
                'faturas_pagas': faturas_pagas,
                'faturas_pendentes': faturas_pendentes,
                'valor_pago': float(valor_pago),
                'valor_pendente': float(valor_pendente),
                'veiculos_ativos': veiculos_ativos,
                'processos_completos': processos_completos,
                'processos_incompletos': total_ctes - processos_completos,
                'ticket_medio': ticket_medio
            }

        except Exception as e:
            return {
                'total_ctes': 0,
                'clientes_unicos': 0,
                'valor_total': 0.0,
                'erro': str(e)
            }