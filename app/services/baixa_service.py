#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Baixas Automáticas - Dashboard Baker Flask
Migrado do Streamlit mantendo todas as funcionalidades
"""

from app.models.cte import CTE
from app import db
from datetime import datetime, date
import pandas as pd
from typing import Tuple, Dict, List
from decimal import Decimal
from sqlalchemy import func

class BaixaService:
    """Serviço para gestão de baixas automáticas"""

    @staticmethod
    def registrar_baixa(numero_cte: int, data_baixa: date, 
                       observacao: str = "", valor_baixa: float = None) -> Tuple[bool, str]:
        """
        Registra baixa de uma fatura específica com validação
        Migrado do sistema Streamlit original
        """
        try:
            # Buscar CTE
            cte = CTE.query.filter_by(numero_cte=numero_cte).first()
            
            if not cte:
                return False, f"CTE {numero_cte} não encontrado"

            # Verificar se já tem baixa
            if cte.data_baixa:
                return False, f"CTE {numero_cte} já possui baixa em {cte.data_baixa.strftime('%d/%m/%Y')}"

            # Validar valor da baixa
            if valor_baixa and abs(float(valor_baixa) - float(cte.valor_total)) > 0.01:
                observacao += f" | Valor original: R$ {cte.valor_total:.2f}, Valor baixa: R$ {valor_baixa:.2f}"

            # Registrar baixa
            cte.data_baixa = data_baixa
            if cte.observacao:
                cte.observacao = cte.observacao + f" | BAIXA: {observacao}"
            else:
                cte.observacao = f"BAIXA: {observacao}"
            
            cte.updated_at = datetime.utcnow()

            db.session.commit()
            return True, f"Baixa registrada com sucesso para CTE {numero_cte}"

        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao registrar baixa: {str(e)}"

    @staticmethod
    def processar_baixas_lote(df_baixas: pd.DataFrame) -> Dict:
        """
        Processa baixas em lote a partir de DataFrame
        Migrado do sistema Streamlit original
        """
        try:
            # Validar colunas obrigatórias
            colunas_obrigatorias = ['numero_cte', 'data_baixa']
            for col in colunas_obrigatorias:
                if col not in df_baixas.columns:
                    return {'sucesso': False, 'erro': f'Coluna obrigatória ausente: {col}'}

            # Processar cada baixa
            resultados = {
                'processadas': 0,
                'sucessos': 0,
                'erros': 0,
                'detalhes': []
            }

            for _, row in df_baixas.iterrows():
                try:
                    numero_cte = int(row['numero_cte'])
                    data_baixa = pd.to_datetime(row['data_baixa']).date()
                    observacao = row.get('observacao', '')
                    valor_baixa = row.get('valor_baixa', None)

                    sucesso, mensagem = BaixaService.registrar_baixa(
                        numero_cte, data_baixa, observacao, valor_baixa
                    )

                    resultados['processadas'] += 1
                    if sucesso:
                        resultados['sucessos'] += 1
                    else:
                        resultados['erros'] += 1

                    resultados['detalhes'].append({
                        'cte': numero_cte,
                        'sucesso': sucesso,
                        'mensagem': mensagem
                    })
                
                except Exception as e:
                    resultados['processadas'] += 1
                    resultados['erros'] += 1
                    resultados['detalhes'].append({
                        'cte': row.get('numero_cte', 'N/A'),
                        'sucesso': False,
                        'mensagem': f"Erro ao processar linha: {str(e)}"
                    })

            return {'sucesso': True, 'resultados': resultados}

        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

    @staticmethod
    def obter_estatisticas_baixas() -> Dict:
        """Retorna estatísticas de baixas para dashboard"""
        try:
            # Total de baixas
            total_baixas = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
            
            # Valor baixado
            valor_baixado = db.session.query(func.sum(CTE.valor_total)).filter(
                CTE.data_baixa.isnot(None)
            ).scalar() or 0

            # Pendentes
            baixas_pendentes = CTE.query.filter(CTE.data_baixa.is_(None)).count()
            
            # Valor pendente
            valor_pendente = db.session.query(func.sum(CTE.valor_total)).filter(
                CTE.data_baixa.is_(None)
            ).scalar() or 0

            return {
                'total_baixas': total_baixas,
                'valor_baixado': float(valor_baixado),
                'baixas_pendentes': baixas_pendentes,
                'valor_pendente': float(valor_pendente)
            }
        except Exception as e:
            return {
                'total_baixas': 0,
                'valor_baixado': 0.0,
                'baixas_pendentes': 0,
                'valor_pendente': 0.0,
                'erro': str(e)
            }