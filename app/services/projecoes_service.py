#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Projeções Financeiras - Dashboard Baker Flask
app/services/projecoes_service.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
import logging
from dateutil.relativedelta import relativedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class ProjecoesService:
    """Serviço para projeções financeiras e análises temporais avançadas"""
    
    @staticmethod
    def projecao_recebimentos_3_meses() -> Dict:
        """
        Gera projeção de recebimentos para os próximos 3 meses
        baseada em tendências históricas e sazonalidade
        """
        try:
            # Buscar dados históricos (último ano)
            data_limite = datetime.now().date() - timedelta(days=365)
            
            ctes = CTE.query.filter(
                CTE.data_emissao >= data_limite,
                CTE.valor_total.isnot(None)
            ).all()
            
            if not ctes:
                return ProjecoesService._projecao_vazia()
            
            # Preparar DataFrame
            dados = []
            for cte in ctes:
                dados.append({
                    'data_emissao': cte.data_emissao,
                    'valor_total': float(cte.valor_total or 0),
                    'mes_ano': cte.data_emissao.strftime('%Y-%m') if cte.data_emissao else None,
                    'has_baixa': cte.has_baixa,
                    'data_baixa': cte.data_baixa
                })
            
            df = pd.DataFrame(dados)
            df['data_emissao'] = pd.to_datetime(df['data_emissao'])
            
            # Análise de receita mensal histórica
            receita_mensal = df.groupby('mes_ano')['valor_total'].sum().sort_index()
            
            # Calcular tendência linear
            if len(receita_mensal) >= 3:
                x = np.arange(len(receita_mensal))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, receita_mensal.values)
                
                # Projetar próximos 3 meses
                projecoes = []
                data_atual = datetime.now().date()
                
                for i in range(1, 4):  # Próximos 3 meses
                    data_projecao = data_atual + relativedelta(months=i)
                    mes_projecao = data_projecao.strftime('%Y-%m')
                    
                    # Valor base da tendência
                    valor_tendencia = slope * (len(receita_mensal) + i - 1) + intercept
                    
                    # Aplicar sazonalidade (média dos últimos 2 anos do mesmo mês)
                    fator_sazonalidade = ProjecoesService._calcular_sazonalidade(
                        df, data_projecao.month
                    )
                    
                    # Valor final projetado
                    valor_projetado = max(0, valor_tendencia * fator_sazonalidade)
                    
                    # Calcular confiança baseada no R²
                    confianca = max(0.3, min(0.95, r_value ** 2))
                    
                    # Margem de erro
                    margem_erro = valor_projetado * (1 - confianca) * 0.5
                    
                    projecoes.append({
                        'mes': mes_projecao,
                        'mes_nome': data_projecao.strftime('%B/%Y'),
                        'valor_projetado': round(valor_projetado, 2),
                        'valor_minimo': round(valor_projetado - margem_erro, 2),
                        'valor_maximo': round(valor_projetado + margem_erro, 2),
                        'confianca_percentual': round(confianca * 100, 1),
                        'tendencia_percentual': round(slope / receita_mensal.mean() * 100, 2)
                    })
                
                # Análise de histórico para comparação
                receita_ultimo_mes = receita_mensal.iloc[-1] if len(receita_mensal) > 0 else 0
                receita_3_meses_atras = receita_mensal.iloc[-3] if len(receita_mensal) >= 3 else 0
                
                return {
                    'success': True,
                    'projecoes_mensais': projecoes,
                    'total_projetado_3_meses': sum(p['valor_projetado'] for p in projecoes),
                    'media_mensal_historica': round(receita_mensal.mean(), 2),
                    'receita_ultimo_mes': round(receita_ultimo_mes, 2),
                    'tendencia_geral': 'Crescimento' if slope > 0 else 'Declínio' if slope < 0 else 'Estável',
                    'r_squared': round(r_value ** 2, 3),
                    'meses_analisados': len(receita_mensal),
                    'data_base_projecao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'metodologia': 'Regressão linear + Sazonalidade histórica'
                }
            else:
                return ProjecoesService._projecao_vazia()
                
        except Exception as e:
            logging.error(f"Erro na projeção de recebimentos: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def analise_comparativa_periodos(filtro_dias: int) -> Dict:
        """
        Análise comparativa entre períodos (7, 15, 30, 60, 90, 180 dias)
        vs mesmo período dos últimos 2 meses e ano anterior
        """
        try:
            data_atual = datetime.now().date()
            
            # Período atual
            data_inicio_atual = data_atual - timedelta(days=filtro_dias)
            
            # Período de 2 meses atrás
            data_inicio_2m = data_atual - relativedelta(months=2) - timedelta(days=filtro_dias)
            data_fim_2m = data_atual - relativedelta(months=2)
            
            # Período de 1 ano atrás
            data_inicio_1a = data_atual - relativedelta(years=1) - timedelta(days=filtro_dias)
            data_fim_1a = data_atual - relativedelta(years=1)
            
            # Buscar dados para cada período
            periodo_atual = ProjecoesService._buscar_dados_periodo(data_inicio_atual, data_atual)
            periodo_2m = ProjecoesService._buscar_dados_periodo(data_inicio_2m, data_fim_2m)
            periodo_1a = ProjecoesService._buscar_dados_periodo(data_inicio_1a, data_fim_1a)
            
            # Calcular métricas comparativas
            comparacao = {
                'periodo_atual': {
                    'data_inicio': data_inicio_atual.strftime('%d/%m/%Y'),
                    'data_fim': data_atual.strftime('%d/%m/%Y'),
                    'receita_total': periodo_atual['receita_total'],
                    'quantidade_ctes': periodo_atual['quantidade_ctes'],
                    'ticket_medio': periodo_atual['ticket_medio'],
                    'clientes_unicos': periodo_atual['clientes_unicos']
                },
                'periodo_2_meses_atras': {
                    'data_inicio': data_inicio_2m.strftime('%d/%m/%Y'),
                    'data_fim': data_fim_2m.strftime('%d/%m/%Y'),
                    'receita_total': periodo_2m['receita_total'],
                    'quantidade_ctes': periodo_2m['quantidade_ctes'],
                    'ticket_medio': periodo_2m['ticket_medio'],
                    'clientes_unicos': periodo_2m['clientes_unicos']
                },
                'periodo_1_ano_atras': {
                    'data_inicio': data_inicio_1a.strftime('%d/%m/%Y'),
                    'data_fim': data_fim_1a.strftime('%d/%m/%Y'),
                    'receita_total': periodo_1a['receita_total'],
                    'quantidade_ctes': periodo_1a['quantidade_ctes'],
                    'ticket_medio': periodo_1a['ticket_medio'],
                    'clientes_unicos': periodo_1a['clientes_unicos']
                }
            }
            
            # Calcular variações percentuais
            variacao_vs_2m = ProjecoesService._calcular_variacao(
                periodo_atual, periodo_2m
            )
            variacao_vs_1a = ProjecoesService._calcular_variacao(
                periodo_atual, periodo_1a
            )
            
            comparacao['variacao_vs_2_meses'] = variacao_vs_2m
            comparacao['variacao_vs_1_ano'] = variacao_vs_1a
            
            # Análise de performance
            performance_score = ProjecoesService._calcular_score_performance(
                variacao_vs_2m, variacao_vs_1a
            )
            
            comparacao['analise_performance'] = performance_score
            comparacao['filtro_dias'] = filtro_dias
            comparacao['data_analise'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            return {'success': True, 'comparacao': comparacao}
            
        except Exception as e:
            logging.error(f"Erro na análise comparativa: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _calcular_sazonalidade(df: pd.DataFrame, mes_target: int) -> float:
        """Calcula fator de sazonalidade baseado no histórico do mês"""
        try:
            df['mes'] = df['data_emissao'].dt.month
            
            # Receita média geral
            receita_media_geral = df['valor_total'].mean()
            
            # Receita média do mês específico
            receita_mes_especifico = df[df['mes'] == mes_target]['valor_total'].mean()
            
            if receita_media_geral > 0 and not pd.isna(receita_mes_especifico):
                return receita_mes_especifico / receita_media_geral
            else:
                return 1.0  # Fator neutro
                
        except Exception:
            return 1.0
    
    @staticmethod
    def _buscar_dados_periodo(data_inicio: date, data_fim: date) -> Dict:
        """Busca dados financeiros para um período específico"""
        try:
            ctes = CTE.query.filter(
                CTE.data_emissao >= data_inicio,
                CTE.data_emissao <= data_fim,
                CTE.valor_total.isnot(None)
            ).all()
            
            if not ctes:
                return {
                    'receita_total': 0.0,
                    'quantidade_ctes': 0,
                    'ticket_medio': 0.0,
                    'clientes_unicos': 0
                }
            
            receita_total = sum(float(cte.valor_total or 0) for cte in ctes)
            quantidade_ctes = len(ctes)
            ticket_medio = receita_total / quantidade_ctes if quantidade_ctes > 0 else 0.0
            clientes_unicos = len(set(cte.destinatario_nome for cte in ctes if cte.destinatario_nome))
            
            return {
                'receita_total': round(receita_total, 2),
                'quantidade_ctes': quantidade_ctes,
                'ticket_medio': round(ticket_medio, 2),
                'clientes_unicos': clientes_unicos
            }
            
        except Exception as e:
            logging.error(f"Erro ao buscar dados do período: {str(e)}")
            return {
                'receita_total': 0.0,
                'quantidade_ctes': 0,
                'ticket_medio': 0.0,
                'clientes_unicos': 0
            }
    
    @staticmethod
    def _calcular_variacao(periodo_atual: Dict, periodo_comparacao: Dict) -> Dict:
        """Calcula variações percentuais entre períodos"""
        def calc_var(atual, anterior):
            if anterior == 0:
                return 100.0 if atual > 0 else 0.0
            return round(((atual - anterior) / anterior) * 100, 2)
        
        return {
            'receita_percentual': calc_var(
                periodo_atual['receita_total'], 
                periodo_comparacao['receita_total']
            ),
            'quantidade_percentual': calc_var(
                periodo_atual['quantidade_ctes'], 
                periodo_comparacao['quantidade_ctes']
            ),
            'ticket_medio_percentual': calc_var(
                periodo_atual['ticket_medio'], 
                periodo_comparacao['ticket_medio']
            ),
            'clientes_percentual': calc_var(
                periodo_atual['clientes_unicos'], 
                periodo_comparacao['clientes_unicos']
            )
        }
    
    @staticmethod
    def _calcular_score_performance(variacao_2m: Dict, variacao_1a: Dict) -> Dict:
        """Calcula score de performance baseado nas variações"""
        
        # Weights para diferentes métricas
        peso_receita = 0.4
        peso_quantidade = 0.3
        peso_ticket = 0.2
        peso_clientes = 0.1
        
        # Score vs 2 meses
        score_2m = (
            variacao_2m['receita_percentual'] * peso_receita +
            variacao_2m['quantidade_percentual'] * peso_quantidade +
            variacao_2m['ticket_medio_percentual'] * peso_ticket +
            variacao_2m['clientes_percentual'] * peso_clientes
        )
        
        # Score vs 1 ano
        score_1a = (
            variacao_1a['receita_percentual'] * peso_receita +
            variacao_1a['quantidade_percentual'] * peso_quantidade +
            variacao_1a['ticket_medio_percentual'] * peso_ticket +
            variacao_1a['clientes_percentual'] * peso_clientes
        )
        
        # Classificação
        def classificar_performance(score):
            if score >= 15:
                return "Excelente", "success"
            elif score >= 5:
                return "Bom", "info"
            elif score >= -5:
                return "Estável", "warning"
            else:
                return "Declínio", "danger"
        
        classificacao_2m, cor_2m = classificar_performance(score_2m)
        classificacao_1a, cor_1a = classificar_performance(score_1a)
        
        return {
            'score_vs_2_meses': round(score_2m, 2),
            'score_vs_1_ano': round(score_1a, 2),
            'classificacao_2m': classificacao_2m,
            'classificacao_1a': classificacao_1a,
            'cor_2m': cor_2m,
            'cor_1a': cor_1a,
            'tendencia_geral': 'Positiva' if (score_2m > 0 and score_1a > 0) else 
                              'Mista' if (score_2m > 0 or score_1a > 0) else 'Negativa'
        }
    
    @staticmethod
    def _projecao_vazia() -> Dict:
        """Retorna estrutura vazia para projeção"""
        return {
            'success': False,
            'projecoes_mensais': [],
            'total_projetado_3_meses': 0.0,
            'media_mensal_historica': 0.0,
            'receita_ultimo_mes': 0.0,
            'tendencia_geral': 'Sem dados',
            'r_squared': 0.0,
            'meses_analisados': 0,
            'error': 'Dados insuficientes para projeção'
        }