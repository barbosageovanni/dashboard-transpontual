#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes para Análise Financeira - VERSÃO CORRIGIDA
app/routes/analise_financeira.py
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
from app.models.cte import CTE
from app import db
from sqlalchemy import func, and_, desc, extract
import logging

bp = Blueprint('analise_financeira', __name__, url_prefix='/analise-financeira')

@bp.route('/')
@login_required
def index():
    """Página principal da análise financeira"""
    return render_template('analise_financeira/index.html')

@bp.route('/api/analise-completa')
@login_required
def api_analise_completa():
    """API para análise financeira completa - VERSÃO SIMPLIFICADA"""
    try:
        # Parâmetros de filtro
        filtro_dias = int(request.args.get('filtro_dias', 180))
        
        # Data limite baseada no filtro
        data_limite = datetime.now().date() - timedelta(days=filtro_dias)
        
        # Query básica sem campos problemáticos
        query_base = db.session.query(CTE).filter(
            CTE.data_emissao >= data_limite
        )
        
        # Métricas básicas
        total_ctes = query_base.count()
        valor_total = query_base.with_entities(
            func.sum(CTE.valor_total)
        ).scalar() or 0
        
        ctes_com_baixa = query_base.filter(
            CTE.data_baixa.isnot(None)
        ).count()
        
        valor_baixado = query_base.filter(
            CTE.data_baixa.isnot(None)
        ).with_entities(
            func.sum(CTE.valor_total)
        ).scalar() or 0
        
        # Receita por mês
        receita_mensal = db.session.query(
            extract('year', CTE.data_emissao).label('ano'),
            extract('month', CTE.data_emissao).label('mes'),
            func.sum(CTE.valor_total).label('total')
        ).filter(
            CTE.data_emissao >= data_limite
        ).group_by(
            extract('year', CTE.data_emissao),
            extract('month', CTE.data_emissao)
        ).order_by(
            extract('year', CTE.data_emissao),
            extract('month', CTE.data_emissao)
        ).all()
        
        # Top clientes
        top_clientes = db.session.query(
            CTE.destinatario_nome,
            func.sum(CTE.valor_total).label('total'),
            func.count(CTE.id).label('quantidade')
        ).filter(
            CTE.data_emissao >= data_limite
        ).group_by(
            CTE.destinatario_nome
        ).order_by(
            desc(func.sum(CTE.valor_total))
        ).limit(10).all()
        
        # Análise por veículo
        analise_veiculos = db.session.query(
            CTE.veiculo_placa,
            func.sum(CTE.valor_total).label('faturamento'),
            func.count(CTE.id).label('viagens'),
            func.avg(CTE.valor_total).label('ticket_medio')
        ).filter(
            and_(
                CTE.data_emissao >= data_limite,
                CTE.veiculo_placa.isnot(None),
                CTE.veiculo_placa != ''
            )
        ).group_by(
            CTE.veiculo_placa
        ).order_by(
            desc(func.sum(CTE.valor_total))
        ).limit(20).all()
        
        # Preparar dados para gráficos
        labels_meses = []
        valores_meses = []
        
        for item in receita_mensal:
            labels_meses.append(f"{int(item.mes):02d}/{int(item.ano)}")
            valores_meses.append(float(item.total))
        
        # Resposta estruturada
        response_data = {
            'success': True,
            'resumo': {
                'total_ctes': total_ctes,
                'valor_total': float(valor_total),
                'ctes_com_baixa': ctes_com_baixa,
                'valor_baixado': float(valor_baixado),
                'valor_pendente': float(valor_total - valor_baixado),
                'percentual_baixado': round((valor_baixado / valor_total * 100) if valor_total > 0 else 0, 2)
            },
            'graficos': {
                'receita_mensal': {
                    'labels': labels_meses,
                    'dados': valores_meses
                }
            },
            'top_clientes': [
                {
                    'nome': cliente.destinatario_nome or 'Cliente Sem Nome',
                    'valor': float(cliente.total),
                    'quantidade': int(cliente.quantidade)
                }
                for cliente in top_clientes
            ],
            'analise_veiculos': [
                {
                    'placa': veiculo.veiculo_placa,
                    'faturamento': float(veiculo.faturamento),
                    'viagens': int(veiculo.viagens),
                    'ticket_medio': float(veiculo.ticket_medio),
                    'score': min(100, int((veiculo.viagens * 10) + (float(veiculo.faturamento) / 1000)))
                }
                for veiculo in analise_veiculos
            ],
            'filtros_aplicados': {
                'periodo_dias': filtro_dias,
                'data_limite': data_limite.strftime('%Y-%m-%d')
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Erro na análise financeira: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@bp.route('/api/projecoes')
@login_required
def api_projecoes():
    """API para projeções futuras - SIMPLIFICADA"""
    try:
        # Últimos 6 meses para base de cálculo
        data_limite = datetime.now().date() - timedelta(days=180)
        
        receita_mensal = db.session.query(
            extract('year', CTE.data_emissao).label('ano'),
            extract('month', CTE.data_emissao).label('mes'),
            func.sum(CTE.valor_total).label('total')
        ).filter(
            CTE.data_emissao >= data_limite
        ).group_by(
            extract('year', CTE.data_emissao),
            extract('month', CTE.data_emissao)
        ).all()
        
        if not receita_mensal:
            return jsonify({
                'success': True,
                'projecoes': [],
                'metodologia': 'Sem dados suficientes para projeção'
            })
        
        # Cálculo simples: média dos últimos meses
        valores = [float(item.total) for item in receita_mensal]
        media_mensal = sum(valores) / len(valores)
        
        # Gerar 3 projeções
        projecoes = []
        for i in range(1, 4):
            data_projecao = datetime.now().date().replace(day=1) + timedelta(days=32*i)
            data_projecao = data_projecao.replace(day=1)
            
            # Variação aleatória para simular cenários
            fator_variacao = 1.0 + (i * 0.05)  # 5% de crescimento por mês
            valor_projetado = media_mensal * fator_variacao
            
            projecoes.append({
                'mes': data_projecao.strftime('%m/%Y'),
                'valor_projetado': valor_projetado,
                'confianca': max(50, 90 - (i * 15)),  # Confiança diminui com o tempo
                'cenario': 'Base' if i == 1 else ('Otimista' if i == 2 else 'Conservador')
            })
        
        return jsonify({
            'success': True,
            'projecoes': projecoes,
            'base_calculo': {
                'meses_analisados': len(valores),
                'media_mensal': media_mensal
            }
        })
        
    except Exception as e:
        logging.error(f"Erro nas projeções: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/comparativo')
@login_required
def api_comparativo():
    """API para análise comparativa temporal"""
    try:
        periodo = int(request.args.get('periodo', 30))  # 7, 15, 30 dias
        
        # Período atual
        data_fim = datetime.now().date()
        data_inicio = data_fim - timedelta(days=periodo)
        
        # Período anterior (mesmo range)
        data_anterior_fim = data_inicio - timedelta(days=1)
        data_anterior_inicio = data_anterior_fim - timedelta(days=periodo)
        
        # Mesmo período ano anterior
        data_ano_anterior_fim = data_fim.replace(year=data_fim.year - 1)
        data_ano_anterior_inicio = data_inicio.replace(year=data_inicio.year - 1)
        
        # Consultas
        def calcular_periodo(inicio, fim):
            return db.session.query(
                func.count(CTE.id),
                func.sum(CTE.valor_total)
            ).filter(
                and_(
                    CTE.data_emissao >= inicio,
                    CTE.data_emissao <= fim
                )
            ).first()
        
        atual = calcular_periodo(data_inicio, data_fim)
        anterior = calcular_periodo(data_anterior_inicio, data_anterior_fim)
        ano_anterior = calcular_periodo(data_ano_anterior_inicio, data_ano_anterior_fim)
        
        def calcular_variacao(atual_val, anterior_val):
            if anterior_val and anterior_val > 0:
                return round(((atual_val - anterior_val) / anterior_val) * 100, 2)
            return 0
        
        atual_valor = float(atual[1] or 0)
        anterior_valor = float(anterior[1] or 0)
        ano_anterior_valor = float(ano_anterior[1] or 0)
        
        return jsonify({
            'success': True,
            'comparativo': {
                'periodo_atual': {
                    'valor': atual_valor,
                    'quantidade': int(atual[0] or 0),
                    'periodo': f"{data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')}"
                },
                'periodo_anterior': {
                    'valor': anterior_valor,
                    'quantidade': int(anterior[0] or 0),
                    'variacao_valor': calcular_variacao(atual_valor, anterior_valor),
                    'periodo': f"{data_anterior_inicio.strftime('%d/%m')} a {data_anterior_fim.strftime('%d/%m')}"
                },
                'ano_anterior': {
                    'valor': ano_anterior_valor,
                    'quantidade': int(ano_anterior[0] or 0),
                    'variacao_valor': calcular_variacao(atual_valor, ano_anterior_valor),
                    'periodo': f"{data_ano_anterior_inicio.strftime('%d/%m')} a {data_ano_anterior_fim.strftime('%d/%m')}"
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Erro no comparativo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/clientes')
@login_required
def api_lista_clientes():
    """Lista de clientes para filtro"""
    try:
        clientes = db.session.query(
            CTE.destinatario_nome
        ).filter(
            and_(
                CTE.destinatario_nome.isnot(None),
                CTE.destinatario_nome != ''
            )
        ).distinct().order_by(
            CTE.destinatario_nome
        ).limit(100).all()
        
        lista_clientes = [cliente[0] for cliente in clientes]
        
        return jsonify({
            'success': True,
            'clientes': lista_clientes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
