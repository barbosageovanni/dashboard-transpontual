#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Análise por Veículo - Dashboard Baker Flask
app/services/analise_veiculo_service.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
import logging
from sqlalchemy import func, desc

class AnaliseVeiculoService:
    """Serviço para análise detalhada de faturamento e performance por veículo"""
    
    @staticmethod
    def analise_completa_veiculos(filtro_dias: int = 180, filtro_veiculo: str = None) -> Dict:
        """
        Análise completa de todos os veículos incluindo:
        - Faturamento por veículo
        - Número de viagens
        - Ticket médio por viagem
        - Performance temporal
        - Comparações entre veículos
        """
        try:
            # Calcular data limite
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Query base
            query = CTE.query.filter(
                CTE.data_emissao >= data_limite,
                CTE.veiculo_placa.isnot(None),
                CTE.valor_total.isnot(None)
            )
            
            # Aplicar filtro de veículo específico se fornecido
            if filtro_veiculo:
                query = query.filter(CTE.veiculo_placa.ilike(f'%{filtro_veiculo}%'))
            
            ctes = query.all()
            
            if not ctes:
                return AnaliseVeiculoService._analise_vazia()
            
            # Preparar dados para análise
            dados = []
            for cte in ctes:
                dados.append({
                    'veiculo_placa': cte.veiculo_placa.strip().upper() if cte.veiculo_placa else 'SEM_PLACA',
                    'numero_cte': cte.numero_cte,
                    'valor_total': float(cte.valor_total or 0),
                    'data_emissao': cte.data_emissao,
                    'destinatario_nome': cte.destinatario_nome,
                    'origem_cidade': cte.origem_cidade,
                    'destino_cidade': cte.destino_cidade,
                    'has_baixa': cte.has_baixa,
                    'data_baixa': cte.data_baixa,
                    'processo_completo': cte.processo_completo,
                    'mes_emissao': cte.data_emissao.strftime('%Y-%m') if cte.data_emissao else None
                })
            
            df = pd.DataFrame(dados)
            
            # Análises principais
            ranking_veiculos = AnaliseVeiculoService._calcular_ranking_veiculos(df)
            metricas_performance = AnaliseVeiculoService._calcular_metricas_performance(df)
            analise_temporal = AnaliseVeiculoService._analise_temporal_veiculos(df)
            distribuicao_geografica = AnaliseVeiculoService._analise_geografica_veiculos(df)
            comparativo_eficiencia = AnaliseVeiculoService._calcular_eficiencia_veiculos(df)
            
            # Insights automáticos
            insights = AnaliseVeiculoService._gerar_insights(ranking_veiculos, metricas_performance)
            
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
                'analise_temporal': analise_temporal,
                'distribuicao_geografica': distribuicao_geografica,
                'comparativo_eficiencia': comparativo_eficiencia,
                'insights': insights
            }
            
        except Exception as e:
            logging.error(f"Erro na análise de veículos: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _calcular_ranking_veiculos(df: pd.DataFrame) -> List[Dict]:
        """Calcula ranking detalhado dos veículos por diversos critérios"""
        try:
            # Agrupar por veículo
            resultado = df.groupby('veiculo_placa').agg({
                'valor_total': ['sum', 'mean', 'count'],
                'numero_cte': 'nunique',
                'destinatario_nome': 'nunique',
                'origem_cidade': 'nunique',
                'destino_cidade': 'nunique',
                'has_baixa': 'sum',
                'processo_completo': 'sum'
            }).round(2)
            
            # Flatten column names
            resultado.columns = [
                'faturamento_total', 'ticket_medio', 'total_viagens',
                'ctes_unicos', 'clientes_unicos', 'origens_unicas',
                'destinos_unicos', 'baixas_realizadas', 'processos_completos'
            ]
            
            # Calcular métricas adicionais
            resultado['taxa_baixa'] = (resultado['baixas_realizadas'] / resultado['total_viagens'] * 100).round(2)
            resultado['taxa_conclusao'] = (resultado['processos_completos'] / resultado['total_viagens'] * 100).round(2)
            resultado['faturamento_por_dia'] = (resultado['faturamento_total'] / (datetime.now().date() - df['data_emissao'].min().date()).days).round(2)
            
            # Converter para lista de dicionários
            ranking = []
            for placa, row in resultado.iterrows():
                # Calcular score de performance (normalizado 0-100)
                score_faturamento = min(100, (row['faturamento_total'] / resultado['faturamento_total'].max()) * 100)
                score_viagens = min(100, (row['total_viagens'] / resultado['total_viagens'].max()) * 100)
                score_ticket = min(100, (row['ticket_medio'] / resultado['ticket_medio'].max()) * 100)
                score_conclusao = row['taxa_conclusao']
                
                score_total = (score_faturamento * 0.4 + score_viagens * 0.3 + score_ticket * 0.2 + score_conclusao * 0.1)
                
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
                    'origens_unicas': int(row['origens_unicas']),
                    'destinos_unicos': int(row['destinos_unicos']),
                    'taxa_baixa': float(row['taxa_baixa']),
                    'taxa_conclusao': float(row['taxa_conclusao']),
                    'faturamento_por_dia': float(row['faturamento_por_dia']),
                    'score_performance': round(score_total, 2),
                    'classificacao': classificacao,
                    'cor_classificacao': cor
                })
            
            # Ordenar por faturamento total (descendente)
            ranking.sort(key=lambda x: x['faturamento_total'], reverse=True)
            
            return ranking
            
        except Exception as e:
            logging.error(f"Erro no ranking de veículos: {str(e)}")
            return []
    
    @staticmethod
    def _calcular_metricas_performance(df: pd.DataFrame) -> Dict:
        """Calcula métricas de performance gerais da frota"""
        try:
            total_veiculos = df['veiculo_placa'].nunique()
            
            # Métricas por veículo
            metricas_por_veiculo = df.groupby('veiculo_placa').agg({
                'valor_total': ['sum', 'count'],
                'has_baixa': 'sum'
            })
            
            faturamento_por_veiculo = metricas_por_veiculo[('valor_total', 'sum')]
            viagens_por_veiculo = metricas_por_veiculo[('valor_total', 'count')]
            baixas_por_veiculo = metricas_por_veiculo[('has_baixa', 'sum')]
            
            # Estatísticas da frota
            return {
                'total_veiculos_ativos': total_veiculos,
                'faturamento_medio_por_veiculo': round(faturamento_por_veiculo.mean(), 2),
                'faturamento_mediano_por_veiculo': round(faturamento_por_veiculo.median(), 2),
                'viagens_media_por_veiculo': round(viagens_por_veiculo.mean(), 2),
                'viagens_mediana_por_veiculo': round(viagens_por_veiculo.median(), 2),
                'maior_faturamento_veiculo': {
                    'placa': faturamento_por_veiculo.idxmax(),
                    'valor': round(faturamento_por_veiculo.max(), 2)
                },
                'menor_faturamento_veiculo': {
                    'placa': faturamento_por_veiculo.idxmin(),
                    'valor': round(faturamento_por_veiculo.min(), 2)
                },
                'veiculo_mais_viagens': {
                    'placa': viagens_por_veiculo.idxmax(),
                    'quantidade': int(viagens_por_veiculo.max())
                },
                'taxa_utilizacao_frota': round((total_veiculos / max(1, total_veiculos)) * 100, 2),
                'concentracao_faturamento': {
                    'top_20_percent': round((faturamento_por_veiculo.nlargest(max(1, int(total_veiculos * 0.2))).sum() / faturamento_por_veiculo.sum()) * 100, 2)
                }
            }
            
        except Exception as e:
            logging.error(f"Erro nas métricas de performance: {str(e)}")
            return {}
    
    @staticmethod
    def _analise_temporal_veiculos(df: pd.DataFrame) -> Dict:
        """Análise temporal da performance dos veículos"""
        try:
            # Agrupar por mês e veículo
            df['mes_emissao'] = pd.to_datetime(df['data_emissao']).dt.to_period('M')
            
            temporal = df.groupby(['mes_emissao', 'veiculo_placa']).agg({
                'valor_total': 'sum',
                'numero_cte': 'count'
            }).reset_index()
            
            # Evolução mensal por veículo (top 5)
            top_veiculos = df.groupby('veiculo_placa')['valor_total'].sum().nlargest(5).index
            
            evolucao_top_veiculos = {}
            for veiculo in top_veiculos:
                dados_veiculo = temporal[temporal['veiculo_placa'] == veiculo]
                evolucao_top_veiculos[veiculo] = {
                    'meses': [str(mes) for mes in dados_veiculo['mes_emissao']],
                    'faturamento': dados_veiculo['valor_total'].tolist(),
                    'viagens': dados_veiculo['numero_cte'].tolist()
                }
            
            # Análise de sazonalidade
            sazonalidade = df.groupby(df['data_emissao'].dt.month)['valor_total'].sum()
            mes_mais_produtivo = sazonalidade.idxmax()
            mes_menos_produtivo = sazonalidade.idxmin()
            
            return {
                'evolucao_top_veiculos': evolucao_top_veiculos,
                'sazonalidade': {
                    'mes_mais_produtivo': mes_mais_produtivo,
                    'valor_mes_mais_produtivo': round(sazonalidade.max(), 2),
                    'mes_menos_produtivo': mes_menos_produtivo,
                    'valor_mes_menos_produtivo': round(sazonalidade.min(), 2),
                    'variacao_sazonal': round(((sazonalidade.max() - sazonalidade.min()) / sazonalidade.max()) * 100, 2)
                }
            }
            
        except Exception as e:
            logging.error(f"Erro na análise temporal: {str(e)}")
            return {}
    
    @staticmethod
    def _analise_geografica_veiculos(df: pd.DataFrame) -> Dict:
        """Análise da distribuição geográfica dos veículos"""
        try:
            # Rotas mais utilizadas por veículo
            df['rota'] = df['origem_cidade'].fillna('N/A') + ' → ' + df['destino_cidade'].fillna('N/A')
            
            rotas_por_veiculo = df.groupby('veiculo_placa')['rota'].value_counts().groupby(level=0).head(3)
            
            # Análise de origem e destino
            origens_mais_utilizadas = df['origem_cidade'].value_counts().head(10)
            destinos_mais_utilizados = df['destino_cidade'].value_counts().head(10)
            
            # Veículos por região
            veiculos_por_origem = df.groupby('origem_cidade')['veiculo_placa'].nunique().sort_values(ascending=False)
            
            return {
                'origens_principais': {
                    'cidades': origens_mais_utilizadas.index.tolist(),
                    'quantidade_viagens': origens_mais_utilizadas.tolist()
                },
                'destinos_principais': {
                    'cidades': destinos_mais_utilizados.index.tolist(),
                    'quantidade_viagens': destinos_mais_utilizados.tolist()
                },
                'veiculos_por_regiao': {
                    'regioes': veiculos_por_origem.index.tolist()[:10],
                    'quantidade_veiculos': veiculos_por_origem.tolist()[:10]
                },
                'total_rotas_unicas': df['rota'].nunique(),
                'rota_mais_frequente': df['rota'].value_counts().index[0] if not df.empty else 'N/A',
                'frequencia_rota_principal': int(df['rota'].value_counts().iloc[0]) if not df.empty else 0
            }
            
        except Exception as e:
            logging.error(f"Erro na análise geográfica: {str(e)}")
            return {}
    
    @staticmethod
    def _calcular_eficiencia_veiculos(df: pd.DataFrame) -> Dict:
        """Calcula métricas de eficiência dos veículos"""
        try:
            # Eficiência por período (últimos 30 dias vs anterior)
            data_corte = datetime.now().date() - timedelta(days=30)
            
            df_recente = df[df['data_emissao'] >= data_corte]
            df_anterior = df[df['data_emissao'] < data_corte]
            
            eficiencia_recente = df_recente.groupby('veiculo_placa')['valor_total'].sum()
            eficiencia_anterior = df_anterior.groupby('veiculo_placa')['valor_total'].sum()
            
            # Calcular variação de eficiência
            variacao_eficiencia = {}
            for veiculo in eficiencia_recente.index:
                valor_recente = eficiencia_recente.get(veiculo, 0)
                valor_anterior = eficiencia_anterior.get(veiculo, 0)
                
                if valor_anterior > 0:
                    variacao = ((valor_recente - valor_anterior) / valor_anterior) * 100
                else:
                    variacao = 100 if valor_recente > 0 else 0
                
                variacao_eficiencia[veiculo] = round(variacao, 2)
            
            # Ranking de eficiência
            ranking_eficiencia = sorted(variacao_eficiencia.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'ranking_eficiencia': ranking_eficiencia[:10],  # Top 10
                'veiculos_em_alta': [v for v, var in ranking_eficiencia if var > 0][:5],
                'veiculos_em_baixa': [v for v, var in ranking_eficiencia if var < 0][-5:],
                'media_variacao_eficiencia': round(np.mean(list(variacao_eficiencia.values())), 2),
                'periodo_comparacao': {
                    'recente': f'Últimos 30 dias',
                    'anterior': f'30 dias anteriores'
                }
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo de eficiência: {str(e)}")
            return {}
    
    @staticmethod
    def _gerar_insights(ranking_veiculos: List[Dict], metricas_performance: Dict) -> List[Dict]:
        """Gera insights automáticos baseado nas análises"""
        insights = []
        
        try:
            if ranking_veiculos:
                # Insight sobre o veículo top
                top_veiculo = ranking_veiculos[0]
                insights.append({
                    'tipo': 'destaque',
                    'titulo': f'Veículo Destaque: {top_veiculo["veiculo_placa"]}',
                    'descricao': f'Líder em faturamento com R$ {top_veiculo["faturamento_total"]:,.2f} e {top_veiculo["total_viagens"]} viagens',
                    'cor': 'success'
                })
                
                # Insight sobre concentração
                if len(ranking_veiculos) >= 5:
                    top_5_faturamento = sum(v['faturamento_total'] for v in ranking_veiculos[:5])
                    total_faturamento = sum(v['faturamento_total'] for v in ranking_veiculos)
                    concentracao = (top_5_faturamento / total_faturamento) * 100
                    
                    if concentracao > 80:
                        insights.append({
                            'tipo': 'alerta',
                            'titulo': 'Alta Concentração de Faturamento',
                            'descricao': f'Top 5 veículos respondem por {concentracao:.1f}% do faturamento total',
                            'cor': 'warning'
                        })
                
                # Insight sobre performance baixa
                baixa_performance = [v for v in ranking_veiculos if v['score_performance'] < 40]
                if baixa_performance:
                    insights.append({
                        'tipo': 'melhoria',
                        'titulo': f'{len(baixa_performance)} Veículos com Baixa Performance',
                        'descricao': 'Considere analisar operação e otimizar rotas',
                        'cor': 'info'
                    })
            
            return insights
            
        except Exception as e:
            logging.error(f"Erro ao gerar insights: {str(e)}")
            return []
    
    @staticmethod
    def obter_lista_veiculos() -> List[str]:
        """Obtém lista de placas de veículos para filtro"""
        try:
            veiculos = db.session.query(CTE.veiculo_placa).distinct().filter(
                CTE.veiculo_placa.isnot(None)
            ).order_by(CTE.veiculo_placa).all()
            
            return [veiculo[0].strip().upper() for veiculo in veiculos if veiculo[0]]
            
        except Exception as e:
            logging.error(f"Erro ao obter lista de veículos: {str(e)}")
            return []
    
    @staticmethod
    def _analise_vazia() -> Dict:
        """Retorna estrutura vazia para análise"""
        return {
            'success': False,
            'total_veiculos': 0,
            'total_viagens': 0,
            'faturamento_total': 0.0,
            'ranking_veiculos': [],
            'metricas_performance': {},
            'analise_temporal': {},
            'distribuicao_geografica': {},
            'comparativo_eficiencia': {},
            'insights': [],
            'error': 'Nenhum dado encontrado para análise'
        }