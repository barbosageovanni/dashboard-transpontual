#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Análise Financeira - Dashboard Baker Flask
app/services/analise_financeira_service.py
ATUALIZADO: Adicionada métrica de Receita por Inclusão Fatura
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
from sqlalchemy import func, and_, or_
from scipy import stats
import logging

class AnaliseFinanceiraService:
    """Serviço para análises financeiras avançadas"""
    
    @staticmethod
    def gerar_analise_completa(filtro_dias: int = 180, filtro_cliente: str = None) -> Dict:
        """
        Gera análise financeira completa com todas as métricas
        ADICIONADO: Receita por Inclusão Fatura
        """
        try:
            # Calcular data limite
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Buscar dados filtrados
            query = CTE.query.filter(CTE.data_emissao >= data_limite)
            
            if filtro_cliente:
                query = query.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
            
            ctes = query.all()
            
            if not ctes:
                return AnaliseFinanceiraService._analise_vazia()
            
            # Converter para DataFrame
            df = AnaliseFinanceiraService._ctes_para_dataframe(ctes)
            
            # Calcular todas as métricas
            return {
                'receita_mensal': AnaliseFinanceiraService._calcular_receita_mensal(df),
                # 🆕 NOVA MÉTRICA ADICIONADA
                'receita_por_inclusao_fatura': AnaliseFinanceiraService._calcular_receita_por_inclusao_fatura(df, filtro_dias),
                'ticket_medio': AnaliseFinanceiraService._calcular_ticket_medio(df),
                'tempo_medio_cobranca': AnaliseFinanceiraService._calcular_tempo_cobranca(df),
                'tendencia_linear': AnaliseFinanceiraService._calcular_tendencia_linear(df),
                'concentracao_clientes': AnaliseFinanceiraService._calcular_concentracao_clientes(df),
                'stress_test_receita': AnaliseFinanceiraService._calcular_stress_test(df),
                'graficos': AnaliseFinanceiraService._gerar_dados_graficos(df),
                'resumo_filtro': {
                    'periodo_dias': filtro_dias,
                    'cliente_filtro': filtro_cliente,
                    'total_ctes': len(df),
                    'data_inicio': data_limite.strftime('%d/%m/%Y'),
                    'data_fim': datetime.now().date().strftime('%d/%m/%Y')
                }
            }
            
        except Exception as e:
            logging.error(f"Erro na análise financeira: {str(e)}")
            return AnaliseFinanceiraService._analise_vazia()
    
    @staticmethod
    def _ctes_para_dataframe(ctes: List[CTE]) -> pd.DataFrame:
        """Converte lista de CTEs para DataFrame - ATUALIZADO"""
        dados = []
        for cte in ctes:
            dados.append({
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome,
                'valor_total': float(cte.valor_total or 0),
                'data_emissao': cte.data_emissao,
                'data_baixa': cte.data_baixa,
                'primeiro_envio': cte.primeiro_envio,
                # 🆕 ADICIONADO: data_inclusao_fatura
                'data_inclusao_fatura': cte.data_inclusao_fatura,
                'mes_emissao': cte.data_emissao.strftime('%Y-%m') if cte.data_emissao else None,
                # 🆕 ADICIONADO: mês de inclusão de fatura
                'mes_inclusao_fatura': cte.data_inclusao_fatura.strftime('%Y-%m') if cte.data_inclusao_fatura else None,
                'has_baixa': cte.data_baixa is not None
            })
        
        df = pd.DataFrame(dados)
        
        # Converter datas - ATUALIZADO
        for col in ['data_emissao', 'data_baixa', 'primeiro_envio', 'data_inclusao_fatura']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    # 🆕 NOVA FUNÇÃO: Receita por Inclusão Fatura
    @staticmethod
    def _calcular_receita_por_inclusao_fatura(df: pd.DataFrame, filtro_dias: int) -> Dict:
        """
        Calcula métricas de receita baseadas em data_inclusao_fatura
        Nova métrica solicitada pelo usuário
        """
        try:
            # Filtrar apenas CTEs com data_inclusao_fatura
            df_inclusao = df[df['data_inclusao_fatura'].notna()].copy()
            
            if df_inclusao.empty:
                return {
                    'receita_total_periodo': 0.0,
                    'receita_mes_corrente': 0.0,
                    'receita_mes_anterior': 0.0,
                    'variacao_percentual': 0.0,
                    'total_ctes_com_inclusao': 0,
                    'percentual_cobertura': 0.0,
                    'ticket_medio_inclusao': 0.0,
                    'status': 'Dados insuficientes'
                }
            
            # Filtrar por período baseado em data_inclusao_fatura
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            df_periodo = df_inclusao[df_inclusao['data_inclusao_fatura'].dt.date >= data_limite]
            
            # Calcular métricas básicas
            receita_total_periodo = df_periodo['valor_total'].sum()
            total_ctes_com_inclusao = len(df_periodo)
            total_ctes_geral = len(df)
            percentual_cobertura = (total_ctes_com_inclusao / total_ctes_geral * 100) if total_ctes_geral > 0 else 0.0
            ticket_medio_inclusao = df_periodo['valor_total'].mean() if not df_periodo.empty else 0.0
            
            # Análise mensal por inclusão de fatura
            if 'mes_inclusao_fatura' in df_periodo.columns and not df_periodo.empty:
                receita_mensal_inclusao = df_periodo.groupby('mes_inclusao_fatura')['valor_total'].sum().sort_index()
                
                if len(receita_mensal_inclusao) >= 2:
                    receita_mes_corrente = float(receita_mensal_inclusao.iloc[-1])
                    receita_mes_anterior = float(receita_mensal_inclusao.iloc[-2])
                elif len(receita_mensal_inclusao) == 1:
                    receita_mes_corrente = float(receita_mensal_inclusao.iloc[0])
                    receita_mes_anterior = 0.0
                else:
                    receita_mes_corrente = 0.0
                    receita_mes_anterior = 0.0
                
                # Calcular variação
                variacao_percentual = ((receita_mes_corrente - receita_mes_anterior) / receita_mes_anterior * 100) if receita_mes_anterior > 0 else 0.0
            else:
                receita_mes_corrente = 0.0
                receita_mes_anterior = 0.0
                variacao_percentual = 0.0
            
            # Determinar status
            if percentual_cobertura >= 80:
                status = 'Excelente cobertura'
            elif percentual_cobertura >= 60:
                status = 'Boa cobertura'
            elif percentual_cobertura >= 40:
                status = 'Cobertura moderada'
            else:
                status = 'Baixa cobertura'
            
            return {
                'receita_total_periodo': round(float(receita_total_periodo), 2),
                'receita_mes_corrente': round(float(receita_mes_corrente), 2),
                'receita_mes_anterior': round(float(receita_mes_anterior), 2),
                'variacao_percentual': round(float(variacao_percentual), 2),
                'total_ctes_com_inclusao': int(total_ctes_com_inclusao),
                'percentual_cobertura': round(float(percentual_cobertura), 2),
                'ticket_medio_inclusao': round(float(ticket_medio_inclusao), 2),
                'status': status
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de receita por inclusão fatura: {str(e)}")
            return {
                'receita_total_periodo': 0.0,
                'receita_mes_corrente': 0.0,
                'receita_mes_anterior': 0.0,
                'variacao_percentual': 0.0,
                'total_ctes_com_inclusao': 0,
                'percentual_cobertura': 0.0,
                'ticket_medio_inclusao': 0.0,
                'status': 'Erro no cálculo'
            }
    
    
    @staticmethod
    def _calcular_receita_mensal(df: pd.DataFrame) -> Dict:
        """Calcula métricas de receita mensal"""
        try:
            if df.empty or 'mes_emissao' not in df.columns:
                return {
                    'receita_mes_corrente': 0.0,
                    'receita_mes_anterior': 0.0,
                    'diferenca_absoluta': 0.0,
                    'variacao_percentual': 0.0,
                    'mes_corrente_nome': datetime.now().strftime('%B %Y'),
                    'mes_anterior_nome': (datetime.now() - timedelta(days=30)).strftime('%B %Y')
                }
            
            # Agrupar por mês
            receita_mensal = df.groupby('mes_emissao')['valor_total'].sum().sort_index()
            
            # Pegar últimos 2 meses
            meses = receita_mensal.index.tolist()
            
            if len(meses) >= 2:
                mes_corrente = meses[-1]
                mes_anterior = meses[-2]
                receita_mes_corrente = float(receita_mensal[mes_corrente])
                receita_mes_anterior = float(receita_mensal[mes_anterior])
            elif len(meses) == 1:
                mes_corrente = meses[0]
                mes_anterior = None
                receita_mes_corrente = float(receita_mensal[mes_corrente])
                receita_mes_anterior = 0.0
            else:
                receita_mes_corrente = 0.0
                receita_mes_anterior = 0.0
                mes_corrente = datetime.now().strftime('%Y-%m')
                mes_anterior = None
            
            # Calcular variação
            diferenca_absoluta = receita_mes_corrente - receita_mes_anterior
            variacao_percentual = ((diferenca_absoluta / receita_mes_anterior) * 100) if receita_mes_anterior > 0 else 0.0
            
            # Formatar nomes dos meses
            try:
                mes_corrente_nome = pd.to_datetime(mes_corrente).strftime('%B %Y')
                mes_anterior_nome = pd.to_datetime(mes_anterior).strftime('%B %Y') if mes_anterior else 'N/A'
            except:
                mes_corrente_nome = mes_corrente if mes_corrente else 'N/A'
                mes_anterior_nome = mes_anterior if mes_anterior else 'N/A'
            
            return {
                'receita_mes_corrente': receita_mes_corrente,
                'receita_mes_anterior': receita_mes_anterior,
                'diferenca_absoluta': diferenca_absoluta,
                'variacao_percentual': round(variacao_percentual, 2),
                'mes_corrente_nome': mes_corrente_nome,
                'mes_anterior_nome': mes_anterior_nome
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de receita mensal: {str(e)}")
            return {
                'receita_mes_corrente': 0.0,
                'receita_mes_anterior': 0.0,
                'diferenca_absoluta': 0.0,
                'variacao_percentual': 0.0,
                'mes_corrente_nome': 'N/A',
                'mes_anterior_nome': 'N/A'
            }

    @staticmethod
    def _analise_vazia() -> Dict:
        """Retorna estrutura vazia para análise - ATUALIZADA"""
        return {
            'receita_mensal': {
                'receita_mes_corrente': 0.0,
                'receita_mes_anterior': 0.0,
                'diferenca_absoluta': 0.0,
                'variacao_percentual': 0.0,
                'mes_corrente_nome': 'N/A',
                'mes_anterior_nome': 'N/A'
            },
            # 🆕 ADICIONADO: estrutura vazia para nova métrica
            'receita_por_inclusao_fatura': {
                'receita_total_periodo': 0.0,
                'receita_mes_corrente': 0.0,
                'receita_mes_anterior': 0.0,
                'variacao_percentual': 0.0,
                'total_ctes_com_inclusao': 0,
                'percentual_cobertura': 0.0,
                'ticket_medio_inclusao': 0.0,
                'status': 'Sem dados'
            },
            'ticket_medio': {'valor': 0.0, 'mediana': 0.0, 'desvio_padrao': 0.0},
            'tempo_medio_cobranca': {'dias_medio': 0.0, 'mediana': 0.0, 'total_analisados': 0},
            'tendencia_linear': {'inclinacao': 0.0, 'r_squared': 0.0, 'previsao_proximo_mes': 0.0},
            'concentracao_clientes': {'percentual_top5': 0.0, 'top_clientes': []},
            'stress_test_receita': {'cenarios': []},
            'graficos': AnaliseFinanceiraService._graficos_vazios(),
            'resumo_filtro': {
                'periodo_dias': 0,
                'cliente_filtro': None,
                'total_ctes': 0,
                'data_inicio': 'N/A',
                'data_fim': 'N/A'
            }
        }

    # [TODAS AS OUTRAS FUNÇÕES MANTIDAS IGUAIS...]
    
    @staticmethod
    def _calcular_ticket_medio(df: pd.DataFrame) -> Dict:
        """Calcula ticket médio por fatura"""
        try:
            if df.empty:
                return {'valor': 0.0, 'mediana': 0.0, 'desvio_padrao': 0.0}
            
            ticket_medio = df['valor_total'].mean()
            mediana = df['valor_total'].median()
            desvio_padrao = df['valor_total'].std()
            
            return {
                'valor': round(float(ticket_medio), 2),
                'mediana': round(float(mediana), 2),
                'desvio_padrao': round(float(desvio_padrao), 2)
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de ticket médio: {str(e)}")
            return {'valor': 0.0, 'mediana': 0.0, 'desvio_padrao': 0.0}
    
    @staticmethod
    def _calcular_tempo_cobranca(df: pd.DataFrame) -> Dict:
        """Calcula tempo médio entre primeiro_envio e data_baixa"""
        try:
            if df.empty:
                return {'dias_medio': 0.0, 'mediana': 0.0, 'total_analisados': 0}
            
            # Filtrar apenas CTEs com ambas as datas
            df_cobranca = df[
                df['primeiro_envio'].notna() & 
                df['data_baixa'].notna()
            ].copy()
            
            if df_cobranca.empty:
                return {'dias_medio': 0.0, 'mediana': 0.0, 'total_analisados': 0}
            
            # Calcular diferença em dias
            df_cobranca['dias_cobranca'] = (
                df_cobranca['data_baixa'] - df_cobranca['primeiro_envio']
            ).dt.days
            
            # Filtrar valores válidos (não negativos)
            dias_validos = df_cobranca[df_cobranca['dias_cobranca'] >= 0]['dias_cobranca']
            
            if dias_validos.empty:
                return {'dias_medio': 0.0, 'mediana': 0.0, 'total_analisados': 0}
            
            return {
                'dias_medio': round(float(dias_validos.mean()), 1),
                'mediana': round(float(dias_validos.median()), 1),
                'total_analisados': len(dias_validos),
                'min_dias': int(dias_validos.min()),
                'max_dias': int(dias_validos.max())
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de tempo de cobrança: {str(e)}")
            return {'dias_medio': 0.0, 'mediana': 0.0, 'total_analisados': 0}
    
    @staticmethod
    def _calcular_tendencia_linear(df: pd.DataFrame) -> Dict:
        """Calcula tendência linear da receita mensal (últimos 6 meses)"""
        try:
            if df.empty or 'mes_emissao' not in df.columns:
                return {'inclinacao': 0.0, 'r_squared': 0.0, 'previsao_proximo_mes': 0.0}
            
            # Agrupar por mês e pegar últimos 6 meses
            receita_mensal = df.groupby('mes_emissao')['valor_total'].sum().sort_index()
            receita_mensal = receita_mensal.tail(6)  # Últimos 6 meses
            
            if len(receita_mensal) < 3:  # Mínimo 3 pontos para regressão
                return {'inclinacao': 0.0, 'r_squared': 0.0, 'previsao_proximo_mes': 0.0}
            
            # Preparar dados para regressão
            x = np.arange(len(receita_mensal))
            y = receita_mensal.values
            
            # Regressão linear
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Previsão para próximo mês
            proximo_x = len(receita_mensal)
            previsao_proximo_mes = slope * proximo_x + intercept
            
            return {
                'inclinacao': round(float(slope), 2),
                'r_squared': round(float(r_value ** 2), 3),
                'previsao_proximo_mes': round(float(previsao_proximo_mes), 2),
                'p_value': round(float(p_value), 4),
                'meses_analisados': len(receita_mensal)
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de tendência linear: {str(e)}")
            return {'inclinacao': 0.0, 'r_squared': 0.0, 'previsao_proximo_mes': 0.0}
    
    @staticmethod
    def _calcular_concentracao_clientes(df: pd.DataFrame) -> Dict:
        """Calcula concentração dos Top 5 clientes"""
        try:
            if df.empty:
                return {'percentual_top5': 0.0, 'top_clientes': []}
            
            # Agrupar por cliente
            receita_cliente = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False)
            
            # Top 5 clientes
            top5_clientes = receita_cliente.head(5)
            receita_total = df['valor_total'].sum()
            
            # Calcular percentual
            receita_top5 = top5_clientes.sum()
            percentual_top5 = (receita_top5 / receita_total * 100) if receita_total > 0 else 0.0
            
            # Preparar lista dos top clientes
            top_clientes = []
            for i, (cliente, valor) in enumerate(top5_clientes.items(), 1):
                percentual_individual = (valor / receita_total * 100) if receita_total > 0 else 0.0
                top_clientes.append({
                    'posicao': i,
                    'nome': cliente,
                    'receita': float(valor),
                    'percentual': round(percentual_individual, 2)
                })
            
            return {
                'percentual_top5': round(percentual_top5, 2),
                'receita_top5': float(receita_top5),
                'receita_total': float(receita_total),
                'top_clientes': top_clientes
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de concentração de clientes: {str(e)}")
            return {'percentual_top5': 0.0, 'top_clientes': []}
    
    @staticmethod
    def _calcular_stress_test(df: pd.DataFrame) -> Dict:
        """Simula impacto de inadimplência dos maiores clientes"""
        try:
            if df.empty:
                return {'cenarios': []}
            
            # Agrupar por cliente
            receita_cliente = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False)
            receita_total = df['valor_total'].sum()
            
            # Cenários de stress test
            cenarios = [
                {'nome': 'Top 1 Cliente', 'clientes': 1},
                {'nome': 'Top 3 Clientes', 'clientes': 3},
                {'nome': 'Top 5 Clientes', 'clientes': 5},
            ]
            
            resultados = []
            for cenario in cenarios:
                n_clientes = cenario['clientes']
                if len(receita_cliente) >= n_clientes:
                    receita_impactada = receita_cliente.head(n_clientes).sum()
                    percentual_impacto = (receita_impactada / receita_total * 100) if receita_total > 0 else 0.0
                    receita_restante = receita_total - receita_impactada
                    
                    resultados.append({
                        'cenario': cenario['nome'],
                        'receita_perdida': float(receita_impactada),
                        'percentual_impacto': round(percentual_impacto, 2),
                        'receita_restante': float(receita_restante),
                        'percentual_restante': round(100 - percentual_impacto, 2)
                    })
            
            return {'cenarios': resultados}
            
        except Exception as e:
            logging.error(f"Erro no stress test: {str(e)}")
            return {'cenarios': []}
    
    @staticmethod
    def _gerar_dados_graficos(df: pd.DataFrame) -> Dict:
        """Gera dados para todos os gráficos"""
        try:
            if df.empty:
                return AnaliseFinanceiraService._graficos_vazios()
            
            return {
                'receita_mensal': AnaliseFinanceiraService._grafico_receita_mensal(df),
                'distribuicao_valores': AnaliseFinanceiraService._grafico_distribuicao_valores(df),
                'tempo_cobranca': AnaliseFinanceiraService._grafico_tempo_cobranca(df),
                'concentracao_clientes': AnaliseFinanceiraService._grafico_concentracao_clientes(df),
                'tendencia_linear': AnaliseFinanceiraService._grafico_tendencia_linear(df)
            }
            
        except Exception as e:
            logging.error(f"Erro na geração de gráficos: {str(e)}")
            return AnaliseFinanceiraService._graficos_vazios()
    
    @staticmethod
    def _grafico_receita_mensal(df: pd.DataFrame) -> Dict:
        """Dados para gráfico de receita mensal"""
        receita_mensal = df.groupby('mes_emissao')['valor_total'].sum().sort_index()
        
        return {
            'labels': [pd.to_datetime(mes).strftime('%b/%Y') for mes in receita_mensal.index],
            'valores': [float(valor) for valor in receita_mensal.values],
            'quantidade_ctes': [int(qtd) for qtd in df.groupby('mes_emissao').size().values]
        }
    
    @staticmethod
    def _grafico_distribuicao_valores(df: pd.DataFrame) -> Dict:
        """Dados para histograma de distribuição de valores"""
        valores = df['valor_total'].values
        
        # Criar bins para histograma
        bins = np.histogram_bin_edges(valores, bins=10)
        hist, _ = np.histogram(valores, bins=bins)
        
        return {
            'bins': [f'R$ {int(bins[i])}-{int(bins[i+1])}' for i in range(len(bins)-1)],
            'frequencias': [int(freq) for freq in hist]
        }
    
    @staticmethod
    def _grafico_tempo_cobranca(df: pd.DataFrame) -> Dict:
        """Dados para gráfico de tempo de cobrança"""
        df_cobranca = df[
            df['primeiro_envio'].notna() & 
            df['data_baixa'].notna()
        ].copy()
        
        if df_cobranca.empty:
            return {'labels': [], 'valores': []}
        
        df_cobranca['dias_cobranca'] = (
            df_cobranca['data_baixa'] - df_cobranca['primeiro_envio']
        ).dt.days
        
        # Agrupar por faixas de dias
        faixas = [
            (0, 30, '0-30 dias'),
            (31, 60, '31-60 dias'),
            (61, 90, '61-90 dias'),
            (91, float('inf'), '90+ dias')
        ]
        
        labels = []
        valores = []
        
        for min_dias, max_dias, label in faixas:
            if max_dias == float('inf'):
                count = len(df_cobranca[df_cobranca['dias_cobranca'] >= min_dias])
            else:
                count = len(df_cobranca[
                    (df_cobranca['dias_cobranca'] >= min_dias) & 
                    (df_cobranca['dias_cobranca'] <= max_dias)
                ])
            labels.append(label)
            valores.append(count)
        
        return {'labels': labels, 'valores': valores}
    
    @staticmethod
    def _grafico_concentracao_clientes(df: pd.DataFrame) -> Dict:
        """Dados para gráfico de concentração de clientes"""
        receita_cliente = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False)
        top5 = receita_cliente.head(5)
        outros = receita_cliente.iloc[5:].sum() if len(receita_cliente) > 5 else 0
        
        labels = list(top5.index) + (['Outros'] if outros > 0 else [])
        valores = list(top5.values) + ([float(outros)] if outros > 0 else [])
        
        return {
            'labels': labels,
            'valores': [float(v) for v in valores]
        }
    
    @staticmethod
    def _grafico_tendencia_linear(df: pd.DataFrame) -> Dict:
        """Dados para gráfico de tendência linear"""
        receita_mensal = df.groupby('mes_emissao')['valor_total'].sum().sort_index().tail(6)
        
        if len(receita_mensal) < 3:
            return {'labels': [], 'valores_reais': [], 'valores_tendencia': []}
        
        # Calcular linha de tendência
        x = np.arange(len(receita_mensal))
        y = receita_mensal.values
        slope, intercept, _, _, _ = stats.linregress(x, y)
        
        tendencia = slope * x + intercept
        
        return {
            'labels': [pd.to_datetime(mes).strftime('%b/%Y') for mes in receita_mensal.index],
            'valores_reais': [float(valor) for valor in receita_mensal.values],
            'valores_tendencia': [float(valor) for valor in tendencia]
        }
    
    @staticmethod
    def _graficos_vazios() -> Dict:
        """Retorna estrutura vazia para gráficos"""
        return {
            'receita_mensal': {'labels': [], 'valores': [], 'quantidade_ctes': []},
            'distribuicao_valores': {'bins': [], 'frequencias': []},
            'tempo_cobranca': {'labels': [], 'valores': []},
            'concentracao_clientes': {'labels': [], 'valores': []},
            'tendencia_linear': {'labels': [], 'valores_reais': [], 'valores_tendencia': []}
        }
    
    @staticmethod
    def obter_lista_clientes() -> List[str]:
        """Obtém lista de clientes para filtro"""
        try:
            clientes = db.session.query(CTE.destinatario_nome).distinct().filter(
                CTE.destinatario_nome.isnot(None)
            ).order_by(CTE.destinatario_nome).all()
            
            return [cliente[0] for cliente in clientes if cliente[0]]
            
        except Exception as e:
            logging.error(f"Erro ao obter lista de clientes: {str(e)}")
            return []
    
    # 🆕 NOVA FUNÇÃO: Faturamento mensal por data_inclusao_fatura com filtros específicos
    @staticmethod
    def obter_faturamento_por_inclusao(filtro_dias: int = 30) -> Dict:
        """
        Obtém faturamento baseado em data_inclusao_fatura com filtros específicos
        Filtros disponíveis: 30, 60, 90 dias
        """
        try:
            # Validar filtro
            if filtro_dias not in [30, 60, 90]:
                filtro_dias = 30
            
            # Calcular data limite
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Buscar CTEs com data_inclusao_fatura no período
            ctes = CTE.query.filter(
                CTE.data_inclusao_fatura >= data_limite,
                CTE.data_inclusao_fatura.isnot(None)
            ).all()
            
            if not ctes:
                return {
                    'faturamento_total': 0.0,
                    'faturamento_mensal': {},
                    'quantidade_ctes': 0,
                    'ticket_medio': 0.0,
                    'periodo_dias': filtro_dias,
                    'data_inicio': data_limite.strftime('%d/%m/%Y'),
                    'data_fim': datetime.now().date().strftime('%d/%m/%Y'),
                    'status': 'Sem dados no período'
                }
            
            # Converter para DataFrame
            df = pd.DataFrame([{
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome,
                'valor_total': float(cte.valor_total or 0),
                'data_inclusao_fatura': cte.data_inclusao_fatura,
                'mes_inclusao': cte.data_inclusao_fatura.strftime('%Y-%m') if cte.data_inclusao_fatura else None
            } for cte in ctes])
            
            # Calcular métricas
            faturamento_total = df['valor_total'].sum()
            quantidade_ctes = len(df)
            ticket_medio = df['valor_total'].mean()
            
            # Faturamento mensal
            faturamento_mensal = df.groupby('mes_inclusao')['valor_total'].sum().to_dict()
            faturamento_mensal_formatado = {}
            for mes, valor in faturamento_mensal.items():
                mes_nome = pd.to_datetime(mes).strftime('%B %Y')
                faturamento_mensal_formatado[mes_nome] = float(valor)
            
            # Determinar status
            if quantidade_ctes >= 50:
                status = 'Volume alto'
            elif quantidade_ctes >= 20:
                status = 'Volume moderado'
            else:
                status = 'Volume baixo'
            
            return {
                'faturamento_total': round(float(faturamento_total), 2),
                'faturamento_mensal': faturamento_mensal_formatado,
                'quantidade_ctes': int(quantidade_ctes),
                'ticket_medio': round(float(ticket_medio), 2),
                'periodo_dias': filtro_dias,
                'data_inicio': data_limite.strftime('%d/%m/%Y'),
                'data_fim': datetime.now().date().strftime('%d/%m/%Y'),
                'status': status,
                'graficos': {
                    'faturamento_mensal': {
                        'labels': list(faturamento_mensal_formatado.keys()),
                        'valores': list(faturamento_mensal_formatado.values())
                    }
                }
            }
            
        except Exception as e:
            logging.error(f"Erro no faturamento por inclusão: {str(e)}")
            return {
                'faturamento_total': 0.0,
                'faturamento_mensal': {},
                'quantidade_ctes': 0,
                'ticket_medio': 0.0,
                'periodo_dias': filtro_dias,
                'data_inicio': 'N/A',
                'data_fim': 'N/A',
                'status': 'Erro no cálculo'
            }
    
    @staticmethod
    def obter_receita_com_faturas(filtro_dias: int = 30, incluir_sem_baixa: bool = True) -> Dict:
        """
        Análise de receita considerando faturas e baixas
        """
        try:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Query base
            query = CTE.query.filter(CTE.data_emissao >= data_limite)
            
            # Aplicar filtro de baixa se necessário
            if not incluir_sem_baixa:
                query = query.filter(CTE.data_baixa.isnot(None))
            
            ctes = query.all()
            
            if not ctes:
                return {
                    'receita_total': 0.0,
                    'receita_com_baixa': 0.0,
                    'receita_sem_baixa': 0.0,
                    'percentual_baixado': 0.0,
                    'quantidade_total': 0,
                    'quantidade_com_baixa': 0,
                    'quantidade_sem_baixa': 0,
                    'ticket_medio_geral': 0.0,
                    'ticket_medio_baixados': 0.0,
                    'periodo_dias': filtro_dias,
                    'status': 'Sem dados'
                }
            
            # Converter para DataFrame
            df = AnaliseFinanceiraService._ctes_para_dataframe(ctes)
            
            # Separar por status de baixa
            df_com_baixa = df[df['data_baixa'].notna()]
            df_sem_baixa = df[df['data_baixa'].isna()]
            
            # Calcular métricas
            receita_total = df['valor_total'].sum()
            receita_com_baixa = df_com_baixa['valor_total'].sum()
            receita_sem_baixa = df_sem_baixa['valor_total'].sum()
            
            percentual_baixado = (receita_com_baixa / receita_total * 100) if receita_total > 0 else 0
            
            quantidade_total = len(df)
            quantidade_com_baixa = len(df_com_baixa)
            quantidade_sem_baixa = len(df_sem_baixa)
            
            ticket_medio_geral = receita_total / quantidade_total if quantidade_total > 0 else 0
            ticket_medio_baixados = receita_com_baixa / quantidade_com_baixa if quantidade_com_baixa > 0 else 0
            
            return {
                'receita_total': round(float(receita_total), 2),
                'receita_com_baixa': round(float(receita_com_baixa), 2),
                'receita_sem_baixa': round(float(receita_sem_baixa), 2),
                'percentual_baixado': round(float(percentual_baixado), 2),
                'quantidade_total': int(quantidade_total),
                'quantidade_com_baixa': int(quantidade_com_baixa),
                'quantidade_sem_baixa': int(quantidade_sem_baixa),
                'ticket_medio_geral': round(float(ticket_medio_geral), 2),
                'ticket_medio_baixados': round(float(ticket_medio_baixados), 2),
                'periodo_dias': filtro_dias,
                'data_inicio': data_limite.strftime('%d/%m/%Y'),
                'data_fim': datetime.now().date().strftime('%d/%m/%Y'),
                'status': 'Calculado com sucesso',
                'graficos': {
                    'distribuicao_baixas': {
                        'labels': ['Com Baixa', 'Sem Baixa'],
                        'valores': [float(receita_com_baixa), float(receita_sem_baixa)]
                    },
                    'quantidade_status': {
                        'labels': ['Com Baixa', 'Sem Baixa'],
                        'valores': [quantidade_com_baixa, quantidade_sem_baixa]
                    }
                }
            }
            
        except Exception as e:
            logging.error(f"Erro na receita com faturas: {str(e)}")
            return {
                'receita_total': 0.0,
                'receita_com_baixa': 0.0,
                'receita_sem_baixa': 0.0,
                'percentual_baixado': 0.0,
                'quantidade_total': 0,
                'quantidade_com_baixa': 0,
                'quantidade_sem_baixa': 0,
                'ticket_medio_geral': 0.0,
                'ticket_medio_baixados': 0.0,
                'periodo_dias': filtro_dias,
                'status': 'Erro no cálculo'
            }