#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes para Análise Financeira - VERSÃO FINAL CORRIGIDA
app/routes/analise_financeira.py - SUBSTITUIR COMPLETAMENTE
"""

from flask import Blueprint, render_template, jsonify, request, send_file, make_response
from flask_login import login_required
from datetime import datetime, timedelta
from app.models.cte import CTE
from app import db
from sqlalchemy import func, and_, desc, extract, text
import logging
import calendar
import pandas as pd
import io
import json

bp = Blueprint('analise_financeira', __name__, url_prefix='/analise-financeira')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/')
@login_required
def index():
    """Página principal da análise financeira"""
    return render_template('analise_financeira/index.html')

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def aplicar_filtros_base(filtro_dias=180, filtro_cliente=None, data_inicio=None, data_fim=None):
    """Função auxiliar para aplicar filtros consistentemente"""
    try:
        query = CTE.query
        
        if data_inicio and data_fim:
            query = query.filter(CTE.data_emissao.between(data_inicio, data_fim))
        else:
            data_limite = datetime.now().date() - timedelta(days=int(filtro_dias))
            query = query.filter(CTE.data_emissao >= data_limite)
        
        if filtro_cliente and filtro_cliente.lower() not in ['todos', 'all', '']:
            query = query.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
        
        return query
        
    except Exception as e:
        logger.error(f"Erro ao aplicar filtros: {str(e)}")
        return CTE.query.filter(CTE.id == -1)

# ============================================================================
# APIS PRINCIPAIS
# ============================================================================

@bp.route('/api/test-conexao')
def api_test_conexao():
    """API de teste para verificar conectividade"""
    try:
        total_ctes = CTE.query.count()
        agora = datetime.now()
        primeiro_dia = agora.replace(day=1).date()
        
        ctes_mes = CTE.query.filter(CTE.data_emissao >= primeiro_dia).count()
        receita_mes = db.session.query(func.sum(CTE.valor_total)).filter(
            CTE.data_emissao >= primeiro_dia
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'status': 'Sistema funcionando',
            'total_ctes': total_ctes,
            'ctes_mes_corrente': ctes_mes,
            'receita_mes_corrente': float(receita_mes),
            'mes_referencia': agora.strftime('%m/%Y'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no teste de conexão: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/metricas-mes-corrente')
@login_required
def api_metricas_mes_corrente():
    """API para métricas do mês corrente"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 30))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        logger.info(f"Calculando métricas. Cliente: {filtro_cliente}, Dias: {filtro_dias}")
        
        with db.engine.connect() as connection:
            where_conditions = []
            params = {}
            
            if data_inicio and data_fim:
                where_conditions.append("data_emissao BETWEEN :data_inicio AND :data_fim")
                params['data_inicio'] = data_inicio
                params['data_fim'] = data_fim
            else:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                where_conditions.append("data_emissao >= :data_limite")
                params['data_limite'] = data_limite
            
            if filtro_cliente:
                where_conditions.append("destinatario_nome ILIKE :filtro_cliente")
                params['filtro_cliente'] = f'%{filtro_cliente}%'
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            sql_main = text(f"""
                SELECT 
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total,
                    COALESCE(AVG(valor_total), 0) as ticket_medio,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as ctes_com_baixa,
                    COALESCE(SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_baixado,
                    COUNT(CASE 
                        WHEN envio_final IS NOT NULL THEN 1 
                        WHEN envio_final IS NULL AND data_baixa IS NOT NULL THEN 1 
                        END) as ctes_faturados,
                    COALESCE(SUM(CASE 
                        WHEN envio_final IS NOT NULL THEN valor_total 
                        WHEN envio_final IS NULL AND data_baixa IS NOT NULL THEN valor_total 
                        ELSE 0 END), 0) as receita_faturada,
                    COUNT(CASE 
                        WHEN data_inclusao_fatura IS NOT NULL THEN 1 
                        WHEN data_inclusao_fatura IS NULL AND numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 
                        END) as ctes_com_faturas,
                    COALESCE(SUM(CASE 
                        WHEN data_inclusao_fatura IS NOT NULL THEN valor_total 
                        WHEN data_inclusao_fatura IS NULL AND numero_fatura IS NOT NULL AND numero_fatura != '' THEN valor_total 
                        ELSE 0 END), 0) as receita_com_faturas
                FROM dashboard_baker 
                WHERE {where_clause}
            """)
            
            result = connection.execute(sql_main, params).fetchone()
            
        receita_total = float(result.receita_total)
        receita_faturada = float(result.receita_faturada)
        receita_com_faturas_valor = float(result.receita_com_faturas)
        
        percentual_faturado = (receita_faturada / receita_total * 100) if receita_total > 0 else 0
        percentual_com_faturas = (receita_com_faturas_valor / receita_total * 100) if receita_total > 0 else 0
        percentual_baixado = (float(result.valor_baixado) / receita_total * 100) if receita_total > 0 else 0
        
        if data_inicio and data_fim:
            periodo_str = f"{data_inicio} a {data_fim}"
            mes_referencia = f"{data_inicio} - {data_fim}"
        else:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            periodo_str = f"{data_limite.strftime('%d/%m')} a {datetime.now().strftime('%d/%m')}"
            mes_referencia = f"Últimos {filtro_dias} dias"
        
        resultado = {
            'success': True,
            'mes_referencia': mes_referencia,
            'periodo': periodo_str,
            'filtros_aplicados': {
                'cliente': filtro_cliente,
                'dias': filtro_dias,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'metricas_basicas': {
                'receita_mes_atual': receita_total,
                'total_ctes': int(result.total_ctes),
                'ticket_medio': float(result.ticket_medio),
                'ctes_com_baixa': int(result.ctes_com_baixa),
                'valor_baixado': float(result.valor_baixado),
                'percentual_baixado': percentual_baixado
            },
            'receita_faturada': {
                'receita_total': receita_faturada,
                'quantidade_ctes': int(result.ctes_faturados),
                'percentual_total': percentual_faturado,
                'variacao_percentual': 0,
                'periodo_completo': periodo_str
            },
            'receita_com_faturas': {
                'receita_total': receita_com_faturas_valor,
                'quantidade_ctes': int(result.ctes_com_faturas),
                'ticket_medio': receita_com_faturas_valor / int(result.ctes_com_faturas) if int(result.ctes_com_faturas) > 0 else 0,
                'percentual_cobertura': percentual_com_faturas,
                'periodo_completo': periodo_str
            }
        }
        
        logger.info(f"Métricas calculadas: {result.total_ctes} CTEs, R$ {receita_total:,.2f}")
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro nas métricas: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao calcular métricas: {str(e)}'
        }), 500

@bp.route('/api/receita-faturada')
@login_required
def api_receita_faturada():
    """API para receita faturada"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        with db.engine.connect() as connection:
            where_conditions = []
            params = {}
            
            if data_inicio and data_fim:
                where_conditions.append("data_emissao BETWEEN :data_inicio AND :data_fim")
                params['data_inicio'] = data_inicio
                params['data_fim'] = data_fim
            else:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                where_conditions.append("data_emissao >= :data_limite")
                params['data_limite'] = data_limite
            
            if filtro_cliente:
                where_conditions.append("destinatario_nome ILIKE :filtro_cliente")
                params['filtro_cliente'] = f'%{filtro_cliente}%'
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            sql_receita_faturada = text(f"""
                SELECT 
                    COUNT(CASE 
                        WHEN envio_final IS NOT NULL THEN 1 
                        WHEN envio_final IS NULL AND data_baixa IS NOT NULL THEN 1 
                        END) as qtd_faturada,
                    COALESCE(SUM(CASE 
                        WHEN envio_final IS NOT NULL THEN valor_total 
                        WHEN envio_final IS NULL AND data_baixa IS NOT NULL THEN valor_total 
                        ELSE 0 END), 0) as valor_faturada,
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total,
                    EXTRACT(YEAR FROM COALESCE(envio_final, data_baixa)) as ano,
                    EXTRACT(MONTH FROM COALESCE(envio_final, data_baixa)) as mes
                FROM dashboard_baker 
                WHERE {where_clause}
                GROUP BY EXTRACT(YEAR FROM COALESCE(envio_final, data_baixa)), EXTRACT(MONTH FROM COALESCE(envio_final, data_baixa))
                ORDER BY ano DESC, mes DESC
            """)
            
            results = connection.execute(sql_receita_faturada, params).fetchall()
            
        if not results:
            return jsonify({
                'success': True,
                'dados': {
                    'receita_total': 0.0,
                    'quantidade_ctes': 0,
                    'percentual_total': 0.0,
                    'campo_usado': 'Nenhum',
                    'periodo_completo': 'Sem dados',
                    'evolucao_mensal': {'labels': [], 'valores': []}
                }
            })
        
        receita_valor = sum(float(row.valor_faturada or 0) for row in results)
        quantidade = sum(int(row.qtd_faturada or 0) for row in results)
        receita_total_geral = sum(float(row.receita_total or 0) for row in results)
        
        percentual = (receita_valor / receita_total_geral * 100) if receita_total_geral > 0 else 0
        
        evolucao_labels = []
        evolucao_valores = []
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for row in results[-12:]:
            if row.ano and row.mes:
                mes_nome = meses_nomes[int(row.mes) - 1]
                label = f"{mes_nome}/{int(row.ano)}"
                evolucao_labels.append(label)
                evolucao_valores.append(float(row.valor_faturada or 0))
        
        if data_inicio and data_fim:
            periodo_str = f"{data_inicio} a {data_fim}"
        else:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            periodo_str = f"{data_limite.strftime('%d/%m')} a {datetime.now().strftime('%d/%m')}"
        
        dados = {
            'receita_total': receita_valor,
            'quantidade_ctes': quantidade,
            'percentual_total': percentual,
            'campo_usado': 'envio_final/data_baixa (fallback automático)',
            'periodo_completo': periodo_str,
            'evolucao_mensal': {
                'labels': evolucao_labels,
                'valores': evolucao_valores
            },
            'filtros_aplicados': {
                'cliente': filtro_cliente,
                'dias': filtro_dias,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        }
        
        logger.info(f"Receita faturada: R$ {receita_valor:,.2f} ({quantidade} CTEs)")
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        logger.error(f"Erro na API receita faturada: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/receita-com-faturas')
@login_required
def api_receita_com_faturas():
    """API para receita com faturas"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        with db.engine.connect() as connection:
            where_conditions = []
            params = {}
            
            if data_inicio and data_fim:
                where_conditions.append("data_emissao BETWEEN :data_inicio AND :data_fim")
                params['data_inicio'] = data_inicio
                params['data_fim'] = data_fim
            else:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                where_conditions.append("data_emissao >= :data_limite")
                params['data_limite'] = data_limite
            
            if filtro_cliente:
                where_conditions.append("destinatario_nome ILIKE :filtro_cliente")
                params['filtro_cliente'] = f'%{filtro_cliente}%'
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            sql_receita_faturas = text(f"""
                SELECT 
                    COUNT(CASE 
                        WHEN data_inclusao_fatura IS NOT NULL THEN 1 
                        WHEN data_inclusao_fatura IS NULL AND numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 
                        END) as qtd_com_faturas,
                    COALESCE(SUM(CASE 
                        WHEN data_inclusao_fatura IS NOT NULL THEN valor_total 
                        WHEN data_inclusao_fatura IS NULL AND numero_fatura IS NOT NULL AND numero_fatura != '' THEN valor_total 
                        ELSE 0 END), 0) as valor_com_faturas,
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total,
                    EXTRACT(YEAR FROM COALESCE(data_inclusao_fatura, data_emissao)) as ano,
                    EXTRACT(MONTH FROM COALESCE(data_inclusao_fatura, data_emissao)) as mes
                FROM dashboard_baker 
                WHERE {where_clause}
                GROUP BY EXTRACT(YEAR FROM COALESCE(data_inclusao_fatura, data_emissao)), EXTRACT(MONTH FROM COALESCE(data_inclusao_fatura, data_emissao))
                ORDER BY ano DESC, mes DESC
            """)
            
            results = connection.execute(sql_receita_faturas, params).fetchall()
        
        if not results:
            return jsonify({
                'success': True,
                'dados': {
                    'receita_total': 0.0,
                    'quantidade_ctes': 0,
                    'ticket_medio': 0.0,
                    'percentual_cobertura': 0.0,
                    'campo_usado': 'Nenhum',
                    'periodo_completo': 'Sem dados',
                    'grafico': {'labels': [], 'valores': []}
                }
            })
        
        receita_valor = sum(float(row.valor_com_faturas or 0) for row in results)
        quantidade = sum(int(row.qtd_com_faturas or 0) for row in results)
        total_ctes_geral = sum(int(row.total_ctes or 0) for row in results)
        
        cobertura = (quantidade / total_ctes_geral * 100) if total_ctes_geral > 0 else 0
        ticket_medio = receita_valor / quantidade if quantidade > 0 else 0
        
        grafico_labels = []
        grafico_valores = []
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for row in results[-12:]:
            if row.ano and row.mes:
                mes_nome = meses_nomes[int(row.mes) - 1]
                label = f"{mes_nome}/{int(row.ano)}"
                grafico_labels.append(label)
                grafico_valores.append(float(row.valor_com_faturas or 0))
        
        if data_inicio and data_fim:
            periodo_str = f"{data_inicio} a {data_fim}"
        else:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            periodo_str = f"{data_limite.strftime('%d/%m')} a {datetime.now().strftime('%d/%m')}"
        
        dados = {
            'receita_total': receita_valor,
            'quantidade_ctes': quantidade,
            'ticket_medio': ticket_medio,
            'percentual_cobertura': cobertura,
            'campo_usado': 'data_inclusao_fatura/numero_fatura (fallback automático)',
            'periodo_completo': periodo_str,
            'grafico': {
                'labels': grafico_labels,
                'valores': grafico_valores
            },
            'filtros_aplicados': {
                'cliente': filtro_cliente,
                'dias': filtro_dias,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        }
        
        logger.info(f"Receita com faturas: R$ {receita_valor:,.2f} ({quantidade} CTEs)")
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        logger.error(f"Erro na API receita com faturas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/receita-media-mensal')
@login_required
def api_receita_media_mensal():
    """API para receita média mensal"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 365))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        with db.engine.connect() as connection:
            where_conditions = []
            params = {}
            
            if data_inicio and data_fim:
                where_conditions.append("data_emissao BETWEEN :data_inicio AND :data_fim")
                params['data_inicio'] = data_inicio
                params['data_fim'] = data_fim
            else:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                where_conditions.append("data_emissao >= :data_limite")
                params['data_limite'] = data_limite
            
            if filtro_cliente:
                where_conditions.append("destinatario_nome ILIKE :filtro_cliente")
                params['filtro_cliente'] = f'%{filtro_cliente}%'
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            sql_media_mensal = text(f"""
                SELECT 
                    EXTRACT(YEAR FROM data_emissao) as ano,
                    EXTRACT(MONTH FROM data_emissao) as mes,
                    COUNT(*) as qtd_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_mes
                FROM dashboard_baker 
                WHERE {where_clause}
                GROUP BY EXTRACT(YEAR FROM data_emissao), EXTRACT(MONTH FROM data_emissao)
                ORDER BY ano DESC, mes DESC
            """)
            
            results = connection.execute(sql_media_mensal, params).fetchall()
        
        if not results:
            return jsonify({
                'success': True,
                'dados': {
                    'receita_media_mensal': 0.0,
                    'receita_total_periodo': 0.0,
                    'meses_analisados': 0,
                    'maior_receita_mes': 0.0,
                    'menor_receita_mes': 0.0,
                    'tendencia': 'estável',
                    'evolucao_mensal': {'labels': [], 'valores': []}
                }
            })
        
        receitas_mensais = [float(row.receita_mes) for row in results]
        receita_media = sum(receitas_mensais) / len(receitas_mensais)
        receita_total = sum(receitas_mensais)
        maior_receita = max(receitas_mensais)
        menor_receita = min(receitas_mensais)
        
        tendencia = 'estável'
        if len(receitas_mensais) >= 6:
            ultimos_3 = sum(receitas_mensais[:3]) / 3
            anteriores_3 = sum(receitas_mensais[3:6]) / 3
            if ultimos_3 > anteriores_3 * 1.1:
                tendencia = 'crescimento'
            elif ultimos_3 < anteriores_3 * 0.9:
                tendencia = 'decréscimo'
        
        evolucao_labels = []
        evolucao_valores = []
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for row in reversed(results):
            if row.ano and row.mes:
                mes_nome = meses_nomes[int(row.mes) - 1]
                label = f"{mes_nome}/{int(row.ano)}"
                evolucao_labels.append(label)
                evolucao_valores.append(float(row.receita_mes))
        
        dados = {
            'receita_media_mensal': receita_media,
            'receita_total_periodo': receita_total,
            'meses_analisados': len(results),
            'maior_receita_mes': maior_receita,
            'menor_receita_mes': menor_receita,
            'tendencia': tendencia,
            'evolucao_mensal': {
                'labels': evolucao_labels,
                'valores': evolucao_valores
            },
            'filtros_aplicados': {
                'cliente': filtro_cliente,
                'dias': filtro_dias,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        }
        
        logger.info(f"Receita média mensal: R$ {receita_media:,.2f} ({len(results)} meses)")
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        logger.error(f"Erro na API receita média mensal: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/evolucao-receita-inclusao-fatura')
@login_required
def api_evolucao_receita_inclusao_fatura():
    """API para evolução da receita por data de inclusão de fatura"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 365))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        with db.engine.connect() as connection:
            where_conditions = ['data_inclusao_fatura IS NOT NULL']
            params = {}
            
            if data_inicio and data_fim:
                where_conditions.append("data_inclusao_fatura BETWEEN :data_inicio AND :data_fim")
                params['data_inicio'] = data_inicio
                params['data_fim'] = data_fim
            else:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                where_conditions.append("data_inclusao_fatura >= :data_limite")
                params['data_limite'] = data_limite
            
            if filtro_cliente:
                where_conditions.append("destinatario_nome ILIKE :filtro_cliente")
                params['filtro_cliente'] = f'%{filtro_cliente}%'
            
            where_clause = " AND ".join(where_conditions)
            
            sql_evolucao = text(f"""
                SELECT 
                    EXTRACT(YEAR FROM data_inclusao_fatura) as ano,
                    EXTRACT(MONTH FROM data_inclusao_fatura) as mes,
                    COUNT(*) as qtd_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_mes,
                    COALESCE(AVG(valor_total), 0) as ticket_medio_mes
                FROM dashboard_baker 
                WHERE {where_clause}
                GROUP BY EXTRACT(YEAR FROM data_inclusao_fatura), EXTRACT(MONTH FROM data_inclusao_fatura)
                ORDER BY ano, mes
            """)
            
            results = connection.execute(sql_evolucao, params).fetchall()
        
        if not results:
            return jsonify({
                'success': True,
                'dados': {
                    'titulo': 'Evolução da Receita com Faturas (Data Inclusão) - Sem Dados',
                    'labels': [],
                    'valores': [],
                    'quantidades': [],
                    'ticket_medio': [],
                    'estatisticas': {
                        'total_periodo': 0.0,
                        'media_mensal': 0.0,
                        'total_ctes': 0,
                        'meses_analisados': 0
                    }
                }
            })
        
        labels = []
        valores = []
        quantidades = []
        ticket_medio_mensal = []
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for row in results:
            if row.ano and row.mes:
                mes_nome = meses_nomes[int(row.mes) - 1]
                label = f"{mes_nome}/{int(row.ano)}"
                
                labels.append(label)
                valores.append(float(row.receita_mes))
                quantidades.append(int(row.qtd_ctes))
                ticket_medio_mensal.append(float(row.ticket_medio_mes))
        
        total_periodo = sum(valores)
        media_mensal = total_periodo / len(valores) if valores else 0
        total_ctes = sum(quantidades)
        
        dados = {
            'titulo': f'Evolução da Receita com Faturas (Data Inclusão) - {len(results)} meses',
            'labels': labels,
            'valores': valores,
            'quantidades': quantidades,
            'ticket_medio': ticket_medio_mensal,
            'estatisticas': {
                'total_periodo': total_periodo,
                'media_mensal': media_mensal,
                'total_ctes': total_ctes,
                'meses_analisados': len(results)
            },
            'filtros_aplicados': {
                'cliente': filtro_cliente,
                'dias': filtro_dias,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        }
        
        logger.info(f"Evolução receita inclusão fatura: {len(labels)} meses, R$ {total_periodo:,.2f}")
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        logger.error(f"Erro na API evolução receita inclusão fatura: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# SISTEMA DE EXPORTAÇÃO
# ============================================================================

@bp.route('/api/exportar/excel')
@login_required
def exportar_excel():
    """Exporta análise completa para Excel"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        query = aplicar_filtros_base(filtro_dias, filtro_cliente, data_inicio, data_fim)
        ctes = query.all()
        
        if not ctes:
            return jsonify({'error': 'Nenhum dado para exportar'}), 400
        
        dados = []
        for cte in ctes:
            # Função helper para acessar campos com segurança
            def get_field_safe(obj, field_name, default=''):
                """Acessa campo do modelo com segurança, retornando default se não existir"""
                try:
                    return getattr(obj, field_name, default)
                except AttributeError:
                    return default
            
            # Função helper para formatar datas com segurança
            def format_date_safe(obj, field_name):
                """Formata data com segurança, retornando string vazia se campo não existir ou for None"""
                try:
                    field_value = getattr(obj, field_name, None)
                    if field_value:
                        return field_value.strftime('%d/%m/%Y')
                    return ''
                except (AttributeError, TypeError):
                    return ''
            
            # Campos básicos (sempre existem)
            row_data = {
                'Número CTE': cte.numero_cte,
                'Cliente': cte.destinatario_nome,
                'Veiculo': get_field_safe(cte, 'veiculo_placa', ''),
                'Valor Total': float(cte.valor_total or 0),
                'Data Emissão': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                'Data Baixa': cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else '',
                'Número Fatura': get_field_safe(cte, 'numero_fatura', ''),
                'Data Inclusão Fatura': format_date_safe(cte, 'data_inclusao_fatura'),
                'Status': 'Baixado' if cte.data_baixa else 'Pendente'
            }
            
            # Campos novos (podem não existir) - ADICIONAR COM SEGURANÇA
            novos_campos = {
                'Data Envio Processo': format_date_safe(cte, 'data_envio_processo'),
                'Primeiro Envio': format_date_safe(cte, 'primeiro_envio'),
                'Data Rq/TMC': format_date_safe(cte, 'data_requisicao'),
                'Data Atesto': format_date_safe(cte, 'data_atesto'),
                'Envio Final': format_date_safe(cte, 'envio_final'),
                'Observações': get_field_safe(cte, 'observacoes', '')
            }
            
            # Combinar dados básicos com novos campos
            row_data.update(novos_campos)
            dados.append(row_data)
        
        # Log para debug
        logger.info(f"Exportando {len(dados)} registros para Excel")
        
        df = pd.DataFrame(dados)
        
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Dados CTEs', index=False)
            
            # Resumo com cálculos seguros
            total_ctes = len(df)
            receita_total = df['Valor Total'].sum()
            ticket_medio = df['Valor Total'].mean() if total_ctes > 0 else 0
            ctes_baixados = len(df[df['Status'] == 'Baixado'])
            valor_baixado = df[df['Status'] == 'Baixado']['Valor Total'].sum()
            
            resumo_data = {
                'Métrica': [
                    'Total CTEs', 
                    'Receita Total', 
                    'Ticket Médio', 
                    'CTEs com Baixa', 
                    'Valor Baixado',
                    'Taxa de Baixa (%)',
                    'Período Filtro',
                    'Cliente Filtro'
                ],
                'Valor': [
                    total_ctes,
                    f'R$ {receita_total:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                    f'R$ {ticket_medio:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                    ctes_baixados,
                    f'R$ {valor_baixado:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                    f'{(ctes_baixados/total_ctes*100):,.1f}%' if total_ctes > 0 else '0%',
                    f'{filtro_dias} dias',
                    filtro_cliente or 'Todos'
                ]
            }
            resumo_df = pd.DataFrame(resumo_data)
            resumo_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Formatação
            workbook = writer.book
            money_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
            
            worksheet = writer.sheets['Dados CTEs']
            worksheet.set_column('D:D', 12, money_format)  # Coluna Valor Total
            
            # Auto-ajustar largura das colunas
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )
                worksheet.set_column(i, i, min(max_length + 2, 50))
        
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'analise_financeira_{timestamp}.xlsx'
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        # Log detalhado do erro
        import traceback
        logger.error(f"Erro na exportação Excel: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        
        # Retornar erro mais específico
        return jsonify({
            'error': f'Erro na exportação: {str(e)}',
            'details': 'Verifique se todos os campos existem no modelo CTE'
        }), 500

@bp.route('/api/exportar/json')
@login_required  
def exportar_json():
    """Exporta análise completa para JSON"""
    try:
        from flask import url_for, current_app
        
        args = dict(request.args)
        
        with current_app.test_request_context(query_string=request.query_string):
            try:
                metricas_response = api_metricas_mes_corrente()
                metricas_data = metricas_response.get_json() if hasattr(metricas_response, 'get_json') else metricas_response[0].get_json()
            except:
                metricas_data = {'success': False, 'data': {}}
            
            try:
                receita_faturada_response = api_receita_faturada()
                receita_faturada_data = receita_faturada_response.get_json() if hasattr(receita_faturada_response, 'get_json') else receita_faturada_response[0].get_json()
            except:
                receita_faturada_data = {'success': False, 'dados': {}}
            
            try:
                receita_faturas_response = api_receita_com_faturas()
                receita_faturas_data = receita_faturas_response.get_json() if hasattr(receita_faturas_response, 'get_json') else receita_faturas_response[0].get_json()
            except:
                receita_faturas_data = {'success': False, 'dados': {}}
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'filtros_aplicados': args,
            'metricas_principais': metricas_data.get('data', {}) if metricas_data.get('success') else {},
            'receita_faturada': receita_faturada_data.get('dados', {}) if receita_faturada_data.get('success') else {},
            'receita_com_faturas': receita_faturas_data.get('dados', {}) if receita_faturas_data.get('success') else {},
            'metadata': {
                'sistema': 'Dashboard Baker',
                'versao': '3.0',
                'modulo': 'Análise Financeira'
            }
        }
        
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'analise_financeira_{timestamp}.json'
        
        response = make_response(json_content)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        logger.error(f"Erro na exportação JSON: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/exportar/pdf')
@login_required
def exportar_pdf():
    """Exporta relatório em PDF"""
    try:
        from flask import current_app
        
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        
        with current_app.test_request_context(query_string=request.query_string):
            try:
                metricas_response = api_metricas_mes_corrente()
                metricas_data = metricas_response.get_json() if hasattr(metricas_response, 'get_json') else metricas_response[0].get_json()
            except:
                metricas_data = {'success': False, 'data': {}}
        
        if not metricas_data.get('success'):
            return jsonify({'error': 'Erro ao buscar dados para PDF'}), 500
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
        except ImportError:
            return jsonify({'error': 'ReportLab não instalado. Execute: pip install reportlab'}), 500
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Relatório de Análise Financeira")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        y_position = height - 120
        metricas = metricas_data.get('metricas_basicas', {})
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Métricas Principais")
        y_position -= 30
        
        c.setFont("Helvetica", 11)
        dados_relatorio = [
            f"Total de CTEs: {metricas.get('total_ctes', 0)}",
            f"Receita Total: R$ {metricas.get('receita_mes_atual', 0):,.2f}",
            f"Ticket Médio: R$ {metricas.get('ticket_medio', 0):,.2f}",
            f"CTEs com Baixa: {metricas.get('ctes_com_baixa', 0)}",
            f"Valor Baixado: R$ {metricas.get('valor_baixado', 0):,.2f}",
            f"Percentual Baixado: {metricas.get('percentual_baixado', 0):.1f}%"
        ]
        
        for linha in dados_relatorio:
            c.drawString(50, y_position, linha)
            y_position -= 20
        
        receita_faturada = metricas_data.get('receita_faturada', {})
        if receita_faturada:
            y_position -= 20
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "Receita Faturada")
            y_position -= 25
            
            c.setFont("Helvetica", 11)
            c.drawString(50, y_position, f"Valor: R$ {receita_faturada.get('receita_total', 0):,.2f}")
            y_position -= 20
            c.drawString(50, y_position, f"CTEs: {receita_faturada.get('quantidade_ctes', 0)}")
            y_position -= 20
            c.drawString(50, y_position, f"Percentual: {receita_faturada.get('percentual_total', 0):.1f}%")
        
        receita_faturas = metricas_data.get('receita_com_faturas', {})
        if receita_faturas:
            y_position -= 30
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "Receita com Faturas")
            y_position -= 25
            
            c.setFont("Helvetica", 11)
            c.drawString(50, y_position, f"Valor: R$ {receita_faturas.get('receita_total', 0):,.2f}")
            y_position -= 20
            c.drawString(50, y_position, f"CTEs: {receita_faturas.get('quantidade_ctes', 0)}")
            y_position -= 20
            c.drawString(50, y_position, f"Cobertura: {receita_faturas.get('percentual_cobertura', 0):.1f}%")
        
        c.setFont("Helvetica", 9)
        c.drawString(50, 50, "Dashboard Baker - Sistema de Análise Financeira")
        c.drawString(400, 50, f"Página 1 de 1")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'relatorio_financeiro_{timestamp}.pdf'
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erro na exportação PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# APIS AUXILIARES E COMPATIBILIDADE
# ============================================================================

@bp.route('/api/clientes')
@login_required
def api_clientes():
    """API para lista de clientes"""
    try:
        data_limite = datetime.now().date() - timedelta(days=180)
        
        with db.engine.connect() as connection:
            sql = text("""
                SELECT 
                    destinatario_nome,
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                AND destinatario_nome IS NOT NULL
                AND destinatario_nome != ''
                GROUP BY destinatario_nome
                ORDER BY receita_total DESC
                LIMIT 50
            """)
            
            result = connection.execute(sql, {"data_limite": data_limite}).fetchall()
            
            clientes = []
            for row in result:
                clientes.append(row.destinatario_nome)
            
            logger.info(f"Lista de clientes carregada: {len(clientes)} clientes")
            
            return jsonify({
                'success': True,
                'clientes': clientes
            })
        
    except Exception as e:
        logger.error(f"Erro na API clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/analise-completa')
@login_required
def api_analise_completa():
    """API para análise financeira completa - COMPATIBILIDADE"""
    try:
        return api_metricas_mes_corrente()
        
    except Exception as e:
        logger.error(f"Erro na análise completa: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/diagnostico-completo')
@login_required
def api_diagnostico_completo():
    """API de diagnóstico completo do sistema"""
    try:
        diagnostico = {}
        
        with db.engine.connect() as connection:
            total_ctes = connection.execute(text('SELECT COUNT(*) FROM dashboard_baker')).scalar()
            diagnostico['total_ctes'] = total_ctes
            
            agora = datetime.now()
            primeiro_dia = agora.replace(day=1).date()
            
            sql_diagnostico = text("""
                SELECT 
                    COUNT(*) as total_mes,
                    SUM(valor_total) as receita_mes,
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as com_envio_final,
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as com_inclusao_fatura,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as com_numero_fatura,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa,
                    COUNT(CASE WHEN primeiro_envio IS NOT NULL THEN 1 END) as com_primeiro_envio
                FROM dashboard_baker 
                WHERE data_emissao >= :primeiro_dia
            """)
            
            result = connection.execute(sql_diagnostico, {"primeiro_dia": primeiro_dia}).fetchone()
            
            diagnostico['mes_corrente'] = {
                'total_ctes': int(result.total_mes),
                'receita_total': float(result.receita_mes or 0),
                'com_envio_final': int(result.com_envio_final),
                'com_inclusao_fatura': int(result.com_inclusao_fatura),
                'com_numero_fatura': int(result.com_numero_fatura),
                'com_baixa': int(result.com_baixa),
                'com_primeiro_envio': int(result.com_primeiro_envio)
            }
            
            diagnostico['status_campos'] = {
                'envio_final': 'OK' if result.com_envio_final > 0 else 'VAZIO',
                'data_inclusao_fatura': 'OK' if result.com_inclusao_fatura > 0 else 'VAZIO',
                'data_baixa': 'OK' if result.com_baixa > 0 else 'VAZIO',
                'primeiro_envio': 'OK' if result.com_primeiro_envio > 0 else 'VAZIO'
            }
        
        diagnostico['apis_funcionais'] = True
        diagnostico['sistema_exportacao'] = 'Ativo'
        
        return jsonify({
            'success': True,
            'diagnostico': diagnostico,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# SUBSTITUIR AS APIs QUE ADICIONEI ANTERIORMENTE POR ESTAS VERSÕES CORRIGIDAS
# NO ARQUIVO app/routes/analise_financeira.py

@bp.route('/api/debug/base-dados')
@login_required
def api_debug_base_dados():
    """API de diagnóstico da base de dados - VERSÃO SIMPLES"""
    try:
        diagnostico = {
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Usar query simples do SQLAlchemy
        total_registros = CTE.query.count()
        diagnostico['total_registros_tabela'] = total_registros
        
        # Registros recentes
        data_limite = datetime.now().date() - timedelta(days=180)
        registros_recentes = CTE.query.filter(CTE.data_emissao >= data_limite).count()
        diagnostico['registros_ultimos_180_dias'] = registros_recentes
        
        # Verificar alguns campos básicos
        ctes_com_valor = CTE.query.filter(
            CTE.data_emissao >= data_limite,
            CTE.valor_total.isnot(None),
            CTE.valor_total > 0
        ).count()
        
        ctes_com_cliente = CTE.query.filter(
            CTE.data_emissao >= data_limite,
            CTE.destinatario_nome.isnot(None),
            CTE.destinatario_nome != ''
        ).count()
        
        diagnostico['campos_preenchidos'] = {
            'com_valor_total': ctes_com_valor,
            'com_destinatario': ctes_com_cliente,
            'com_data_baixa': CTE.query.filter(CTE.data_emissao >= data_limite, CTE.data_baixa.isnot(None)).count(),
            'com_numero_fatura': CTE.query.filter(CTE.data_emissao >= data_limite, CTE.numero_fatura.isnot(None)).count(),
            'com_data_inclusao_fatura': CTE.query.filter(CTE.data_emissao >= data_limite, CTE.data_inclusao_fatura.isnot(None)).count()
        }
        
        # Identificar problemas básicos
        problemas = []
        recomendacoes = []
        
        if total_registros == 0:
            problemas.append("Tabela dashboard_baker vazia")
            recomendacoes.append("Importar dados de CTEs")
        elif registros_recentes == 0:
            problemas.append("Nenhum CTE nos últimos 180 dias")
            recomendacoes.append("Verificar datas de emissão dos CTEs")
        elif ctes_com_valor == 0:
            problemas.append("Campo valor_total vazio em todos os registros")
            recomendacoes.append("Preencher campo valor_total")
        elif ctes_com_cliente == 0:
            problemas.append("Campo destinatario_nome vazio")
            recomendacoes.append("Preencher campo destinatario_nome")
        
        diagnostico['problemas_identificados'] = problemas
        diagnostico['recomendacoes'] = recomendacoes
        
        return jsonify({'success': True, 'diagnostico': diagnostico})
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'diagnostico': {
                'total_registros_tabela': 0,
                'registros_ultimos_180_dias': 0,
                'problemas_identificados': [f'Erro de conexão: {str(e)}']
            }
        }), 500

@bp.route('/api/metricas-forcadas')
@login_required
def api_metricas_forcadas():
    """API que força métricas mesmo com dados limitados - VERSÃO SIMPLES"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Aplicar filtros usando SQLAlchemy ORM (mais seguro)
        query = CTE.query
        
        if data_inicio and data_fim:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao.between(data_inicio_obj, data_fim_obj))
            except:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                query = query.filter(CTE.data_emissao >= data_limite)
        else:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            query = query.filter(CTE.data_emissao >= data_limite)
        
        if filtro_cliente:
            query = query.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
        
        # Buscar todos os CTEs que atendem aos filtros
        ctes = query.all()
        
        if not ctes:
            # Retornar dados zerados quando não há dados
            return jsonify({
                'success': True,
                'metricas_basicas': {
                    'receita_mes_atual': 0.0,
                    'total_ctes': 0,
                    'ticket_medio': 0.0
                },
                'receita_faturada': {
                    'receita_total': 0.0,
                    'quantidade_ctes': 0,
                    'percentual_total': 0.0
                },
                'receita_com_faturas': {
                    'receita_total': 0.0,
                    'quantidade_ctes': 0,
                    'percentual_cobertura': 0.0
                },
                'status_sistema': {
                    'total_registros': 0,
                    'taxa_faturamento': 0.0,
                    'taxa_com_faturas': 0.0,
                    'tempo_medio_cobranca': 0.0,
                    'concentracao_top5': 0.0,
                    'impacto_top_cliente': 0.0
                },
                'top_clientes': [],
                'debug_info': {
                    'dados_encontrados': False,
                    'total_registros_query': 0,
                    'filtros_aplicados': {
                        'cliente': filtro_cliente,
                        'dias': filtro_dias,
                        'data_inicio': data_inicio,
                        'data_fim': data_fim
                    }
                }
            })
        
        # Calcular métricas básicas
        total_ctes = len(ctes)
        receita_total = sum(float(cte.valor_total or 0) for cte in ctes)
        ticket_medio = receita_total / total_ctes if total_ctes > 0 else 0
        
        # Calcular receita faturada (com fallbacks)
        ctes_faturados = 0
        receita_faturada = 0.0
        
        for cte in ctes:
            if (cte.envio_final is not None or 
                cte.data_baixa is not None or 
                (cte.numero_fatura and cte.numero_fatura.strip())):
                ctes_faturados += 1
                receita_faturada += float(cte.valor_total or 0)
        
        # Calcular receita com faturas
        ctes_com_faturas = 0
        receita_com_faturas_valor = 0.0
        
        for cte in ctes:
            if (cte.data_inclusao_fatura is not None or 
                (cte.numero_fatura and cte.numero_fatura.strip())):
                ctes_com_faturas += 1
                receita_com_faturas_valor += float(cte.valor_total or 0)
        
        # Calcular baixas
        ctes_baixados = sum(1 for cte in ctes if cte.data_baixa is not None)
        valor_baixado = sum(float(cte.valor_total or 0) for cte in ctes if cte.data_baixa is not None)
        
        # Calcular tempo médio de cobrança (aproximado)
        tempos_cobranca = []
        for cte in ctes:
            if cte.data_baixa and cte.data_emissao:
                dias = (cte.data_baixa - cte.data_emissao).days
                if dias >= 0:
                    tempos_cobranca.append(dias)
        
        tempo_medio_cobranca = sum(tempos_cobranca) / len(tempos_cobranca) if tempos_cobranca else 0
        
        # Calcular percentuais
        taxa_faturamento = (receita_faturada / receita_total * 100) if receita_total > 0 else 0
        taxa_com_faturas = (ctes_com_faturas / total_ctes * 100) if total_ctes > 0 else 0
        
        # Top 5 clientes
        clientes_receita = {}
        for cte in ctes:
            if cte.destinatario_nome and cte.destinatario_nome.strip():
                nome = cte.destinatario_nome.strip()
                if nome not in clientes_receita:
                    clientes_receita[nome] = 0.0
                clientes_receita[nome] += float(cte.valor_total or 0)
        
        # Ordenar por receita
        top_clientes_sorted = sorted(clientes_receita.items(), key=lambda x: x[1], reverse=True)[:5]
        
        top_clientes = []
        receita_top5 = 0
        
        for i, (nome, receita_cliente) in enumerate(top_clientes_sorted):
            receita_top5 += receita_cliente
            percentual = (receita_cliente / receita_total * 100) if receita_total > 0 else 0
            
            risco = 'Baixo Risco'
            classe_risco = 'success'
            if percentual >= 40:
                risco = 'Alto Risco'
                classe_risco = 'danger'
            elif percentual >= 25:
                risco = 'Médio Risco'
                classe_risco = 'warning'
            
            top_clientes.append({
                'posicao': i + 1,
                'nome': nome,
                'receita': receita_cliente,
                'percentual': percentual,
                'risco': risco,
                'classe_risco': classe_risco
            })
        
        concentracao_top5 = (receita_top5 / receita_total * 100) if receita_total > 0 else 0
        impacto_top_cliente = top_clientes[0]['percentual'] if top_clientes else 0
        
        resultado = {
            'success': True,
            'metricas_basicas': {
                'receita_mes_atual': receita_total,
                'total_ctes': total_ctes,
                'ticket_medio': ticket_medio
            },
            'receita_faturada': {
                'receita_total': receita_faturada,
                'quantidade_ctes': ctes_faturados,
                'percentual_total': taxa_faturamento
            },
            'receita_com_faturas': {
                'receita_total': receita_com_faturas_valor,
                'quantidade_ctes': ctes_com_faturas,
                'percentual_cobertura': taxa_com_faturas
            },
            'status_sistema': {
                'total_registros': total_ctes,
                'taxa_faturamento': taxa_faturamento,
                'taxa_com_faturas': taxa_com_faturas,
                'tempo_medio_cobranca': tempo_medio_cobranca,
                'concentracao_top5': concentracao_top5,
                'impacto_top_cliente': impacto_top_cliente
            },
            'top_clientes': top_clientes,
            'debug_info': {
                'dados_encontrados': True,
                'total_registros_query': total_ctes,
                'receita_total_query': receita_total,
                'metodo_usado': 'SQLAlchemy ORM (seguro)',
                'filtros_aplicados': {
                    'cliente': filtro_cliente,
                    'dias': filtro_dias,
                    'data_inicio': data_inicio,
                    'data_fim': data_fim
                }
            }
        }
        
        logger.info(f"Métricas forçadas calculadas: {total_ctes} CTEs, R$ {receita_total:,.2f}")
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro nas métricas forçadas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'metricas_basicas': {'receita_mes_atual': 0, 'total_ctes': 0, 'ticket_medio': 0},
            'receita_faturada': {'receita_total': 0, 'quantidade_ctes': 0, 'percentual_total': 0},
            'receita_com_faturas': {'receita_total': 0, 'quantidade_ctes': 0, 'percentual_cobertura': 0},
            'status_sistema': {'total_registros': 0, 'taxa_faturamento': 0, 'taxa_com_faturas': 0, 'tempo_medio_cobranca': 0, 'concentracao_top5': 0, 'impacto_top_cliente': 0},
            'top_clientes': []
        }), 500

@bp.route('/api/graficos-simples')
@login_required
def api_graficos_simples():
    """API para gráficos básicos funcionais - VERSÃO SIMPLES"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Aplicar filtros
        query = CTE.query
        
        if data_inicio and data_fim:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao.between(data_inicio_obj, data_fim_obj))
            except:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                query = query.filter(CTE.data_emissao >= data_limite)
        else:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            query = query.filter(CTE.data_emissao >= data_limite)
        
        if filtro_cliente:
            query = query.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
        
        # Filtrar apenas CTEs com valor
        query = query.filter(CTE.valor_total.isnot(None), CTE.valor_total > 0)
        ctes = query.all()
        
        if not ctes:
            # Retornar gráficos vazios mas funcionais
            return jsonify({
                'success': True,
                'graficos': {
                    'receita_mensal': {
                        'labels': ['Jan/2024', 'Fev/2024', 'Mar/2024', 'Abr/2024', 'Mai/2024', 'Jun/2024'],
                        'valores': [0, 0, 0, 0, 0, 0],
                        'quantidades': [0, 0, 0, 0, 0, 0]
                    },
                    'concentracao_clientes': {
                        'labels': ['Aguardando dados'],
                        'valores': [1]
                    },
                    'tendencia_linear': {
                        'labels': ['Jan/2024', 'Fev/2024', 'Mar/2024', 'Abr/2024', 'Mai/2024', 'Jun/2024'],
                        'valores_reais': [0, 0, 0, 0, 0, 0]
                    },
                    'tempo_cobranca': {
                        'labels': ['0-30 dias', '31-60 dias', '61-90 dias', '90+ dias'],
                        'valores': [0, 0, 0, 0]
                    }
                }
            })
        
        # 1. RECEITA MENSAL - agrupar por mês/ano
        receita_mensal = {}
        for cte in ctes:
            if cte.data_emissao:
                chave = f"{cte.data_emissao.year}-{cte.data_emissao.month:02d}"
                if chave not in receita_mensal:
                    receita_mensal[chave] = {'receita': 0.0, 'qtd': 0}
                receita_mensal[chave]['receita'] += float(cte.valor_total or 0)
                receita_mensal[chave]['qtd'] += 1
        
        # Ordenar e formatar
        meses_ordenados = sorted(receita_mensal.keys())[-12:]  # Últimos 12 meses
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        receita_labels = []
        receita_valores = []
        receita_quantidades = []
        
        for chave in meses_ordenados:
            ano, mes = chave.split('-')
            mes_nome = meses_nomes[int(mes) - 1]
            receita_labels.append(f"{mes_nome}/{ano}")
            receita_valores.append(receita_mensal[chave]['receita'])
            receita_quantidades.append(receita_mensal[chave]['qtd'])
        
        # Se não tem dados suficientes, criar pelo menos alguns meses
        if len(receita_labels) == 0:
            hoje = datetime.now()
            for i in range(6):
                mes_data = hoje - timedelta(days=i*30)
                mes_nome = meses_nomes[mes_data.month - 1]
                receita_labels.insert(0, f"{mes_nome}/{mes_data.year}")
                receita_valores.insert(0, 0)
                receita_quantidades.insert(0, 0)
        
        # 2. CONCENTRAÇÃO DE CLIENTES - top 6
        clientes_receita = {}
        for cte in ctes:
            if cte.destinatario_nome and cte.destinatario_nome.strip():
                nome = cte.destinatario_nome.strip()
                if nome not in clientes_receita:
                    clientes_receita[nome] = 0.0
                clientes_receita[nome] += float(cte.valor_total or 0)
        
        # Pegar top 6 clientes
        top_clientes_sorted = sorted(clientes_receita.items(), key=lambda x: x[1], reverse=True)[:6]
        
        concentracao_labels = []
        concentracao_valores = []
        
        for nome, receita in top_clientes_sorted:
            nome_curto = nome[:25] + "..." if len(nome) > 25 else nome
            concentracao_labels.append(nome_curto)
            concentracao_valores.append(receita)
        
        if not concentracao_labels:
            concentracao_labels = ['Aguardando dados']
            concentracao_valores = [1]
        
        # 3. TEMPO DE COBRANÇA - distribuição aproximada
        tempo_cobranca = {'0-30 dias': 0, '31-60 dias': 0, '61-90 dias': 0, '90+ dias': 0}
        
        for cte in ctes:
            if cte.data_baixa and cte.data_emissao:
                dias = (cte.data_baixa - cte.data_emissao).days
                if dias <= 30:
                    tempo_cobranca['0-30 dias'] += 1
                elif dias <= 60:
                    tempo_cobranca['31-60 dias'] += 1
                elif dias <= 90:
                    tempo_cobranca['61-90 dias'] += 1
                else:
                    tempo_cobranca['90+ dias'] += 1
            else:
                tempo_cobranca['90+ dias'] += 1
        
        tempo_labels = list(tempo_cobranca.keys())
        tempo_valores = list(tempo_cobranca.values())
        
        # 4. TENDÊNCIA - usar receita mensal como base
        tendencia_labels = receita_labels.copy()
        tendencia_valores_reais = receita_valores.copy()
        
        graficos = {
            'receita_mensal': {
                'labels': receita_labels,
                'valores': receita_valores,
                'quantidades': receita_quantidades
            },
            'concentracao_clientes': {
                'labels': concentracao_labels,
                'valores': concentracao_valores
            },
            'tendencia_linear': {
                'labels': tendencia_labels,
                'valores_reais': tendencia_valores_reais
            },
            'tempo_cobranca': {
                'labels': tempo_labels,
                'valores': tempo_valores
            }
        }
        
        logger.info(f"Gráficos simples calculados: {len(ctes)} CTEs, {len(receita_labels)} meses")
        
        return jsonify({
            'success': True,
            'graficos': graficos
        })
        
    except Exception as e:
        logger.error(f"Erro nos gráficos simples: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'graficos': {
                'receita_mensal': {'labels': ['Erro'], 'valores': [0], 'quantidades': [0]},
                'concentracao_clientes': {'labels': ['Erro'], 'valores': [1]},
                'tendencia_linear': {'labels': ['Erro'], 'valores_reais': [0]},
                'tempo_cobranca': {'labels': ['0-30 dias', '31-60 dias', '61-90 dias', '90+ dias'], 'valores': [0, 0, 0, 0]}
            }
        }), 500

@bp.route('/api/top-clientes')
@login_required  
def api_top_clientes():
    """API para top clientes - VERSÃO SIMPLES"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Aplicar filtros
        query = CTE.query
        
        if data_inicio and data_fim:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao.between(data_inicio_obj, data_fim_obj))
            except:
                data_limite = datetime.now().date() - timedelta(days=filtro_dias)
                query = query.filter(CTE.data_emissao >= data_limite)
        else:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            query = query.filter(CTE.data_emissao >= data_limite)
        
        if filtro_cliente:
            query = query.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
        
        # Buscar CTEs com cliente e valor
        query = query.filter(
            CTE.destinatario_nome.isnot(None),
            CTE.destinatario_nome != '',
            CTE.valor_total.isnot(None),
            CTE.valor_total > 0
        )
        
        ctes = query.all()
        
        if not ctes:
            return jsonify({
                'success': True,
                'top_clientes': []
            })
        
        # Agrupar por cliente
        clientes_dados = {}
        receita_total_geral = 0
        
        for cte in ctes:
            nome = cte.destinatario_nome.strip()
            receita = float(cte.valor_total or 0)
            receita_total_geral += receita
            
            if nome not in clientes_dados:
                clientes_dados[nome] = {'receita': 0.0, 'qtd': 0}
            
            clientes_dados[nome]['receita'] += receita
            clientes_dados[nome]['qtd'] += 1
        
        # Ordenar por receita
        clientes_ordenados = sorted(clientes_dados.items(), key=lambda x: x[1]['receita'], reverse=True)
        
        # Pegar top 10
        top_clientes = []
        
        for i, (nome, dados) in enumerate(clientes_ordenados[:10]):
            receita_cliente = dados['receita']
            percentual = (receita_cliente / receita_total_geral * 100) if receita_total_geral > 0 else 0
            
            risco = 'Baixo Risco'
            classe_risco = 'success'
            if percentual >= 40:
                risco = 'Alto Risco'
                classe_risco = 'danger'
            elif percentual >= 25:
                risco = 'Médio Risco'
                classe_risco = 'warning'
            
            top_clientes.append({
                'posicao': i + 1,
                'nome': nome,
                'receita': receita_cliente,
                'percentual': percentual,
                'qtd_ctes': dados['qtd'],
                'risco': risco,
                'classe_risco': classe_risco
            })
        
        return jsonify({
            'success': True,
            'top_clientes': top_clientes,
            'receita_total_base': receita_total_geral
        })
        
    except Exception as e:
        logger.error(f"Erro no top clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'top_clientes': []
        }), 500

@bp.route('/api/stress-test')
@login_required
def api_stress_test():
    """API para stress test - VERSÃO SIMPLES"""
    try:
        # Buscar top cliente para calcular impacto
        filtro_dias = int(request.args.get('filtro_dias', 180))
        data_limite = datetime.now().date() - timedelta(days=filtro_dias)
        
        # Buscar receita por cliente
        query = CTE.query.filter(
            CTE.data_emissao >= data_limite,
            CTE.destinatario_nome.isnot(None),
            CTE.destinatario_nome != '',
            CTE.valor_total.isnot(None),
            CTE.valor_total > 0
        )
        
        ctes = query.all()
        
        if not ctes:
            return jsonify({
                'success': True,
                'cenarios': [],
                'receita_total': 0
            })
        
        # Agrupar por cliente
        clientes_receita = {}
        receita_total = 0
        
        for cte in ctes:
            nome = cte.destinatario_nome.strip()
            receita = float(cte.valor_total or 0)
            receita_total += receita
            
            if nome not in clientes_receita:
                clientes_receita[nome] = 0.0
            clientes_receita[nome] += receita
        
        # Ordenar clientes por receita
        clientes_ordenados = sorted(clientes_receita.items(), key=lambda x: x[1], reverse=True)
        
        # Criar cenários de stress test
        cenarios = []
        
        if len(clientes_ordenados) > 0:
            # Cenário 1: Perda do top cliente
            top_cliente_receita = clientes_ordenados[0][1]
            impacto_top = (top_cliente_receita / receita_total * 100) if receita_total > 0 else 0
            
            cenarios.append({
                'cenario': 'Perda do Top Cliente',
                'icon': '⚠️',
                'receita_perdida': top_cliente_receita,
                'percentual_impacto': impacto_top,
                'receita_restante': receita_total - top_cliente_receita,
                'descricao': f'Impacto da perda de {clientes_ordenados[0][0]}'
            })
        
        if len(clientes_ordenados) >= 3:
            # Cenário 2: Perda dos top 3 clientes
            top3_receita = sum(cliente[1] for cliente in clientes_ordenados[:3])
            impacto_top3 = (top3_receita / receita_total * 100) if receita_total > 0 else 0
            
            cenarios.append({
                'cenario': 'Perda Top 3 Clientes',
                'icon': '🚨',
                'receita_perdida': top3_receita,
                'percentual_impacto': impacto_top3,
                'receita_restante': receita_total - top3_receita,
                'descricao': 'Cenário de maior risco'
            })
        
        # Cenário 3: Redução geral de 20%
        reducao_20 = receita_total * 0.20
        cenarios.append({
            'cenario': 'Redução Geral 20%',
            'icon': '📉',
            'receita_perdida': reducao_20,
            'percentual_impacto': 20.0,
            'receita_restante': receita_total - reducao_20,
            'descricao': 'Cenário de crise moderada'
        })
        
        return jsonify({
            'success': True,
            'cenarios': cenarios,
            'receita_total': receita_total
        })
        
    except Exception as e:
        logger.error(f"Erro no stress test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'cenarios': [],
            'receita_total': 0
        }), 500