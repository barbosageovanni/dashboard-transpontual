#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Análise Financeira - Dashboard Baker Flask (ATUALIZADO)
app/services/analise_financeira_service.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
import logging
from app.services.projecoes_service import ProjecoesService
from app.services.analise_veiculo_service import AnaliseVeiculoService

class AnaliseFinanceiraService:
    """Serviço principal para análise financeira completa - VERSÃO EXPANDIDA"""
    
    @staticmethod
    def analise_completa(filtro_dias: int = 180, filtro_cliente: str = None) -> Dict:
        """
        Análise financeira completa com novos períodos: 7, 15, 30, 60, 90, 180 dias
        """
        try:
            # Validar filtros - NOVOS PERÍODOS ADICIONADOS
            filtros_validos = [7, 15, 30, 60, 90, 180]
            if filtro_dias not in filtros_validos:
                filtro_dias = 180
            
            # Buscar dados base
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            query = CTE.query.filter(CTE.data_emissao >= data_limite)
            
            # Aplicar filtro de cliente se fornecido
            if filtro_cliente:
                query = query.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
            
            ctes = query.all()
            
            if not ctes:
                return AnaliseFinanceiraService._analise_vazia()
            
            # Preparar DataFrame base
            df = AnaliseFinanceiraService._preparar_dataframe(ctes)
            
            # MÓDULOS DE ANÁLISE EXPANDIDOS
            
            # 1. Métricas fundamentais (existente - melhorado)
            metricas_fundamentais = AnaliseFinanceiraService._calcular_metricas_fundamentais(df)
            
            # 2. Análise de receita (existente - melhorado)
            analise_receita = AnaliseFinanceiraService._analisar_receita(df)
            
            # 3. 🆕 PROJEÇÃO FUTURA (NOVO)
            projecao_futura = ProjecoesService.projecao_recebimentos_3_meses()
            
            # 4. 🆕 COMPARAÇÃO TEMPORAL (NOVO)
            comparacao_temporal = ProjecoesService.analise_comparativa_periodos(filtro_dias)
            
            # 5. 🆕 ANÁLISE POR VEÍCULO (NOVO) 
            analise_veiculos = AnaliseVeiculoService.analise_completa_veiculos(filtro_dias)
            
            # 6. Análise de clientes (existente - melhorado)
            analise_clientes = AnaliseFinanceiraService._analisar_clientes(df)
            
            # 7. Gráficos para dashboard (existente - melhorado)
            graficos = AnaliseFinanceiraService._gerar_graficos(df)
            
            # 8. 🆕 INDICADORES DE TENDÊNCIA (NOVO)
            indicadores_tendencia = AnaliseFinanceiraService._calcular_indicadores_tendencia(df, filtro_dias)
            
            # 9. 🆕 ANÁLISE DE SAZONALIDADE (NOVO)
            analise_sazonalidade = AnaliseFinanceiraService._analisar_sazonalidade(df)
            
            # 10. 🆕 SCORE DE SAÚDE FINANCEIRA (NOVO)
            score_saude = AnaliseFinanceiraService._calcular_score_saude_financeira(metricas_fundamentais, analise_receita)
            
            # Resultado final expandido
            return {
                'success': True,
                'data_analise': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'periodo_analise': {
                    'filtro_dias': filtro_dias,
                    'data_inicio': data_limite.strftime('%d/%m/%Y'),
                    'data_fim': datetime.now().date().strftime('%d/%m/%Y'),
                    'filtro_cliente': filtro_cliente,
                    'total_registros': len(df)
                },
                
                # MÓDULOS PRINCIPAIS
                'metricas_fundamentais': metricas_fundamentais,
                'analise_receita': analise_receita,
                'analise_clientes': analise_clientes,
                
                # 🆕 NOVOS MÓDULOS
                'projecao_futura': projecao_futura,
                'comparacao_temporal': comparacao_temporal,
                'analise_veiculos': analise_veiculos,
                'indicadores_tendencia': indicadores_tendencia,
                'analise_sazonalidade': analise_sazonalidade,
                'score_saude_financeira': score_saude,
                
                # VISUALIZAÇÕES
                'graficos': graficos,
                
                # RESUMO EXECUTIVO
                'resumo_executivo': AnaliseFinanceiraService._gerar_resumo_executivo(
                    metricas_fundamentais, analise_receita, projecao_futura, score_saude
                )
            }
            
        except Exception as e:
            logging.error(f"Erro na análise financeira completa: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _calcular_indicadores_tendencia(df: pd.DataFrame, filtro_dias: int) -> Dict:
        """🆕 Calcula indicadores de tendência baseados no período"""
        try:
            # Dividir período em segmentos para análise de tendência
            df['data_emissao'] = pd.to_datetime(df['data_emissao'])
            
            if filtro_dias <= 15:
                # Para períodos curtos, analisar por dia
                df['periodo'] = df['data_emissao'].dt.date
                agrupamento = 'diário'
            elif filtro_dias <= 60:
                # Para períodos médios, analisar por semana
                df['periodo'] = df['data_emissao'].dt.to_period('W')
                agrupamento = 'semanal'
            else:
                # Para períodos longos, analisar por mês
                df['periodo'] = df['data_emissao'].dt.to_period('M')
                agrupamento = 'mensal'
            
            # Calcular métricas por período
            tendencia = df.groupby('periodo').agg({
                'valor_total': ['sum', 'count', 'mean'],
                'destinatario_nome': 'nunique'
            }).reset_index()
            
            # Flatten columns
            tendencia.columns = ['periodo', 'receita_total', 'quantidade_ctes', 'ticket_medio', 'clientes_unicos']
            
            # Calcular tendência linear (slope)
            if len(tendencia) >= 3:
                from scipy.stats import linregress
                x = np.arange(len(tendencia))
                
                slope_receita, _, r_receita, _, _ = linregress(x, tendencia['receita_total'])
                slope_quantidade, _, r_quantidade, _, _ = linregress(x, tendencia['quantidade_ctes'])
                slope_ticket, _, r_ticket, _, _ = linregress(x, tendencia['ticket_medio'])
                
                # Interpretar tendências
                def interpretar_tendencia(slope, r_value):
                    if abs(r_value) < 0.3:
                        return "Estável", "secondary"
                    elif slope > 0:
                        return "Crescimento", "success"
                    else:
                        return "Declínio", "danger"
                
                tendencia_receita, cor_receita = interpretar_tendencia(slope_receita, r_receita)
                tendencia_quantidade, cor_quantidade = interpretar_tendencia(slope_quantidade, r_quantidade)
                tendencia_ticket, cor_ticket = interpretar_tendencia(slope_ticket, r_ticket)
                
                return {
                    'agrupamento': agrupamento,
                    'periodos_analisados': len(tendencia),
                    'receita': {
                        'tendencia': tendencia_receita,
                        'cor': cor_receita,
                        'variacao_percentual': round((slope_receita / tendencia['receita_total'].mean()) * 100, 2),
                        'confianca': round(r_receita ** 2, 3)
                    },
                    'quantidade': {
                        'tendencia': tendencia_quantidade,
                        'cor': cor_quantidade,
                        'variacao_percentual': round((slope_quantidade / tendencia['quantidade_ctes'].mean()) * 100, 2),
                        'confianca': round(r_quantidade ** 2, 3)
                    },
                    'ticket_medio': {
                        'tendencia': tendencia_ticket,
                        'cor': cor_ticket,
                        'variacao_percentual': round((slope_ticket / tendencia['ticket_medio'].mean()) * 100, 2),
                        'confianca': round(r_ticket ** 2, 3)
                    },
                    'dados_grafico': {
                        'labels': [str(p) for p in tendencia['periodo']],
                        'receita': tendencia['receita_total'].tolist(),
                        'quantidade': tendencia['quantidade_ctes'].tolist(),
                        'ticket_medio': tendencia['ticket_medio'].tolist()
                    }
                }
            else:
                return {
                    'agrupamento': agrupamento,
                    'periodos_analisados': len(tendencia),
                    'erro': 'Dados insuficientes para análise de tendência'
                }
                
        except Exception as e:
            logging.error(f"Erro nos indicadores de tendência: {str(e)}")
            return {'erro': str(e)}
    
    @staticmethod
    def _analisar_sazonalidade(df: pd.DataFrame) -> Dict:
        """🆕 Analisa padrões sazonais nos dados"""
        try:
            df['data_emissao'] = pd.to_datetime(df['data_emissao'])
            
            # Análise por mês do ano
            df['mes'] = df['data_emissao'].dt.month
            por_mes = df.groupby('mes')['valor_total'].sum()
            
            # Análise por dia da semana
            df['dia_semana'] = df['data_emissao'].dt.dayofweek  # 0=Monday, 6=Sunday
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            por_dia_semana = df.groupby('dia_semana')['valor_total'].sum()
            
            # Análise por dia do mês
            df['dia_mes'] = df['data_emissao'].dt.day
            por_dia_mes = df.groupby('dia_mes')['valor_total'].sum()
            
            # Identificar padrões
            mes_mais_forte = por_mes.idxmax()
            mes_mais_fraco = por_mes.idxmin()
            dia_semana_mais_forte = por_dia_semana.idxmax()
            dia_semana_mais_fraco = por_dia_semana.idxmin()
            
            # Calcular coeficiente de variação (medida de sazonalidade)
            cv_mensal = (por_mes.std() / por_mes.mean()) * 100
            cv_semanal = (por_dia_semana.std() / por_dia_semana.mean()) * 100
            
            # Interpretar níveis de sazonalidade
            def interpretar_sazonalidade(cv):
                if cv < 20:
                    return "Baixa", "success"
                elif cv < 40:
                    return "Moderada", "warning"
                else:
                    return "Alta", "danger"
            
            nivel_sazonal_mensal, cor_mensal = interpretar_sazonalidade(cv_mensal)
            nivel_sazonal_semanal, cor_semanal = interpretar_sazonalidade(cv_semanal)
            
            meses_nomes = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            
            return {
                'sazonalidade_mensal': {
                    'nivel': nivel_sazonal_mensal,
                    'cor': cor_mensal,
                    'coeficiente_variacao': round(cv_mensal, 2),
                    'mes_mais_forte': meses_nomes.get(mes_mais_forte, 'N/A'),
                    'valor_mes_mais_forte': round(por_mes.max(), 2),
                    'mes_mais_fraco': meses_nomes.get(mes_mais_fraco, 'N/A'),
                    'valor_mes_mais_fraco': round(por_mes.min(), 2),
                    'dados_grafico': {
                        'labels': [meses_nomes.get(m, str(m)) for m in por_mes.index],
                        'valores': por_mes.tolist()
                    }
                },
                'sazonalidade_semanal': {
                    'nivel': nivel_sazonal_semanal,
                    'cor': cor_semanal,
                    'coeficiente_variacao': round(cv_semanal, 2),
                    'dia_mais_forte': dias_semana[dia_semana_mais_forte],
                    'valor_dia_mais_forte': round(por_dia_semana.max(), 2),
                    'dia_mais_fraco': dias_semana[dia_semana_mais_fraco],
                    'valor_dia_mais_fraco': round(por_dia_semana.min(), 2),
                    'dados_grafico': {
                        'labels': [dias_semana[d] for d in por_dia_semana.index],
                        'valores': por_dia_semana.tolist()
                    }
                },
                'distribuicao_mensal': {
                    'labels': [f'Dia {d}' for d in por_dia_mes.index],
                    'valores': por_dia_mes.tolist()
                }
            }
            
        except Exception as e:
            logging.error(f"Erro na análise de sazonalidade: {str(e)}")
            return {'erro': str(e)}
    
    @staticmethod
    def _calcular_score_saude_financeira(metricas_fundamentais: Dict, analise_receita: Dict) -> Dict:
        """🆕 Calcula score de saúde financeira (0-100)"""
        try:
            score_components = {}
            
            # 1. Volume de Receita (25 pontos)
            receita_total = metricas_fundamentais.get('receita_total', 0)
            if receita_total >= 1000000:  # >= 1M
                score_components['receita'] = 25
            elif receita_total >= 500000:  # >= 500K
                score_components['receita'] = 20
            elif receita_total >= 100000:  # >= 100K
                score_components['receita'] = 15
            elif receita_total >= 50000:   # >= 50K
                score_components['receita'] = 10
            else:
                score_components['receita'] = 5
            
            # 2. Taxa de Pagamento (25 pontos)
            taxa_pagamento = metricas_fundamentais.get('taxa_pagamento', 0)
            if taxa_pagamento >= 90:
                score_components['pagamento'] = 25
            elif taxa_pagamento >= 80:
                score_components['pagamento'] = 20
            elif taxa_pagamento >= 70:
                score_components['pagamento'] = 15
            elif taxa_pagamento >= 60:
                score_components['pagamento'] = 10
            else:
                score_components['pagamento'] = 5
            
            # 3. Diversificação de Clientes (20 pontos)
            clientes_unicos = metricas_fundamentais.get('clientes_unicos', 0)
            if clientes_unicos >= 50:
                score_components['diversificacao'] = 20
            elif clientes_unicos >= 30:
                score_components['diversificacao'] = 15
            elif clientes_unicos >= 20:
                score_components['diversificacao'] = 10
            elif clientes_unicos >= 10:
                score_components['diversificacao'] = 7
            else:
                score_components['diversificacao'] = 3
            
            # 4. Taxa de Conclusão de Processos (15 pontos)
            taxa_conclusao = metricas_fundamentais.get('taxa_conclusao', 0)
            if taxa_conclusao >= 95:
                score_components['conclusao'] = 15
            elif taxa_conclusao >= 85:
                score_components['conclusao'] = 12
            elif taxa_conclusao >= 75:
                score_components['conclusao'] = 9
            elif taxa_conclusao >= 65:
                score_components['conclusao'] = 6
            else:
                score_components['conclusao'] = 3
            
            # 5. Crescimento da Receita (15 pontos)
            crescimento = analise_receita.get('crescimento_mensal', 0)
            if crescimento >= 10:
                score_components['crescimento'] = 15
            elif crescimento >= 5:
                score_components['crescimento'] = 12
            elif crescimento >= 0:
                score_components['crescimento'] = 8
            elif crescimento >= -5:
                score_components['crescimento'] = 5
            else:
                score_components['crescimento'] = 2
            
            # Score total
            score_total = sum(score_components.values())
            
            # Classificação
            if score_total >= 85:
                classificacao = "Excelente"
                cor = "success"
                recomendacao = "Saúde financeira excelente. Continue as boas práticas."
            elif score_total >= 70:
                classificacao = "Boa"
                cor = "info"
                recomendacao = "Boa saúde financeira. Pequenos ajustes podem otimizar ainda mais."
            elif score_total >= 55:
                classificacao = "Regular"
                cor = "warning"
                recomendacao = "Saúde financeira regular. Foque em melhorar taxa de pagamento e diversificação."
            elif score_total >= 40:
                classificacao = "Fraca"
                cor = "danger"
                recomendacao = "Saúde financeira preocupante. Ação imediata necessária."
            else:
                classificacao = "Crítica"
                cor = "dark"
                recomendacao = "Situação crítica. Revisar urgentemente estratégia financeira."
            
            return {
                'score_total': score_total,
                'score_maximo': 100,
                'classificacao': classificacao,
                'cor': cor,
                'recomendacao': recomendacao,
                'componentes': {
                    'receita': {
                        'pontos': score_components['receita'],
                        'maximo': 25,
                        'percentual': round((score_components['receita'] / 25) * 100, 1)
                    },
                    'pagamento': {
                        'pontos': score_components['pagamento'],
                        'maximo': 25,
                        'percentual': round((score_components['pagamento'] / 25) * 100, 1)
                    },
                    'diversificacao': {
                        'pontos': score_components['diversificacao'],
                        'maximo': 20,
                        'percentual': round((score_components['diversificacao'] / 20) * 100, 1)
                    },
                    'conclusao': {
                        'pontos': score_components['conclusao'],
                        'maximo': 15,
                        'percentual': round((score_components['conclusao'] / 15) * 100, 1)
                    },
                    'crescimento': {
                        'pontos': score_components['crescimento'],
                        'maximo': 15,
                        'percentual': round((score_components['crescimento'] / 15) * 100, 1)
                    }
                }
            }
            
        except Exception as e:
            logging.error(f"Erro no cálculo do score de saúde: {str(e)}")
            return {'erro': str(e)}
    
    @staticmethod
    def _gerar_resumo_executivo(metricas: Dict, receita: Dict, projecao: Dict, score: Dict) -> Dict:
        """🆕 Gera resumo executivo automático"""
        try:
            resumo = {
                'receita_atual': metricas.get('receita_total', 0),
                'crescimento_mensal': receita.get('crescimento_mensal', 0),
                'projecao_3_meses': projecao.get('total_projetado_3_meses', 0) if projecao.get('success') else 0,
                'score_saude': score.get('score_total', 0),
                'classificacao_saude': score.get('classificacao', 'N/A'),
                
                # Destaques automáticos
                'principais_insights': [],
                'alertas': [],
                'oportunidades': []
            }
            
            # Gerar insights automáticos
            if resumo['crescimento_mensal'] > 10:
                resumo['principais_insights'].append("Forte crescimento mensal da receita")
            elif resumo['crescimento_mensal'] < -5:
                resumo['alertas'].append("Declínio preocupante na receita mensal")
            
            if score.get('score_total', 0) >= 80:
                resumo['principais_insights'].append("Excelente saúde financeira geral")
            elif score.get('score_total', 0) < 50:
                resumo['alertas'].append("Saúde financeira requer atenção urgente")
            
            # Oportunidades baseadas em projeção
            if projecao.get('success') and projecao.get('total_projetado_3_meses', 0) > resumo['receita_atual']:
                resumo['oportunidades'].append("Projeção positiva para os próximos 3 meses")
            
            return resumo
            
        except Exception as e:
            logging.error(f"Erro no resumo executivo: {str(e)}")
            return {}
    
    # ========================================================================
    # MÉTODOS EXISTENTES MANTIDOS (com pequenas melhorias)
    # ========================================================================
    
    @staticmethod
    def _preparar_dataframe(ctes: List) -> pd.DataFrame:
        """Prepara DataFrame base para análises"""
        dados = []
        for cte in ctes:
            dados.append({
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome,
                'veiculo_placa': cte.veiculo_placa,
                'valor_total': float(cte.valor_total or 0),
                'data_emissao': cte.data_emissao,
                'data_baixa': cte.data_baixa,
                'has_baixa': cte.has_baixa,
                'processo_completo': cte.processo_completo,
                'origem_cidade': cte.origem_cidade,
                'destino_cidade': cte.destino_cidade
            })
        return pd.DataFrame(dados)
    
    @staticmethod
    def _calcular_metricas_fundamentais(df: pd.DataFrame) -> Dict:
        """Calcula métricas fundamentais do período"""
        total_ctes = len(df)
        receita_total = df['valor_total'].sum()
        clientes_unicos = df['destinatario_nome'].nunique()
        
        faturas_pagas = df[df['has_baixa'] == True].shape[0]
        faturas_pendentes = total_ctes - faturas_pagas
        
        valor_pago = df[df['has_baixa'] == True]['valor_total'].sum()
        valor_pendente = receita_total - valor_pago
        
        processos_completos = df[df['processo_completo'] == True].shape[0]
        
        return {
            'total_ctes': total_ctes,
            'receita_total': round(receita_total, 2),
            'clientes_unicos': clientes_unicos,
            'faturas_pagas': faturas_pagas,
            'faturas_pendentes': faturas_pendentes,
            'valor_pago': round(valor_pago, 2),
            'valor_pendente': round(valor_pendente, 2),
            'processos_completos': processos_completos,
            'ticket_medio': round(receita_total / total_ctes, 2) if total_ctes > 0 else 0,
            'taxa_pagamento': round((faturas_pagas / total_ctes) * 100, 2) if total_ctes > 0 else 0,
            'taxa_conclusao': round((processos_completos / total_ctes) * 100, 2) if total_ctes > 0 else 0
        }
    
    @staticmethod
    def _analisar_receita(df: pd.DataFrame) -> Dict:
        """Análise detalhada da receita"""
        if df.empty:
            return {'crescimento_mensal': 0, 'distribuicao_mensal': {}}
        
        df['mes_emissao'] = pd.to_datetime(df['data_emissao']).dt.to_period('M')
        receita_mensal = df.groupby('mes_emissao')['valor_total'].sum()
        
        if len(receita_mensal) >= 2:
            ultimo_mes = receita_mensal.iloc[-1]
            penultimo_mes = receita_mensal.iloc[-2]
            crescimento = ((ultimo_mes - penultimo_mes) / penultimo_mes) * 100 if penultimo_mes > 0 else 0
        else:
            crescimento = 0
        
        return {
            'crescimento_mensal': round(crescimento, 2),
            'receita_mensal_media': round(receita_mensal.mean(), 2),
            'distribuicao_mensal': {
                'labels': [str(mes) for mes in receita_mensal.index],
                'valores': receita_mensal.tolist()
            }
        }
    
    @staticmethod
    def _analisar_clientes(df: pd.DataFrame) -> Dict:
        """Análise de clientes"""
        if df.empty:
            return {'top_clientes': []}
        
        clientes = df.groupby('destinatario_nome').agg({
            'valor_total': ['sum', 'count'],
            'numero_cte': 'nunique'
        }).round(2)
        
        clientes.columns = ['faturamento', 'quantidade_viagens', 'ctes_unicos']
        top_clientes = clientes.nlargest(10, 'faturamento')
        
        return {
            'top_clientes': [
                {
                    'nome': nome,
                    'faturamento': float(row['faturamento']),
                    'viagens': int(row['quantidade_viagens']),
                    'ticket_medio': round(row['faturamento'] / row['quantidade_viagens'], 2)
                }
                for nome, row in top_clientes.iterrows()
            ]
        }
    
    @staticmethod
    def _gerar_graficos(df: pd.DataFrame) -> Dict:
        """Gera dados para gráficos"""
        if df.empty:
            return {}
        
        # Receita mensal
        df['mes_emissao'] = pd.to_datetime(df['data_emissao']).dt.to_period('M')
        receita_mensal = df.groupby('mes_emissao')['valor_total'].sum()
        
        # Top clientes
        top_clientes = df.groupby('destinatario_nome')['valor_total'].sum().nlargest(10)
        
        return {
            'receita_mensal': {
                'labels': [str(mes) for mes in receita_mensal.index],
                'valores': receita_mensal.tolist()
            },
            'top_clientes': {
                'labels': list(top_clientes.index),
                'valores': list(top_clientes.values)
            }
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
    
    @staticmethod
    def _analise_vazia() -> Dict:
        """Retorna estrutura vazia"""
        return {
            'success': False,
            'error': 'Nenhum dado encontrado para análise',
            'metricas_fundamentais': {},
            'analise_receita': {},
            'analise_clientes': {},
            'projecao_futura': {},
            'comparacao_temporal': {},
            'analise_veiculos': {},
            'graficos': {}
        }