#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico - Módulo Análise Financeira
diagnostico_modulo.py
"""

import os
import sys
import importlib
from pathlib import Path

def verificar_estrutura_arquivos():
    """Verificar se todos os arquivos foram criados"""
    print("🔍 DIAGNÓSTICO 1: Verificando estrutura de arquivos...")
    
    arquivos_necessarios = [
        'app/services/analise_financeira_service.py',
        'app/routes/analise_financeira.py',
        'app/templates/analise_financeira/index.html',
        'app/static/js/analise_financeira.js'
    ]
    
    arquivos_existentes = []
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
            arquivos_existentes.append(arquivo)
        else:
            print(f"❌ {arquivo} - ARQUIVO NÃO ENCONTRADO")
            arquivos_faltando.append(arquivo)
    
    return len(arquivos_faltando) == 0, arquivos_faltando

def verificar_imports():
    """Verificar se imports funcionam"""
    print("\n🔍 DIAGNÓSTICO 2: Verificando imports...")
    
    try:
        # Verificar se scipy está instalado
        import scipy
        print("✅ scipy instalado")
    except ImportError:
        print("❌ scipy NÃO INSTALADO")
        return False
    
    try:
        # Verificar app principal
        from app import create_app
        print("✅ app principal OK")
    except ImportError as e:
        print(f"❌ Erro no app principal: {e}")
        return False
    
    try:
        # Verificar serviço
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        print("✅ AnaliseFinanceiraService OK")
    except ImportError as e:
        print(f"❌ AnaliseFinanceiraService FALHOU: {e}")
        return False
    
    return True

def verificar_blueprint_registrado():
    """Verificar se blueprint foi registrado"""
    print("\n🔍 DIAGNÓSTICO 3: Verificando registro do blueprint...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Listar todos os blueprints registrados
        blueprints = list(app.blueprints.keys())
        print(f"📋 Blueprints registrados: {blueprints}")
        
        if 'analise_financeira' in blueprints:
            print("✅ Blueprint 'analise_financeira' registrado")
            return True
        else:
            print("❌ Blueprint 'analise_financeira' NÃO REGISTRADO")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar blueprints: {e}")
        return False

def verificar_rotas():
    """Verificar se rotas estão funcionando"""
    print("\n🔍 DIAGNÓSTICO 4: Verificando rotas...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Listar todas as rotas
            rotas = []
            for rule in app.url_map.iter_rules():
                rotas.append(str(rule))
            
            # Verificar rotas específicas do módulo
            rotas_modulo = [r for r in rotas if 'analise-financeira' in r]
            
            print(f"📋 Total de rotas: {len(rotas)}")
            print(f"📋 Rotas do módulo: {len(rotas_modulo)}")
            
            for rota in rotas_modulo[:5]:  # Mostrar primeiras 5
                print(f"   🔗 {rota}")
            
            return len(rotas_modulo) > 0
            
    except Exception as e:
        print(f"❌ Erro ao verificar rotas: {e}")
        return False

def verificar_menu():
    """Verificar se menu foi atualizado"""
    print("\n🔍 DIAGNÓSTICO 5: Verificando menu...")
    
    try:
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        if 'analise-financeira' in conteudo.lower():
            print("✅ Menu atualizado com Análise Financeira")
            return True
        else:
            print("❌ Menu NÃO CONTÉM link para Análise Financeira")
            return False
            
    except FileNotFoundError:
        print("❌ Arquivo base.html não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar menu: {e}")
        return False

def criar_arquivos_faltando(arquivos_faltando):
    """Criar arquivos que estão faltando"""
    print(f"\n🔧 CORRIGINDO: Criando {len(arquivos_faltando)} arquivos faltando...")
    
    # Criar diretórios se não existirem
    os.makedirs('app/services', exist_ok=True)
    os.makedirs('app/routes', exist_ok=True)
    os.makedirs('app/templates/analise_financeira', exist_ok=True)
    os.makedirs('app/static/js', exist_ok=True)
    
    # Criar arquivos básicos
    if 'app/services/analise_financeira_service.py' in arquivos_faltando:
        criar_service_basico()
    
    if 'app/routes/analise_financeira.py' in arquivos_faltando:
        criar_routes_basico()
    
    if 'app/templates/analise_financeira/index.html' in arquivos_faltando:
        criar_template_basico()
    
    if 'app/static/js/analise_financeira.js' in arquivos_faltando:
        criar_js_basico()

def criar_service_basico():
    """Criar service básico"""
    codigo = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Análise Financeira - Dashboard Baker
app/services/analise_financeira_service.py
"""

from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy import func

class AnaliseFinanceiraService:
    """Serviço para análise financeira completa"""
    
    @staticmethod
    def gerar_analise_completa(filtro_dias: int = 180, filtro_cliente: str = None) -> Dict:
        """Gera análise financeira completa"""
        try:
            # Filtros de data
            data_inicio = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Query base
            query = CTE.query.filter(CTE.data_emissao >= data_inicio)
            
            if filtro_cliente:
                query = query.filter(CTE.destinatario_nome == filtro_cliente)
            
            ctes = query.all()
            
            if not ctes:
                return cls._analise_vazia()
            
            # Converter para DataFrame
            df = pd.DataFrame([{
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome,
                'valor_total': float(cte.valor_total or 0),
                'data_emissao': cte.data_emissao,
                'data_baixa': cte.data_baixa,
                'primeiro_envio': cte.primeiro_envio
            } for cte in ctes])
            
            return {
                'receita_mensal': cls._calcular_receita_mensal(df),
                'ticket_medio': cls._calcular_ticket_medio(df),
                'tempo_medio_cobranca': cls._calcular_tempo_cobranca(df),
                'tendencia_linear': cls._calcular_tendencia(df),
                'concentracao_clientes': cls._calcular_concentracao(df),
                'stress_test_receita': cls._calcular_stress_test(df),
                'graficos': cls._gerar_dados_graficos(df),
                'resumo_filtro': {
                    'total_ctes': len(df),
                    'filtro_dias': filtro_dias,
                    'filtro_cliente': filtro_cliente
                }
            }
            
        except Exception as e:
            return {'erro': str(e)}
    
    @classmethod
    def _analise_vazia(cls) -> Dict:
        """Retorna análise vazia"""
        return {
            'receita_mensal': {'receita_mes_corrente': 0, 'receita_mes_anterior': 0, 'variacao_percentual': 0},
            'ticket_medio': {'valor': 0, 'mediana': 0},
            'tempo_medio_cobranca': {'dias_medio': 0, 'total_analisados': 0},
            'tendencia_linear': {'coeficiente': 0, 'r_squared': 0},
            'concentracao_clientes': {'percentual_top5': 0, 'clientes_top5': []},
            'stress_test_receita': {'cenarios': []},
            'graficos': {'receita_mensal': {'labels': [], 'valores': []}},
            'resumo_filtro': {'total_ctes': 0}
        }
    
    @staticmethod
    def _calcular_receita_mensal(df: pd.DataFrame) -> Dict:
        """Calcula receita mensal"""
        df['mes_ano'] = pd.to_datetime(df['data_emissao']).dt.to_period('M')
        receita_mensal = df.groupby('mes_ano')['valor_total'].sum()
        
        if len(receita_mensal) >= 2:
            mes_corrente = receita_mensal.iloc[-1]
            mes_anterior = receita_mensal.iloc[-2]
            variacao = ((mes_corrente - mes_anterior) / mes_anterior * 100) if mes_anterior > 0 else 0
        else:
            mes_corrente = receita_mensal.iloc[-1] if len(receita_mensal) > 0 else 0
            mes_anterior = 0
            variacao = 0
        
        return {
            'receita_mes_corrente': float(mes_corrente),
            'receita_mes_anterior': float(mes_anterior),
            'variacao_percentual': float(variacao)
        }
    
    @staticmethod
    def _calcular_ticket_medio(df: pd.DataFrame) -> Dict:
        """Calcula ticket médio"""
        return {
            'valor': float(df['valor_total'].mean()),
            'mediana': float(df['valor_total'].median())
        }
    
    @staticmethod
    def _calcular_tempo_cobranca(df: pd.DataFrame) -> Dict:
        """Calcula tempo médio de cobrança (primeiro_envio → data_baixa)"""
        df_tempo = df[(df['primeiro_envio'].notna()) & (df['data_baixa'].notna())].copy()
        
        if df_tempo.empty:
            return {'dias_medio': 0, 'total_analisados': 0}
        
        df_tempo['dias_cobranca'] = (pd.to_datetime(df_tempo['data_baixa']) - 
                                   pd.to_datetime(df_tempo['primeiro_envio'])).dt.days
        
        return {
            'dias_medio': float(df_tempo['dias_cobranca'].mean()),
            'total_analisados': len(df_tempo)
        }
    
    @staticmethod
    def _calcular_concentracao(df: pd.DataFrame) -> Dict:
        """Calcula concentração Top 5 clientes"""
        receita_por_cliente = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False)
        top5 = receita_por_cliente.head(5)
        percentual_top5 = (top5.sum() / df['valor_total'].sum() * 100) if df['valor_total'].sum() > 0 else 0
        
        return {
            'percentual_top5': float(percentual_top5),
            'clientes_top5': top5.to_dict()
        }
    
    @staticmethod
    def _calcular_stress_test(df: pd.DataFrame) -> Dict:
        """Calcula stress test dos maiores clientes"""
        receita_por_cliente = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False)
        total_receita = df['valor_total'].sum()
        
        cenarios = []
        for i in range(1, min(4, len(receita_por_cliente) + 1)):
            impacto = receita_por_cliente.head(i).sum()
            percentual = (impacto / total_receita * 100) if total_receita > 0 else 0
            cenarios.append({
                'cenario': f'Top {i} cliente(s)',
                'impacto': float(impacto),
                'percentual': float(percentual)
            })
        
        return {'cenarios': cenarios}
    
    @staticmethod
    def _calcular_tendencia(df: pd.DataFrame) -> Dict:
        """Calcula tendência linear (6 meses)"""
        try:
            from scipy import stats
            df['mes_ano'] = pd.to_datetime(df['data_emissao']).dt.to_period('M')
            receita_mensal = df.groupby('mes_ano')['valor_total'].sum().tail(6)
            
            if len(receita_mensal) >= 2:
                x = range(len(receita_mensal))
                y = receita_mensal.values
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                return {
                    'coeficiente': float(slope),
                    'r_squared': float(r_value ** 2)
                }
        except:
            pass
        
        return {'coeficiente': 0, 'r_squared': 0}
    
    @staticmethod
    def _gerar_dados_graficos(df: pd.DataFrame) -> Dict:
        """Gera dados para gráficos"""
        try:
            # Receita mensal
            df['mes_ano'] = pd.to_datetime(df['data_emissao']).dt.to_period('M')
            receita_mensal = df.groupby('mes_ano')['valor_total'].sum()
            
            # Concentração de clientes
            receita_por_cliente = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False).head(5)
            
            return {
                'receita_mensal': {
                    'labels': [str(x) for x in receita_mensal.index],
                    'valores': receita_mensal.values.tolist()
                },
                'concentracao_clientes': {
                    'labels': list(receita_por_cliente.index),
                    'valores': receita_por_cliente.values.tolist()
                },
                'distribuicao_valores': {'labels': [], 'valores': []},
                'tempo_cobranca': {'labels': [], 'valores': []},
                'tendencia_linear': {'labels': [], 'valores': []}
            }
        except:
            return {
                'receita_mensal': {'labels': [], 'valores': []},
                'concentracao_clientes': {'labels': [], 'valores': []},
                'distribuicao_valores': {'labels': [], 'valores': []},
                'tempo_cobranca': {'labels': [], 'valores': []},
                'tendencia_linear': {'labels': [], 'valores': []}
            }
    
    @staticmethod
    def obter_lista_clientes() -> List[str]:
        """Obtém lista de clientes únicos"""
        try:
            clientes = db.session.query(CTE.destinatario_nome).distinct().all()
            return [c[0] for c in clientes if c[0]]
        except:
            return []
'''
    
    with open('app/services/analise_financeira_service.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Service criado")

def criar_routes_basico():
    """Criar routes básico"""
    codigo = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes - Análise Financeira
app/routes/analise_financeira.py
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.services.analise_financeira_service import AnaliseFinanceiraService

bp = Blueprint('analise_financeira', __name__, url_prefix='/analise-financeira')

@bp.route('/')
@login_required
def index():
    """Página principal da análise financeira"""
    return render_template('analise_financeira/index.html')

@bp.route('/api/analise-completa')
@login_required
def api_analise_completa():
    """API para análise completa"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        filtro_cliente = request.args.get('filtro_cliente')
        
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        return jsonify({
            'success': True,
            'data': analise
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/clientes')
@login_required
def api_clientes():
    """API para lista de clientes"""
    try:
        clientes = AnaliseFinanceiraService.obter_lista_clientes()
        return jsonify({
            'success': True,
            'clientes': clientes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/receita-mensal')
@login_required
def api_receita_mensal():
    """API específica para receita mensal"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=filtro_dias)
        
        return jsonify({
            'success': True,
            'data': analise['receita_mensal']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/resumo-executivo')
@login_required
def api_resumo_executivo():
    """API para resumo executivo"""
    try:
        analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=180)
        
        resumo = {
            'receita_mes_corrente': analise['receita_mensal']['receita_mes_corrente'],
            'variacao_percentual': analise['receita_mensal']['variacao_percentual'],
            'ticket_medio': analise['ticket_medio']['valor'],
            'tempo_medio_cobranca': analise['tempo_medio_cobranca']['dias_medio'],
            'concentracao_top5': analise['concentracao_clientes']['percentual_top5']
        }
        
        return jsonify({
            'success': True,
            'data': resumo
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/concentracao-clientes')
@login_required
def api_concentracao_clientes():
    """API específica para concentração de clientes"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=filtro_dias)
        
        return jsonify({
            'success': True,
            'data': analise['concentracao_clientes']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/tempo-cobranca')
@login_required
def api_tempo_cobranca():
    """API específica para tempo de cobrança"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=filtro_dias)
        
        return jsonify({
            'success': True,
            'data': analise['tempo_medio_cobranca']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/tendencia')
@login_required
def api_tendencia():
    """API específica para tendência"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=filtro_dias)
        
        return jsonify({
            'success': True,
            'data': analise['tendencia_linear']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
'''
    
    with open('app/routes/analise_financeira.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Routes criado")

def criar_template_basico():
    """Criar template básico"""
    codigo = '''{% extends "base.html" %}

{% block title %}Análise Financeira - Dashboard Baker{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5><i class="fas fa-chart-line"></i> Análise Financeira</h5>
                </div>
                <div class="card-body">
                    
                    <!-- Filtros -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <label for="filtroPeriodo" class="form-label">Período:</label>
                            <select class="form-select" id="filtroPeriodo">
                                <option value="15">15 dias</option>
                                <option value="30">30 dias</option>
                                <option value="90">90 dias</option>
                                <option value="180" selected>180 dias</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label for="filtroCliente" class="form-label">Cliente:</label>
                            <select class="form-select" id="filtroCliente">
                                <option value="">Todos os clientes</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Cards de Métricas -->
                    <div class="row mb-4">
                        <div class="col-md-2">
                            <div class="metric-card">
                                <div class="metric-number" id="receitaAtual">R$ 0</div>
                                <div class="metric-title">Receita Atual</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="metric-card">
                                <div class="metric-number" id="variacao">0%</div>
                                <div class="metric-title">Variação</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="metric-card">
                                <div class="metric-number" id="ticketMedio">R$ 0</div>
                                <div class="metric-title">Ticket Médio</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="metric-card">
                                <div class="metric-number" id="tempoCobranca">0</div>
                                <div class="metric-title">Dias Cobrança</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="metric-card">
                                <div class="metric-number" id="concentracao">0%</div>
                                <div class="metric-title">Concentração Top5</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="metric-card">
                                <div class="metric-number" id="tendencia">0</div>
                                <div class="metric-title">Tendência</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Gráficos -->
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>📈 Receita Mensal</h6>
                                </div>
                                <div class="card-body">
                                    <canvas id="chartReceitaMensal" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>🎯 Concentração de Clientes</h6>
                                </div>
                                <div class="card-body">
                                    <canvas id="chartConcentracao" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ url_for('static', filename='js/analise_financeira.js') }}"></script>
{% endblock %}'''
    
    with open('app/templates/analise_financeira/index.html', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Template criado")

def criar_js_basico():
    """Criar JavaScript básico"""
    codigo = '''// Análise Financeira JavaScript
$(document).ready(function() {
    carregarAnaliseFinanceira();
    carregarListaClientes();
    
    // Event listeners
    $('#filtroPeriodo, #filtroCliente').on('change', function() {
        carregarAnaliseFinanceira();
    });
});

function carregarAnaliseFinanceira() {
    const filtro_dias = $('#filtroPeriodo').val();
    const filtro_cliente = $('#filtroCliente').val();
    
    const params = new URLSearchParams({
        filtro_dias: filtro_dias
    });
    
    if (filtro_cliente) {
        params.append('filtro_cliente', filtro_cliente);
    }
    
    $.ajax({
        url: `/analise-financeira/api/analise-completa?${params.toString()}`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                atualizarMetricas(response.data);
                criarGraficos(response.data);
            } else {
                console.error('Erro:', response.error);
            }
        },
        error: function(xhr) {
            console.error('Erro na requisição:', xhr);
        }
    });
}

function carregarListaClientes() {
    $.ajax({
        url: '/analise-financeira/api/clientes',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                const select = $('#filtroCliente');
                select.empty().append('<option value="">Todos os clientes</option>');
                
                response.clientes.forEach(cliente => {
                    select.append(`<option value="${cliente}">${cliente}</option>`);
                });
            }
        }
    });
}

function atualizarMetricas(data) {
    $('#receitaAtual').text(formatarMoeda(data.receita_mensal.receita_mes_corrente));
    $('#variacao').text(data.receita_mensal.variacao_percentual.toFixed(1) + '%');
    $('#ticketMedio').text(formatarMoeda(data.ticket_medio.valor));
    $('#tempoCobranca').text(Math.round(data.tempo_medio_cobranca.dias_medio));
    $('#concentracao').text(data.concentracao_clientes.percentual_top5.toFixed(1) + '%');
    $('#tendencia').text(data.tendencia_linear.coeficiente.toFixed(0));
}

function criarGraficos(data) {
    // Gráfico de Receita Mensal
    const ctxReceita = document.getElementById('chartReceitaMensal');
    if (ctxReceita) {
        new Chart(ctxReceita, {
            type: 'line',
            data: {
                labels: data.graficos.receita_mensal.labels,
                datasets: [{
                    label: 'Receita',
                    data: data.graficos.receita_mensal.valores,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Gráfico de Concentração
    const ctxConcentracao = document.getElementById('chartConcentracao');
    if (ctxConcentracao) {
        new Chart(ctxConcentracao, {
            type: 'pie',
            data: {
                labels: data.graficos.concentracao_clientes.labels,
                datasets: [{
                    data: data.graficos.concentracao_clientes.valores,
                    backgroundColor: [
                        '#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}'''
    
    with open('app/static/js/analise_financeira.js', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ JavaScript criado")

def corrigir_init_py():
    """Corrigir app/__init__.py"""
    print("\n🔧 CORRIGINDO: Atualizando app/__init__.py...")
    
    try:
        with open('app/__init__.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if 'analise_financeira' not in conteudo:
            # Adicionar import e registro
            linhas = conteudo.split('\n')
            
            # Adicionar import após outros imports de routes
            for i, linha in enumerate(linhas):
                if 'from app.routes import' in linha and 'auth' in linha:
                    linhas.insert(i + 1, '    from app.routes import analise_financeira')
                    break
            
            # Adicionar registro do blueprint
            for i, linha in enumerate(linhas):
                if 'app.register_blueprint(dashboard.bp)' in linha:
                    linhas.insert(i + 1, '    app.register_blueprint(analise_financeira.bp)')
                    break
            
            # Salvar arquivo
            with open('app/__init__.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas))
            
            print("✅ app/__init__.py atualizado")
            return True
        else:
            print("✅ app/__init__.py já estava correto")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao atualizar app/__init__.py: {e}")
        return False

def corrigir_routes_init():
    """Corrigir app/routes/__init__.py"""
    print("\n🔧 CORRIGINDO: Atualizando app/routes/__init__.py...")
    
    try:
        # Verificar se arquivo existe
        if not os.path.exists('app/routes/__init__.py'):
            # Criar arquivo básico
            codigo = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes Package - Dashboard Baker
"""

from . import auth
from . import dashboard  
from . import baixas
from . import ctes
from . import api
from . import analise_financeira
'''
            with open('app/routes/__init__.py', 'w', encoding='utf-8') as f:
                f.write(codigo)
            print("✅ app/routes/__init__.py criado")
        else:
            # Verificar se analise_financeira já está incluído
            with open('app/routes/__init__.py', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            if 'analise_financeira' not in conteudo:
                # Adicionar import
                with open('app/routes/__init__.py', 'a', encoding='utf-8') as f:
                    f.write('\nfrom . import analise_financeira\n')
                print("✅ app/routes/__init__.py atualizado")
            else:
                print("✅ app/routes/__init__.py já estava correto")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar app/routes/__init__.py: {e}")
        return False

def corrigir_menu():
    """Corrigir menu no base.html"""
    print("\n🔧 CORRIGINDO: Atualizando menu no base.html...")
    
    try:
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if 'analise-financeira' not in conteudo.lower():
            # Adicionar item de menu após CTEs
            menu_item = '''                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('analise_financeira.index') }}">
                            <i class="fas fa-chart-line"></i> Análise Financeira
                        </a>
                    </li>'''
            
            # Encontrar posição para inserir
            if 'CTEs' in conteudo:
                conteudo = conteudo.replace(
                    '</a>\n                    </li>',
                    '</a>\n                    </li>\n' + menu_item,
                    1  # Substituir apenas a primeira ocorrência
                )
            else:
                # Se não encontrar CTEs, adicionar após último item de menu
                conteudo = conteudo.replace(
                    '</ul>\n                \n                <ul class="navbar-nav">',
                    menu_item + '\n                </ul>\n                \n                <ul class="navbar-nav">'
                )
            
            with open('app/templates/base.html', 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            print("✅ Menu atualizado no base.html")
            return True
        else:
            print("✅ Menu já estava correto no base.html")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao atualizar menu: {e}")
        return False

def main():
    """Função principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO - MÓDULO ANÁLISE FINANCEIRA")
    print("="*60)
    
    # 1. Verificar arquivos
    arquivos_ok, arquivos_faltando = verificar_estrutura_arquivos()
    
    if not arquivos_ok:
        print(f"\n🔧 SOLUÇÃO: Criando {len(arquivos_faltando)} arquivos faltando...")
        criar_arquivos_faltando(arquivos_faltando)
    
    # 2. Corrigir registros
    print("\n🔧 CORRIGINDO REGISTROS E CONFIGURAÇÕES...")
    corrigir_init_py()
    corrigir_routes_init()
    corrigir_menu()
    
    # 3. Verificar imports
    imports_ok = verificar_imports()
    
    # 4. Verificar blueprint
    blueprint_ok = verificar_blueprint_registrado()
    
    # 5. Verificar rotas
    rotas_ok = verificar_rotas()
    
    # 6. Verificar menu
    menu_ok = verificar_menu()
    
    # Resultado final
    print("\n" + "="*60)
    print("📋 RESULTADO FINAL DO DIAGNÓSTICO:")
    print("="*60)
    
    resultados = [
        ("Arquivos", arquivos_ok),
        ("Imports", imports_ok),
        ("Blueprint", blueprint_ok),
        ("Rotas", rotas_ok),
        ("Menu", menu_ok)
    ]
    
    todos_ok = all(resultado for _, resultado in resultados)
    
    for nome, resultado in resultados:
        status = "✅ OK" if resultado else "❌ PROBLEMA"
        print(f"{nome:<12} {status}")
    
    if todos_ok:
        print("\n🎉 TODOS OS PROBLEMAS CORRIGIDOS!")
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Instalar dependência: pip install scipy>=1.10.0")
        print("2. Reiniciar aplicação: python iniciar.py")
        print("3. Acessar: http://localhost:5000/analise-financeira/")
        print("4. Executar teste: python test_analise_financeira.py")
    else:
        print("\n⚠️ AINDA HÁ PROBLEMAS PARA RESOLVER")
        print("Verifique os erros acima e execute o diagnóstico novamente")
    
    print("="*60)

if __name__ == '__main__':
    main()