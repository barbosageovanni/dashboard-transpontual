#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Métricas Expandidas - Dashboard Baker
Sistema completo de análise financeira e produtividade
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models.cte import CTE
from app import db
from sqlalchemy import func, and_, or_

# Configurações de Alertas Inteligentes - ATUALIZADAS
ALERTAS_CONFIG = {
    'ctes_sem_aprovacao': {
        'dias_limite': 7,
        'prioridade': 'alta',
        'acao_sugerida': 'Entrar em contato com o cliente para aprovação',
        'impacto_financeiro': 'medio'
    },
    'ctes_sem_faturas': {
        'dias_limite': 3,
        'prioridade': 'media',
        'acao_sugerida': 'Gerar fatura no sistema Bsoft',
        'impacto_financeiro': 'baixo'
    },
    'faturas_vencidas': {
        'dias_limite': 90,  # 90 dias após ENVIO FINAL
        'prioridade': 'critica',
        'acao_sugerida': 'Ação judicial de cobrança',
        'impacto_financeiro': 'alto'
    },
    'envio_final_pendente': {
        'dias_limite': 1,  # 1 dia após ATESTO
        'prioridade': 'media',
        'acao_sugerida': 'Completar envio final dos documentos',
        'impacto_financeiro': 'baixo'
    },
    'primeiro_envio_pendente': {
        'dias_limite': 10,
        'prioridade': 'alta',
        'acao_sugerida': 'Enviar documentos para aprovação',
        'impacto_financeiro': 'alto'
    }
}

# Configurações de Variações Temporais Expandidas
VARIACOES_CONFIG = [
    {
        'nome': 'CTE → Inclusão Fatura',
        'campo_inicio': 'data_emissao',
        'campo_fim': 'data_inclusao_fatura',
        'meta_dias': 2,
        'codigo': 'cte_inclusao_fatura',
        'categoria': 'processo_interno'
    },
    {
        'nome': 'Inclusão → 1º Envio', 
        'campo_inicio': 'data_inclusao_fatura',
        'campo_fim': 'primeiro_envio',
        'meta_dias': 1,
        'codigo': 'inclusao_primeiro_envio',
        'categoria': 'processo_interno'
    },
    {
        'nome': 'RQ/TMC → 1º Envio',
        'campo_inicio': 'data_rq_tmc', 
        'campo_fim': 'primeiro_envio',
        'meta_dias': 3,
        'codigo': 'rq_tmc_primeiro_envio',
        'categoria': 'processo_cliente'
    },
    {
        'nome': '1º Envio → Atesto',
        'campo_inicio': 'primeiro_envio',
        'campo_fim': 'data_atesto',
        'meta_dias': 7,
        'codigo': 'primeiro_envio_atesto',
        'categoria': 'processo_cliente'
    },
    {
        'nome': 'Atesto → Envio Final',
        'campo_inicio': 'data_atesto',
        'campo_fim': 'envio_final',
        'meta_dias': 2,
        'codigo': 'atesto_envio_final',
        'categoria': 'processo_interno'
    },
    {
        'nome': 'Processo Completo',
        'campo_inicio': 'data_emissao',
        'campo_fim': 'envio_final',
        'meta_dias': 15,
        'codigo': 'processo_completo',
        'categoria': 'processo_completo'
    },
    {
        'nome': 'CTE → Baixa',
        'campo_inicio': 'data_emissao',
        'campo_fim': 'data_baixa',
        'meta_dias': 30,
        'codigo': 'cte_baixa',
        'categoria': 'financeiro'
    }
]

class MetricasService:
    """Serviço completo de métricas financeiras e produtividade"""
    
    @staticmethod
    def gerar_metricas_expandidas() -> Dict:
        """Gera métricas expandidas com análises avançadas"""
        try:
            # Buscar todos os CTEs
            ctes = CTE.query.all()
            
            if not ctes:
                return MetricasService._metricas_vazias()
            
            # Converter para DataFrame para análise
            dados = []
            for cte in ctes:
                dados.append({
                    'numero_cte': cte.numero_cte,
                    'destinatario_nome': cte.destinatario_nome,
                    'veiculo_placa': cte.veiculo_placa,
                    'valor_total': float(cte.valor_total or 0),
                    'data_emissao': cte.data_emissao,
                    'data_baixa': cte.data_baixa,
                    'numero_fatura': cte.numero_fatura,
                    'data_inclusao_fatura': cte.data_inclusao_fatura,
                    'data_envio_processo': cte.data_envio_processo,
                    'primeiro_envio': cte.primeiro_envio,
                    'data_rq_tmc': cte.data_rq_tmc,
                    'data_atesto': cte.data_atesto,
                    'envio_final': cte.envio_final,
                    'has_baixa': cte.has_baixa,
                    'processo_completo': cte.processo_completo
                })
            
            df = pd.DataFrame(dados)
            
            # Calcular métricas
            return MetricasService._calcular_metricas(df)
            
        except Exception as e:
            print(f"Erro ao gerar métricas: {e}")
            return MetricasService._metricas_vazias()
    
    @staticmethod
    def _calcular_metricas(df: pd.DataFrame) -> Dict:
        """Calcula todas as métricas do DataFrame"""
        
        total_ctes = len(df)
        
        # Métricas básicas
        valor_total = df['valor_total'].sum()
        clientes_unicos = df['destinatario_nome'].nunique()
        veiculos_ativos = df['veiculo_placa'].nunique()
        
        # Métricas de faturamento
        faturas_pagas = len(df[df['has_baixa'] == True])
        faturas_pendentes = len(df[df['has_baixa'] == False])
        valor_pago = df[df['has_baixa'] == True]['valor_total'].sum()
        valor_pendente = df[df['has_baixa'] == False]['valor_total'].sum()
        
        # Métricas de fatura
        tem_fatura = df['numero_fatura'].notna() & (df['numero_fatura'] != '')
        ctes_com_fatura = len(df[tem_fatura])
        ctes_sem_fatura = len(df[~tem_fatura])
        valor_com_fatura = df[tem_fatura]['valor_total'].sum()
        valor_sem_fatura = df[~tem_fatura]['valor_total'].sum()
        
        # Métricas de envio final
        tem_envio_final = df['envio_final'].notna()
        ctes_com_envio_final = len(df[tem_envio_final])
        ctes_sem_envio_final = len(df[~tem_envio_final])
        valor_com_envio_final = df[tem_envio_final]['valor_total'].sum()
        valor_sem_envio_final = df[~tem_envio_final]['valor_total'].sum()
        
        # Processos completos
        processos_completos = len(df[df['processo_completo'] == True])
        processos_incompletos = total_ctes - processos_completos
        
        # Métricas financeiras avançadas
        ticket_medio = df['valor_total'].mean() if total_ctes > 0 else 0.0
        maior_valor = df['valor_total'].max() if total_ctes > 0 else 0.0
        menor_valor = df['valor_total'].min() if total_ctes > 0 else 0.0
        
        # Análise temporal
        receita_mensal_media, crescimento_mensal = MetricasService._calcular_crescimento_mensal(df)
        
        return {
            'total_ctes': total_ctes,
            'valor_total': valor_total,
            'clientes_unicos': clientes_unicos,
            'veiculos_ativos': veiculos_ativos,
            'faturas_pagas': faturas_pagas,
            'faturas_pendentes': faturas_pendentes,
            'valor_pago': valor_pago,
            'valor_pendente': valor_pendente,
            'ctes_com_fatura': ctes_com_fatura,
            'ctes_sem_fatura': ctes_sem_fatura,
            'valor_com_fatura': valor_com_fatura,
            'valor_sem_fatura': valor_sem_fatura,
            'ctes_com_envio_final': ctes_com_envio_final,
            'ctes_sem_envio_final': ctes_sem_envio_final,
            'valor_com_envio_final': valor_com_envio_final,
            'valor_sem_envio_final': valor_sem_envio_final,
            'processos_completos': processos_completos,
            'processos_incompletos': processos_incompletos,
            'ticket_medio': ticket_medio,
            'maior_valor': maior_valor,
            'menor_valor': menor_valor,
            'receita_mensal_media': receita_mensal_media,
            'crescimento_mensal': crescimento_mensal,
            # Taxas calculadas
            'taxa_conclusao': (processos_completos / total_ctes * 100) if total_ctes > 0 else 0,
            'taxa_pagamento': (faturas_pagas / total_ctes * 100) if total_ctes > 0 else 0,
            'taxa_faturamento': (ctes_com_fatura / total_ctes * 100) if total_ctes > 0 else 0
        }
    
    @staticmethod
    def _calcular_crescimento_mensal(df: pd.DataFrame) -> Tuple[float, float]:
        """Calcula receita mensal média e crescimento"""
        try:
            df_temp = df[df['data_emissao'].notna()].copy()
            if df_temp.empty:
                return 0.0, 0.0
            
            # Converter para datetime se necessário
            if not pd.api.types.is_datetime64_any_dtype(df_temp['data_emissao']):
                df_temp['data_emissao'] = pd.to_datetime(df_temp['data_emissao'])
            
            # Agrupar por mês
            df_temp['mes_ano'] = df_temp['data_emissao'].dt.to_period('M')
            receita_mensal = df_temp.groupby('mes_ano')['valor_total'].sum()
            
            receita_media = receita_mensal.mean() if len(receita_mensal) > 0 else 0.0
            
            # Crescimento (últimos 2 meses)
            crescimento = 0.0
            if len(receita_mensal) >= 2:
                ultimo = receita_mensal.iloc[-1]
                penultimo = receita_mensal.iloc[-2]
                if penultimo > 0:
                    crescimento = ((ultimo - penultimo) / penultimo) * 100
            
            return receita_media, crescimento
            
        except Exception as e:
            print(f"Erro no cálculo de crescimento: {e}")
            return 0.0, 0.0
    
    @staticmethod
    def calcular_alertas_inteligentes() -> Dict:
        """Sistema de alertas inteligentes - CORRIGIDO com lógicas atualizadas"""
        alertas = {
            'ctes_sem_aprovacao': {'qtd': 0, 'valor': 0.0, 'lista': []},
            'ctes_sem_faturas': {'qtd': 0, 'valor': 0.0, 'lista': []},
            'faturas_vencidas': {'qtd': 0, 'valor': 0.0, 'lista': []},
            'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
            'envio_final_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []}
        }
        
        try:
            hoje = datetime.now().date()
            
            # 1. CTEs sem aprovação (7 dias após emissão)
            ctes_sem_aprovacao = CTE.query.filter(
                and_(
                    CTE.data_emissao.isnot(None),
                    CTE.data_atesto.is_(None),
                    func.date_part('day', func.now() - CTE.data_emissao) > ALERTAS_CONFIG['ctes_sem_aprovacao']['dias_limite']
                )
            ).all()
            
            if ctes_sem_aprovacao:
                alertas['ctes_sem_aprovacao'] = {
                    'qtd': len(ctes_sem_aprovacao),
                    'valor': sum(float(cte.valor_total or 0) for cte in ctes_sem_aprovacao),
                    'lista': [cte.to_dict() for cte in ctes_sem_aprovacao[:10]]
                }
            
            # 2. CTEs sem faturas (3 dias após atesto)
            ctes_sem_faturas = CTE.query.filter(
                and_(
                    CTE.data_atesto.isnot(None),
                    or_(CTE.numero_fatura.is_(None), CTE.numero_fatura == ''),
                    func.date_part('day', func.now() - CTE.data_atesto) > ALERTAS_CONFIG['ctes_sem_faturas']['dias_limite']
                )
            ).all()
            
            if ctes_sem_faturas:
                alertas['ctes_sem_faturas'] = {
                    'qtd': len(ctes_sem_faturas),
                    'valor': sum(float(cte.valor_total or 0) for cte in ctes_sem_faturas),
                    'lista': [cte.to_dict() for cte in ctes_sem_faturas[:10]]
                }
            
            # 3. Faturas vencidas (90 dias após ENVIO FINAL, sem baixa) - LÓGICA CORRIGIDA
            faturas_vencidas = CTE.query.filter(
                and_(
                    CTE.envio_final.isnot(None),  # MUDANÇA: após envio final
                    CTE.data_baixa.is_(None),
                    func.date_part('day', func.now() - CTE.envio_final) > ALERTAS_CONFIG['faturas_vencidas']['dias_limite']
                )
            ).all()
            
            if faturas_vencidas:
                alertas['faturas_vencidas'] = {
                    'qtd': len(faturas_vencidas),
                    'valor': sum(float(cte.valor_total or 0) for cte in faturas_vencidas),
                    'lista': [cte.to_dict() for cte in faturas_vencidas[:10]]
                }
            
            # 4. Primeiro envio pendente (10 dias após emissão)
            primeiro_envio_pendente = CTE.query.filter(
                and_(
                    CTE.data_emissao.isnot(None),
                    CTE.primeiro_envio.is_(None),
                    func.date_part('day', func.now() - CTE.data_emissao) > ALERTAS_CONFIG['primeiro_envio_pendente']['dias_limite']
                )
            ).all()
            
            if primeiro_envio_pendente:
                alertas['primeiro_envio_pendente'] = {
                    'qtd': len(primeiro_envio_pendente),
                    'valor': sum(float(cte.valor_total or 0) for cte in primeiro_envio_pendente),
                    'lista': [cte.to_dict() for cte in primeiro_envio_pendente[:10]]
                }
            
            # 5. Envio Final Pendente (1 dia após ATESTO) - LÓGICA CORRIGIDA
            envio_final_pendente = CTE.query.filter(
                and_(
                    CTE.data_atesto.isnot(None),  # Tem atesto
                    or_(CTE.envio_final.is_(None), CTE.envio_final == ''),  # Sem envio final
                    func.date_part('day', func.now() - CTE.data_atesto) > ALERTAS_CONFIG['envio_final_pendente']['dias_limite']  # 1 dia após atesto
                )
            ).all()
            
            if envio_final_pendente:
                alertas['envio_final_pendente'] = {
                    'qtd': len(envio_final_pendente),
                    'valor': sum(float(cte.valor_total or 0) for cte in envio_final_pendente),
                    'lista': [cte.to_dict() for cte in envio_final_pendente[:10]]
                }
            
            return alertas
            
        except Exception as e:
            print(f"Erro ao calcular alertas: {e}")
            return alertas
    
    @staticmethod
    def calcular_variacoes_tempo_expandidas() -> Dict:
        """Sistema de análise de variações temporais expandido"""
        variacoes = {}
        
        try:
            # Buscar todos os CTEs
            ctes = CTE.query.all()
            
            if not ctes:
                return {}
            
            # Converter para DataFrame
            dados = []
            for cte in ctes:
                dados.append({
                    'data_emissao': cte.data_emissao,
                    'data_inclusao_fatura': cte.data_inclusao_fatura,
                    'primeiro_envio': cte.primeiro_envio,
                    'data_rq_tmc': cte.data_rq_tmc,
                    'data_atesto': cte.data_atesto,
                    'envio_final': cte.envio_final,
                    'data_baixa': cte.data_baixa,
                    'valor_total': float(cte.valor_total or 0)
                })
            
            df = pd.DataFrame(dados)
            
            # Calcular variações para cada configuração
            for config in VARIACOES_CONFIG:
                campo_inicio = config['campo_inicio']
                campo_fim = config['campo_fim']
                codigo = config['codigo']
                meta_dias = config['meta_dias']
                
                if campo_inicio in df.columns and campo_fim in df.columns:
                    # Filtrar registros válidos
                    mask = df[campo_inicio].notna() & df[campo_fim].notna()
                    
                    if mask.any():
                        # Converter para datetime se necessário
                        inicio = pd.to_datetime(df.loc[mask, campo_inicio])
                        fim = pd.to_datetime(df.loc[mask, campo_fim])
                        
                        # Calcular diferença em dias
                        dias = (fim - inicio).dt.days
                        
                        # Filtrar dias válidos (não negativos)
                        dias_validos = dias[dias >= 0]
                        
                        if len(dias_validos) > 0:
                            media = dias_validos.mean()
                            mediana = dias_validos.median()
                            percentil_90 = dias_validos.quantile(0.9)
                            
                            # Classificar performance
                            if media <= meta_dias:
                                performance = 'excelente'
                            elif media <= meta_dias * 1.5:
                                performance = 'bom'
                            elif media <= meta_dias * 2:
                                performance = 'atencao'
                            else:
                                performance = 'critico'
                            
                            variacoes[codigo] = {
                                'nome': config['nome'],
                                'media': round(media, 1),
                                'mediana': round(mediana, 1),
                                'percentil_90': round(percentil_90, 1),
                                'qtd': len(dias_validos),
                                'meta_dias': meta_dias,
                                'performance': performance,
                                'categoria': config['categoria'],
                                'desvio_meta': round(((media - meta_dias) / meta_dias * 100), 1) if meta_dias > 0 else 0,
                                'min_dias': int(dias_validos.min()),
                                'max_dias': int(dias_validos.max())
                            }
            
            return variacoes
            
        except Exception as e:
            print(f"Erro ao calcular variações temporais: {e}")
            return {}
    
    @staticmethod
    def _metricas_vazias() -> Dict:
        """Retorna métricas zeradas"""
        return {
            'total_ctes': 0, 'clientes_unicos': 0, 'valor_total': 0.0,
            'faturas_pagas': 0, 'faturas_pendentes': 0, 'valor_pago': 0.0,
            'valor_pendente': 0.0, 'ctes_com_fatura': 0, 'ctes_sem_fatura': 0,
            'valor_com_fatura': 0.0, 'valor_sem_fatura': 0.0, 'veiculos_ativos': 0,
            'ctes_com_envio_final': 0, 'ctes_sem_envio_final': 0,
            'valor_com_envio_final': 0.0, 'valor_sem_envio_final': 0.0,
            'processos_completos': 0, 'processos_incompletos': 0,
            'ticket_medio': 0.0, 'maior_valor': 0.0, 'menor_valor': 0.0,
            'receita_mensal_media': 0.0, 'crescimento_mensal': 0.0,
            'taxa_conclusao': 0.0, 'taxa_pagamento': 0.0, 'taxa_faturamento': 0.0
        }
    
    @staticmethod
    def gerar_dados_graficos() -> Dict:
        """Gera dados para todos os gráficos do dashboard"""
        try:
            ctes = CTE.query.all()
            
            if not ctes:
                return {'erro': 'Nenhum dado encontrado'}
            
            # Preparar dados
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
                    'mes_emissao': cte.data_emissao.strftime('%Y-%m') if cte.data_emissao else None
                })
            
            df = pd.DataFrame(dados)
            
            # 1. Evolução da receita mensal
            evolucao_mensal = MetricasService._calcular_evolucao_mensal(df)
            
            # 2. Top clientes por receita
            top_clientes = MetricasService._calcular_top_clientes(df)
            
            # 3. Distribuição de status
            distribuicao_status = MetricasService._calcular_distribuicao_status(df)
            
            # 4. Performance por veículo
            performance_veiculos = MetricasService._calcular_performance_veiculos(df)
            
            return {
                'evolucao_mensal': evolucao_mensal,
                'top_clientes': top_clientes,
                'distribuicao_status': distribuicao_status,
                'performance_veiculos': performance_veiculos
            }
            
        except Exception as e:
            print(f"Erro ao gerar dados de gráficos: {e}")
            return {'erro': str(e)}
    
    @staticmethod
    def _calcular_evolucao_mensal(df: pd.DataFrame) -> Dict:
        """Calcula evolução da receita mensal"""
        try:
            df_temp = df[df['data_emissao'].notna()].copy()
            if df_temp.empty:
                return {'labels': [], 'valores': [], 'quantidades': []}
            
            # Agrupar por mês
            evolucao = df_temp.groupby('mes_emissao').agg({
                'valor_total': 'sum',
                'numero_cte': 'count'
            }).reset_index()
            
            return {
                'labels': evolucao['mes_emissao'].tolist(),
                'valores': evolucao['valor_total'].tolist(),
                'quantidades': evolucao['numero_cte'].tolist()
            }
        except Exception as e:
            print(f"Erro na evolução mensal: {e}")
            return {'labels': [], 'valores': [], 'quantidades': []}
    
    @staticmethod
    def _calcular_top_clientes(df: pd.DataFrame) -> Dict:
        """Calcula top 10 clientes por receita"""
        try:
            top_clientes = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False).head(10)
            
            return {
                'labels': top_clientes.index.tolist(),
                'valores': top_clientes.values.tolist()
            }
        except Exception as e:
            print(f"Erro no top clientes: {e}")
            return {'labels': [], 'valores': []}
    
    @staticmethod
    def _calcular_distribuicao_status(df: pd.DataFrame) -> Dict:
        """Calcula distribuição de status"""
        try:
            com_baixa = len(df[df['has_baixa'] == True])
            sem_baixa = len(df[df['has_baixa'] == False])
            completos = len(df[df['processo_completo'] == True])
            incompletos = len(df[df['processo_completo'] == False])
            
            return {
                'baixas': {
                    'labels': ['Com Baixa', 'Sem Baixa'],
                    'valores': [com_baixa, sem_baixa]
                },
                'processos': {
                    'labels': ['Completos', 'Incompletos'],
                    'valores': [completos, incompletos]
                }
            }
        except Exception as e:
            print(f"Erro na distribuição de status: {e}")
            return {'baixas': {'labels': [], 'valores': []}, 'processos': {'labels': [], 'valores': []}}
    
    @staticmethod
    def _calcular_performance_veiculos(df: pd.DataFrame) -> Dict:
        """Calcula performance por veículo"""
        try:
            df_veiculos = df[df['veiculo_placa'].notna()]
            
            if df_veiculos.empty:
                return {'labels': [], 'valores': [], 'quantidades': []}
            
            performance = df_veiculos.groupby('veiculo_placa').agg({
                'valor_total': 'sum',
                'numero_cte': 'count'
            }).sort_values('valor_total', ascending=False).head(10)
            
            return {
                'labels': performance.index.tolist(),
                'valores': performance['valor_total'].tolist(),
                'quantidades': performance['numero_cte'].tolist()
            }
        except Exception as e:
            print(f"Erro na performance de veículos: {e}")
            return {'labels': [], 'valores': [], 'quantidades': []}