#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Análise por Veículo - VERSÃO CORRIGIDA
app/services/analise_veiculo_service_corrigido.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
import logging

class AnaliseVeiculoServiceCorrigido:
    """Serviço para análise detalhada por veículo - VERSÃO CORRIGIDA"""
    
    @staticmethod
    def analise_completa_veiculos(filtro_dias: int = 180, filtro_veiculo: str = None) -> Dict:
        """
        Análise completa de veículos usando apenas campos que existem no modelo
        """
        try:
            # Calcular data limite
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Query base - usar apenas campos que sabemos que existem
            query = CTE.query.filter(
                CTE.data_emissao >= data_limite,
                CTE.valor_total.isnot(None)
            )
            
            # Verificar se campo placa existe
            if hasattr(CTE, 'veiculo_placa'):
                query = query.filter(CTE.veiculo_placa.isnot(None))
                if filtro_veiculo:
                    query = query.filter(CTE.veiculo_placa.ilike(f'%{filtro_veiculo}%'))
            elif hasattr(CTE, 'placa'):
                query = query.filter(CTE.placa.isnot(None))
                if filtro_veiculo:
                    query = query.filter(CTE.placa.ilike(f'%{filtro_veiculo}%'))
            
            ctes = query.all()
            
            if not ctes:
                return AnaliseVeiculoServiceCorrigido._analise_vazia()
            
            # Preparar dados usando campos que existem
            dados = []
            for cte in ctes:
                # Mapear campos dinamicamente
                placa = getattr(cte, 'veiculo_placa', None) or getattr(cte, 'placa', 'SEM_PLACA')
                destinatario = getattr(cte, 'destinatario_nome', None) or getattr(cte, 'destinatario', 'SEM_NOME')
                
                dados.append({
                    'veiculo_placa': str(placa).strip().upper() if placa else 'SEM_PLACA',
                    'numero_cte': cte.numero_cte,
                    'valor_total': float(cte.valor_total or 0),
                    'data_emissao': cte.data_emissao,
                    'destinatario_nome': destinatario,
                    'origem_cidade': 'N/A',  # Campo padrão se não existir
                    'destino_cidade': 'N/A',  # Campo padrão se não existir
                    'has_baixa': getattr(cte, 'has_baixa', False),
                    'data_baixa': getattr(cte, 'data_baixa', None),
                    'processo_completo': getattr(cte, 'processo_completo', False),
                    'mes_emissao': cte.data_emissao.strftime('%Y-%m') if cte.data_emissao else None
                })
            
            df = pd.DataFrame(dados)
            
            # Análises principais
            ranking_veiculos = AnaliseVeiculoServiceCorrigido._calcular_ranking_veiculos(df)
            metricas_performance = AnaliseVeiculoServiceCorrigido._calcular_metricas_performance(df)
            
            # Insights simples
            insights = AnaliseVeiculoServiceCorrigido._gerar_insights_simples(ranking_veiculos)
            
            return {
                'success': True,
                'total_veiculos': len(df['veiculo_placa'].unique()),
                'total_viagens': len(df),
                'faturamento_total': df['valor_total'].sum(),
                'periodo_analise': {
                    'data_inicio': data_limite.strftime('%d/%m/%Y'),
                    'data_fim': datetime.now().date().strftime('%d/%m/%Y'),
                    'dias': filtro_dias
                },
                'ranking_veiculos': ranking_veiculos,
                'metricas_performance': metricas_performance,
                'insights': insights
            }
            
        except Exception as e:
            logging.error(f"Erro na análise de veículos: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _calcular_ranking_veiculos(df: pd.DataFrame) -> List[Dict]:
        """Calcula ranking simplificado dos veículos"""
        try:
            # Agrupar por veículo
            resultado = df.groupby('veiculo_placa').agg({
                'valor_total': ['sum', 'mean', 'count'],
                'destinatario_nome': 'nunique',
                'has_baixa': 'sum'
            }).round(2)
            
            # Flatten column names
            resultado.columns = [
                'faturamento_total', 'ticket_medio', 'total_viagens',
                'clientes_unicos', 'baixas_realizadas'
            ]
            
            # Calcular métricas adicionais
            resultado['taxa_baixa'] = (resultado['baixas_realizadas'] / resultado['total_viagens'] * 100).round(2)
            
            # Converter para lista
            ranking = []
            for placa, row in resultado.iterrows():
                # Score simples baseado em faturamento e viagens
                score_total = min(100, (row['faturamento_total'] / resultado['faturamento_total'].max() * 70) + 
                                       (row['total_viagens'] / resultado['total_viagens'].max() * 30))
                
                # Classificação
                if score_total >= 80:
                    classificacao = "Excelente"
                    cor = "success"
                elif score_total >= 60:
                    classificacao = "Bom"
                    cor = "info"
                elif score_total >= 40:
                    classificacao = "Regular"
                    cor = "warning"
                else:
                    classificacao = "Baixa Performance"
                    cor = "danger"
                
                ranking.append({
                    'veiculo_placa': placa,
                    'faturamento_total': float(row['faturamento_total']),
                    'total_viagens': int(row['total_viagens']),
                    'ticket_medio': float(row['ticket_medio']),
                    'clientes_unicos': int(row['clientes_unicos']),
                    'taxa_baixa': float(row['taxa_baixa']),
                    'score_performance': round(score_total, 2),
                    'classificacao': classificacao,
                    'cor_classificacao': cor
                })
            
            # Ordenar por faturamento
            ranking.sort(key=lambda x: x['faturamento_total'], reverse=True)
            
            return ranking
            
        except Exception as e:
            logging.error(f"Erro no ranking de veículos: {str(e)}")
            return []
    
    @staticmethod
    def _calcular_metricas_performance(df: pd.DataFrame) -> Dict:
        """Calcula métricas simplificadas da frota"""
        try:
            total_veiculos = df['veiculo_placa'].nunique()
            
            if total_veiculos == 0:
                return {}
            
            # Métricas por veículo
            faturamento_por_veiculo = df.groupby('veiculo_placa')['valor_total'].sum()
            viagens_por_veiculo = df.groupby('veiculo_placa').size()
            
            return {
                'total_veiculos_ativos': total_veiculos,
                'faturamento_medio_por_veiculo': round(faturamento_por_veiculo.mean(), 2),
                'faturamento_mediano_por_veiculo': round(faturamento_por_veiculo.median(), 2),
                'viagens_media_por_veiculo': round(viagens_por_veiculo.mean(), 2),
                'maior_faturamento_veiculo': {
                    'placa': faturamento_por_veiculo.idxmax(),
                    'valor': round(faturamento_por_veiculo.max(), 2)
                },
                'veiculo_mais_viagens': {
                    'placa': viagens_por_veiculo.idxmax(),
                    'quantidade': int(viagens_por_veiculo.max())
                }
            }
            
        except Exception as e:
            logging.error(f"Erro nas métricas de performance: {str(e)}")
            return {}
    
    @staticmethod
    def _gerar_insights_simples(ranking_veiculos: List[Dict]) -> List[Dict]:
        """Gera insights simples baseado no ranking"""
        insights = []
        
        try:
            if ranking_veiculos:
                # Insight sobre o veículo top
                top_veiculo = ranking_veiculos[0]
                insights.append({
                    'tipo': 'destaque',
                    'titulo': f'Veículo Destaque: {top_veiculo["veiculo_placa"]}',
                    'descricao': f'Líder em faturamento com R$ {top_veiculo["faturamento_total"]:,.2f}',
                    'cor': 'success'
                })
                
                # Insight sobre performance baixa
                baixa_performance = [v for v in ranking_veiculos if v['score_performance'] < 40]
                if baixa_performance:
                    insights.append({
                        'tipo': 'melhoria',
                        'titulo': f'{len(baixa_performance)} Veículos com Baixa Performance',
                        'descricao': 'Considere analisar operação destes veículos',
                        'cor': 'info'
                    })
            
            return insights
            
        except Exception as e:
            logging.error(f"Erro ao gerar insights: {str(e)}")
            return []
    
    @staticmethod
    def obter_lista_veiculos() -> List[str]:
        """Obtém lista de placas usando campos que existem"""
        try:
            # Tentar diferentes campos de placa
            if hasattr(CTE, 'veiculo_placa'):
                veiculos = db.session.query(CTE.veiculo_placa).distinct().filter(
                    CTE.veiculo_placa.isnot(None)
                ).order_by(CTE.veiculo_placa).all()
            elif hasattr(CTE, 'placa'):
                veiculos = db.session.query(CTE.placa).distinct().filter(
                    CTE.placa.isnot(None)
                ).order_by(CTE.placa).all()
            else:
                return []
            
            return [veiculo[0].strip().upper() for veiculo in veiculos if veiculo[0]]
            
        except Exception as e:
            logging.error(f"Erro ao obter lista de veículos: {str(e)}")
            return []
    
    @staticmethod
    def _analise_vazia() -> Dict:
        """Retorna estrutura vazia"""
        return {
            'success': False,
            'total_veiculos': 0,
            'total_viagens': 0,
            'faturamento_total': 0.0,
            'ranking_veiculos': [],
            'metricas_performance': {},
            'insights': [],
            'error': 'Nenhum dado encontrado'
        }
