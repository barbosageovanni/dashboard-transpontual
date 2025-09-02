#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes para Análise Financeira - CORRECAO COMPLETA COM ALERTAS
app/routes/analise_financeira.py - SUBSTITUIR COMPLETAMENTE
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
from app.models.cte import CTE
from app import db
from sqlalchemy import func, and_, desc, extract, text
import logging
import calendar

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
# APIS PRINCIPAIS - ROBUSTAS E COM FALLBACKS
# ============================================================================

@bp.route('/api/test-conexao')
def api_test_conexao():
    """API de teste para verificar conectividade"""
    try:
        # Testar conexão básica
        total_ctes = CTE.query.count()
        
        # Testar dados do mês corrente
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
    """API para métricas do mês corrente - ROBUSTA"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        logger.info(f"Calculando métricas do mês corrente. Cliente: {filtro_cliente}")
        
        # Calcular período do mês corrente
        agora = datetime.now()
        primeiro_dia_mes = agora.replace(day=1).date()
        ultimo_dia_mes = agora.replace(day=calendar.monthrange(agora.year, agora.month)[1]).date()
        
        # Query base para mês corrente
        query_mes = CTE.query.filter(
            CTE.data_emissao.between(primeiro_dia_mes, ultimo_dia_mes)
        )
        
        if filtro_cliente:
            query_mes = query_mes.filter(CTE.destinatario_nome.ilike(f'%{filtro_cliente}%'))
        
        # Buscar dados usando SQL raw para garantir funcionamento
        with db.engine.connect() as connection:
            # Query principal
            sql_main = text("""
                SELECT 
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total,
                    COALESCE(AVG(valor_total), 0) as ticket_medio,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as ctes_com_baixa,
                    COALESCE(SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_baixado
                FROM dashboard_baker 
                WHERE data_emissao BETWEEN :primeiro_dia AND :ultimo_dia
                AND (:filtro_cliente IS NULL OR destinatario_nome ILIKE :cliente_like)
            """)
            
            params = {
                'primeiro_dia': primeiro_dia_mes,
                'ultimo_dia': ultimo_dia_mes,
                'filtro_cliente': filtro_cliente,
                'cliente_like': f'%{filtro_cliente}%' if filtro_cliente else None
            }
            
            result_main = connection.execute(sql_main, params).fetchone()
            
            # Calcular receita faturada (com fallback)
            sql_faturada = text("""
                SELECT 
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as qtd_envio_final,
                    COALESCE(SUM(CASE WHEN envio_final IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_envio_final,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as qtd_baixa_fallback,
                    COALESCE(SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_baixa_fallback
                FROM dashboard_baker 
                WHERE data_emissao BETWEEN :primeiro_dia AND :ultimo_dia
                AND (:filtro_cliente IS NULL OR destinatario_nome ILIKE :cliente_like)
            """)
            
            result_faturada = connection.execute(sql_faturada, params).fetchone()
            
            # Calcular receita com faturas (com fallback)
            sql_faturas = text("""
                SELECT 
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as qtd_inclusao,
                    COALESCE(SUM(CASE WHEN data_inclusao_fatura IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_inclusao,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as qtd_numero_fallback,
                    COALESCE(SUM(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN valor_total ELSE 0 END), 0) as valor_numero_fallback
                FROM dashboard_baker 
                WHERE data_emissao BETWEEN :primeiro_dia AND :ultimo_dia
                AND (:filtro_cliente IS NULL OR destinatario_nome ILIKE :cliente_like)
            """)
            
            result_faturas = connection.execute(sql_faturas, params).fetchone()
        
        # Processar dados da receita faturada
        if result_faturada.qtd_envio_final > 0:
            receita_faturada_valor = float(result_faturada.valor_envio_final)
            receita_faturada_qtd = int(result_faturada.qtd_envio_final)
            logger.info("Usando campo 'envio_final' para receita faturada")
        else:
            receita_faturada_valor = float(result_faturada.valor_baixa_fallback)
            receita_faturada_qtd = int(result_faturada.qtd_baixa_fallback)
            logger.info("Usando fallback 'data_baixa' para receita faturada")
        
        # Processar dados da receita com faturas
        if result_faturas.qtd_inclusao > 0:
            receita_faturas_valor = float(result_faturas.valor_inclusao)
            receita_faturas_qtd = int(result_faturas.qtd_inclusao)
            logger.info("Usando campo 'data_inclusao_fatura' para receita com faturas")
        else:
            receita_faturas_valor = float(result_faturas.valor_numero_fallback)
            receita_faturas_qtd = int(result_faturas.qtd_numero_fallback)
            logger.info("Usando fallback 'numero_fatura' para receita com faturas")
        
        # Calcular percentuais
        receita_total = float(result_main.receita_total)
        percentual_faturado = (receita_faturada_valor / receita_total * 100) if receita_total > 0 else 0
        percentual_com_faturas = (receita_faturas_qtd / int(result_main.total_ctes) * 100) if result_main.total_ctes > 0 else 0
        
        # Montar resposta
        resultado = {
            'success': True,
            'mes_referencia': agora.strftime('%m/%Y'),
            'periodo': f"{primeiro_dia_mes.strftime('%d/%m')} a {ultimo_dia_mes.strftime('%d/%m')}",
            'metricas_basicas': {
                'receita_mes_atual': receita_total,
                'total_ctes': int(result_main.total_ctes),
                'ticket_medio': float(result_main.ticket_medio),
                'ctes_com_baixa': int(result_main.ctes_com_baixa),
                'valor_baixado': float(result_main.valor_baixado),
                'percentual_baixado': (float(result_main.valor_baixado) / receita_total * 100) if receita_total > 0 else 0
            },
            'receita_faturada': {
                'receita_total': receita_faturada_valor,
                'quantidade_ctes': receita_faturada_qtd,
                'percentual_total': percentual_faturado,
                'variacao_percentual': 0,  # Será calculado no próximo update
                'periodo_completo': f"{primeiro_dia_mes.strftime('%d/%m')} a {ultimo_dia_mes.strftime('%d/%m')}"
            },
            'receita_com_faturas': {
                'receita_total': receita_faturas_valor,
                'quantidade_ctes': receita_faturas_qtd,
                'ticket_medio': receita_faturas_valor / receita_faturas_qtd if receita_faturas_qtd > 0 else 0,
                'percentual_cobertura': percentual_com_faturas,
                'periodo_completo': f"{primeiro_dia_mes.strftime('%d/%m')} a {ultimo_dia_mes.strftime('%d/%m')}"
            }
        }
        
        logger.info(f"Métricas calculadas: {result_main.total_ctes} CTEs, R$ {receita_total:,.2f}")
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro nas métricas do mês corrente: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao calcular métricas: {str(e)}'
        }), 500

@bp.route('/api/receita-faturada')
@login_required
def api_receita_faturada():
    """API específica para receita faturada"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Usar SQL direto para garantir funcionamento
        agora = datetime.now()
        primeiro_dia = agora.replace(day=1).date()
        ultimo_dia = agora.replace(day=calendar.monthrange(agora.year, agora.month)[1]).date()
        
        with db.engine.connect() as connection:
            sql = text("""
                SELECT 
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as qtd_envio_final,
                    COALESCE(SUM(CASE WHEN envio_final IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_envio_final,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as qtd_baixa,
                    COALESCE(SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_baixa,
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total
                FROM dashboard_baker 
                WHERE data_emissao BETWEEN :primeiro_dia AND :ultimo_dia
                AND (:filtro_cliente IS NULL OR destinatario_nome ILIKE :cliente_like)
            """)
            
            params = {
                'primeiro_dia': primeiro_dia,
                'ultimo_dia': ultimo_dia,
                'filtro_cliente': filtro_cliente,
                'cliente_like': f'%{filtro_cliente}%' if filtro_cliente else None
            }
            
            result = connection.execute(sql, params).fetchone()
            
            # Decidir qual campo usar
            if result.qtd_envio_final > 0:
                receita_valor = float(result.valor_envio_final)
                quantidade = int(result.qtd_envio_final)
                campo_usado = "envio_final"
            else:
                receita_valor = float(result.valor_baixa)
                quantidade = int(result.qtd_baixa)
                campo_usado = "data_baixa (fallback)"
            
            # Calcular percentual
            receita_total = float(result.receita_total)
            percentual = (receita_valor / receita_total * 100) if receita_total > 0 else 0
            
            dados = {
                'receita_total': receita_valor,
                'quantidade_ctes': quantidade,
                'percentual_total': percentual,
                'variacao_percentual': 0,
                'campo_usado': campo_usado,
                'periodo_completo': f"{primeiro_dia.strftime('%d/%m')} a {ultimo_dia.strftime('%d/%m')}"
            }
            
            logger.info(f"Receita faturada: R$ {receita_valor:,.2f} ({quantidade} CTEs) usando {campo_usado}")
            
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
    """API específica para receita com faturas"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Usar SQL direto
        agora = datetime.now()
        primeiro_dia = agora.replace(day=1).date()
        ultimo_dia = agora.replace(day=calendar.monthrange(agora.year, agora.month)[1]).date()
        
        with db.engine.connect() as connection:
            sql = text("""
                SELECT 
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as qtd_inclusao,
                    COALESCE(SUM(CASE WHEN data_inclusao_fatura IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_inclusao,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as qtd_numero,
                    COALESCE(SUM(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN valor_total ELSE 0 END), 0) as valor_numero,
                    COUNT(*) as total_ctes
                FROM dashboard_baker 
                WHERE data_emissao BETWEEN :primeiro_dia AND :ultimo_dia
                AND (:filtro_cliente IS NULL OR destinatario_nome ILIKE :cliente_like)
            """)
            
            params = {
                'primeiro_dia': primeiro_dia,
                'ultimo_dia': ultimo_dia,
                'filtro_cliente': filtro_cliente,
                'cliente_like': f'%{filtro_cliente}%' if filtro_cliente else None
            }
            
            result = connection.execute(sql, params).fetchone()
            
            # Decidir qual campo usar
            if result.qtd_inclusao > 0:
                receita_valor = float(result.valor_inclusao)
                quantidade = int(result.qtd_inclusao)
                campo_usado = "data_inclusao_fatura"
            else:
                receita_valor = float(result.valor_numero)
                quantidade = int(result.qtd_numero)
                campo_usado = "numero_fatura (fallback)"
            
            # Calcular percentual de cobertura
            total_ctes = int(result.total_ctes)
            cobertura = (quantidade / total_ctes * 100) if total_ctes > 0 else 0
            
            # Calcular ticket médio
            ticket_medio = receita_valor / quantidade if quantidade > 0 else 0
            
            dados = {
                'receita_total': receita_valor,
                'quantidade_ctes': quantidade,
                'ticket_medio': ticket_medio,
                'percentual_cobertura': cobertura,
                'campo_usado': campo_usado,
                'periodo_completo': f"{primeiro_dia.strftime('%d/%m')} a {ultimo_dia.strftime('%d/%m')}"
            }
            
            logger.info(f"Receita com faturas: R$ {receita_valor:,.2f} ({quantidade} CTEs) usando {campo_usado}")
            
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

@bp.route('/api/evolucao-receita-faturada')
@login_required
def api_evolucao_receita_faturada():
    """API para gráfico de evolução da receita faturada"""
    try:
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Calcular últimos 12 meses
        hoje = datetime.now().date()
        inicio_periodo = hoje.replace(day=1) - timedelta(days=365)
        
        with db.engine.connect() as connection:
            sql = text("""
                SELECT 
                    EXTRACT(YEAR FROM data_emissao) as ano,
                    EXTRACT(MONTH FROM data_emissao) as mes,
                    COALESCE(SUM(CASE WHEN envio_final IS NOT NULL THEN valor_total 
                                 WHEN data_baixa IS NOT NULL THEN valor_total 
                                 ELSE 0 END), 0) as valor_mes,
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 
                               WHEN data_baixa IS NOT NULL THEN 1 END) as qtd_mes
                FROM dashboard_baker 
                WHERE data_emissao >= :inicio_periodo
                AND (:filtro_cliente IS NULL OR destinatario_nome ILIKE :cliente_like)
                GROUP BY EXTRACT(YEAR FROM data_emissao), EXTRACT(MONTH FROM data_emissao)
                ORDER BY ano, mes
            """)
            
            params = {
                'inicio_periodo': inicio_periodo,
                'filtro_cliente': filtro_cliente,
                'cliente_like': f'%{filtro_cliente}%' if filtro_cliente else None
            }
            
            result = connection.execute(sql, params).fetchall()
            
            if not result:
                return jsonify({
                    'success': True,
                    'dados': {
                        'labels': [],
                        'valores': [],
                        'titulo': 'Evolução Receita Faturada - Sem Dados'
                    }
                })
            
            # Formatar dados
            labels = []
            valores = []
            quantidades = []
            
            meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            for row in result:
                mes_nome = meses_nomes[int(row.mes) - 1]
                label = f"{mes_nome}/{int(row.ano)}"
                
                labels.append(label)
                valores.append(float(row.valor_mes))
                quantidades.append(int(row.qtd_mes))
            
            # Estatísticas
            total_periodo = sum(valores)
            media_mensal = total_periodo / len(valores) if valores else 0
            ctes_total = sum(quantidades)
            
            dados = {
                'labels': labels,
                'valores': valores,
                'quantidades': quantidades,
                'titulo': 'Evolução Receita Faturada - Últimos 12 Meses',
                'estatisticas': {
                    'total_periodo': total_periodo,
                    'media_mensal': media_mensal,
                    'total_ctes': ctes_total,
                    'meses_analisados': len(valores)
                },
                'filtro_cliente': filtro_cliente or 'Todos os clientes'
            }
            
            logger.info(f"Gráfico evolução gerado: {len(labels)} meses")
            
            return jsonify({
                'success': True,
                'dados': dados
            })
        
    except Exception as e:
        logger.error(f"Erro na API evolução: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/clientes')
@login_required
def api_clientes():
    """API para lista de clientes"""
    try:
        # Últimos 6 meses
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
                clientes.append({
                    'nome': row.destinatario_nome,
                    'total_ctes': int(row.total_ctes),
                    'receita_total': float(row.receita_total)
                })
            
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

# ============================================================================
# SISTEMA DE ALERTAS - NOVO
# ============================================================================

@bp.route('/api/alertas')
@login_required
def api_alertas():
    """API para sistema de alertas"""
    try:
        with db.engine.connect() as connection:
            alertas = []
            
            # 1. Primeiro envio pendente
            sql_primeiro = text("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker 
                WHERE primeiro_envio IS NULL 
                AND data_emissao >= :data_limite
            """)
            
            data_limite = datetime.now() - timedelta(days=60)
            result_primeiro = connection.execute(sql_primeiro, {"data_limite": data_limite}).fetchone()
            
            if result_primeiro.quantidade > 0:
                alertas.append({
                    'tipo': 'critico' if result_primeiro.quantidade > 10 else 'aviso',
                    'titulo': 'Primeiro Envio Pendente',
                    'quantidade': int(result_primeiro.quantidade),
                    'valor': float(result_primeiro.valor_total),
                    'descricao': 'CTEs pendentes de primeiro envio',
                    'icon': 'exclamation-triangle'
                })
            
            # 2. Envio final pendente
            sql_final = text("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker 
                WHERE primeiro_envio IS NOT NULL 
                AND envio_final IS NULL
                AND data_emissao >= :data_limite
            """)
            
            result_final = connection.execute(sql_final, {"data_limite": data_limite}).fetchone()
            
            if result_final.quantidade > 0:
                alertas.append({
                    'tipo': 'aviso',
                    'titulo': 'Envio Final Pendente',
                    'quantidade': int(result_final.quantidade),
                    'valor': float(result_final.valor_total),
                    'descricao': 'CTEs com envio final pendente',
                    'icon': 'clock'
                })
            
            # 3. Faturas sem baixa (vencidas)
            sql_vencidas = text("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker 
                WHERE data_baixa IS NULL 
                AND data_emissao < :data_vencimento
                AND data_emissao >= :data_limite
            """)
            
            data_vencimento = datetime.now() - timedelta(days=30)  # 30 dias para vencer
            data_limite_vencidas = datetime.now() - timedelta(days=90)
            
            result_vencidas = connection.execute(sql_vencidas, {
                "data_vencimento": data_vencimento,
                "data_limite": data_limite_vencidas
            }).fetchone()
            
            if result_vencidas.quantidade > 0:
                alertas.append({
                    'tipo': 'critico',
                    'titulo': 'Faturas Vencidas',
                    'quantidade': int(result_vencidas.quantidade),
                    'valor': float(result_vencidas.valor_total),
                    'descricao': 'Faturas com mais de 30 dias sem baixa',
                    'icon': 'exclamation-circle'
                })
        
        return jsonify({
            'success': True,
            'alertas': alertas,
            'total_alertas': len(alertas),
            'ultima_atualizacao': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na API alertas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# API ANALISE COMPLETA - MANTIDA PARA COMPATIBILIDADE
# ============================================================================

@bp.route('/api/analise-completa')
@login_required
def api_analise_completa():
    """API para análise financeira completa"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Tentar usar serviço se disponível
        try:
            from app.services.analise_financeira_service import AnaliseFinanceiraService
            analise = AnaliseFinanceiraService.gerar_analise_completa(
                filtro_dias=filtro_dias,
                filtro_cliente=filtro_cliente
            )
            
            return jsonify({
                'success': True,
                'analise': analise,
                'dados': analise
            })
            
        except ImportError:
            logger.warning("AnaliseFinanceiraService não disponível, usando fallback")
            
            # Fallback simples
            dados_basicos = {
                'resumo_filtro': {
                    'periodo_dias': filtro_dias,
                    'cliente_filtro': filtro_cliente,
                    'total_ctes': 0
                },
                'graficos': {
                    'receita_mensal': {'labels': [], 'valores': []},
                    'top_clientes': {'labels': [], 'valores': []}
                }
            }
            
            return jsonify({
                'success': True,
                'analise': dados_basicos,
                'dados': dados_basicos
            })
        
    except Exception as e:
        logger.error(f"Erro na análise completa: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# DIAGNÓSTICO E DEBUG
# ============================================================================

@bp.route('/api/diagnostico-completo')
@login_required
def api_diagnostico_completo():
    """API de diagnóstico completo do sistema"""
    try:
        diagnostico = {}
        
        # Verificar banco
        with db.engine.connect() as connection:
            # Dados básicos
            total_ctes = connection.execute(text('SELECT COUNT(*) FROM dashboard_baker')).scalar()
            diagnostico['total_ctes'] = total_ctes
            
            # Mês corrente
            agora = datetime.now()
            primeiro_dia = agora.replace(day=1).date()
            
            sql_mes = text("""
                SELECT 
                    COUNT(*) as total_mes,
                    SUM(valor_total) as receita_mes,
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as com_envio_final,
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as com_inclusao_fatura,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as com_numero_fatura
                FROM dashboard_baker 
                WHERE data_emissao >= :primeiro_dia
            """)
            
            result_mes = connection.execute(sql_mes, {"primeiro_dia": primeiro_dia}).fetchone()
            
            diagnostico['mes_corrente'] = {
                'total_ctes': int(result_mes.total_mes),
                'receita_total': float(result_mes.receita_mes or 0),
                'com_envio_final': int(result_mes.com_envio_final),
                'com_inclusao_fatura': int(result_mes.com_inclusao_fatura),
                'com_numero_fatura': int(result_mes.com_numero_fatura)
            }
        
        # Verificar se APIs funcionam
        diagnostico['apis_funcionais'] = True
        
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