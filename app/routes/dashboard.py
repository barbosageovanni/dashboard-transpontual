from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Adicionar o caminho do serviço
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from app.services.metricas_service import MetricasService
    METRICAS_SERVICE_OK = True
except ImportError as e:
    print(f"⚠️ MetricasService não disponível: {e}")
    METRICAS_SERVICE_OK = False

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    return render_template('dashboard/index.html')

@bp.route('/api/debug')
@login_required
def api_debug():
    """API de debug para diagnosticar problemas"""
    try:
        from app.models.cte import CTE
        
        # Contar registros na base
        total_ctes = CTE.query.count()
        
        # Pegar alguns exemplos
        exemplos = CTE.query.limit(5).all()
        
        # Testar conversão
        exemplos_dict = []
        for cte in exemplos:
            try:
                exemplos_dict.append({
                    'numero_cte': cte.numero_cte,
                    'valor_total': float(cte.valor_total or 0),
                    'destinatario_nome': cte.destinatario_nome,
                    'has_baixa': cte.has_baixa,
                    'data_emissao': cte.data_emissao.isoformat() if cte.data_emissao else None,
                    'data_atesto': cte.data_atesto.isoformat() if cte.data_atesto else None
                })
            except Exception as e:
                exemplos_dict.append({'erro': str(e)})
        
        return jsonify({
            'success': True,
            'debug': {
                'total_ctes_db': total_ctes,
                'exemplos': exemplos_dict,
                'metricas_service_available': METRICAS_SERVICE_OK,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': str(e.__class__.__name__)
        }), 500

@bp.route('/api/metricas')
@login_required
def api_metricas():
    """API para métricas expandidas - VERSÃO CORRIGIDA"""
    try:
        # Usar sempre o cálculo manual com os dados reais
        return calcular_metricas_completas()
        
    except Exception as e:
        print(f"❌ Erro na API de métricas: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'metricas': metricas_vazias(),
            'alertas': {},
            'variacoes': {}
        }), 500

def calcular_metricas_completas():
    """Calcula métricas completas usando pandas - VERSÃO CORRIGIDA"""
    try:
        # Carregar dados do banco como DataFrame
        query = """
            SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                   data_emissao, numero_fatura, data_baixa, observacao,
                   data_inclusao_fatura, data_envio_processo, primeiro_envio,
                   data_rq_tmc, data_atesto, envio_final, origem_dados
            FROM dashboard_baker 
            ORDER BY numero_cte DESC
        """
        
        df = pd.read_sql_query(query, db.session.connection())
        
        if df.empty:
            return jsonify({
                'success': True,
                'metricas': metricas_vazias(),
                'alertas': {},
                'variacoes': {},
                'graficos': graficos_vazios(),
                'timestamp': datetime.now().isoformat(),
                'total_registros': 0
            })
        
        # Converter colunas de data
        date_columns = ['data_emissao', 'data_baixa', 'data_inclusao_fatura',
                       'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                       'data_atesto', 'envio_final']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Garantir que valor_total seja numérico
        df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)
        
        # Calcular métricas
        metricas = calcular_metricas_basicas(df)
        alertas = calcular_alertas_inteligentes(df)
        variacoes = calcular_variacoes_tempo(df)
        graficos = gerar_graficos_dados(df)
        
        return jsonify({
            'success': True,
            'metricas': metricas,
            'alertas': alertas,
            'variacoes': variacoes,
            'graficos': graficos,
            'timestamp': datetime.now().isoformat(),
            'total_registros': len(df)
        })
        
    except Exception as e:
        print(f"❌ Erro no cálculo completo: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'metricas': metricas_vazias(),
            'alertas': {},
            'variacoes': {},
            'graficos': graficos_vazios()
        }), 500

def calcular_metricas_basicas(df):
    """Calcula métricas básicas do DataFrame"""
    if df.empty:
        return metricas_vazias()
    
    # Métricas básicas
    total_ctes = len(df)
    clientes_unicos = df['destinatario_nome'].nunique()
    valor_total = df['valor_total'].sum()
    veiculos_ativos = df['veiculo_placa'].nunique() if 'veiculo_placa' in df.columns else 0
    
    # Métricas de pagamento
    faturas_pagas = len(df[df['data_baixa'].notna()])
    faturas_pendentes = len(df[df['data_baixa'].isna()])
    valor_pago = df[df['data_baixa'].notna()]['valor_total'].sum()
    valor_pendente = df[df['data_baixa'].isna()]['valor_total'].sum()
    
    # Métricas de faturamento
    ctes_com_fatura = len(df[df['numero_fatura'].notna() & (df['numero_fatura'] != '')])
    ctes_sem_fatura = len(df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')])
    valor_com_fatura = df[df['numero_fatura'].notna() & (df['numero_fatura'] != '')]['valor_total'].sum()
    valor_sem_fatura = df[df['numero_fatura'].isna() | (df['numero_fatura'] == '')]['valor_total'].sum()
    
    # Processos completos
    mask_completo = (
        df['data_emissao'].notna() & 
        df['primeiro_envio'].notna() & 
        df['data_atesto'].notna() & 
        df['envio_final'].notna()
    )
    processos_completos = mask_completo.sum()
    processos_incompletos = total_ctes - processos_completos
    
    # Métricas financeiras avançadas
    ticket_medio = df['valor_total'].mean() if total_ctes > 0 else 0.0
    maior_valor = df['valor_total'].max() if total_ctes > 0 else 0.0
    menor_valor = df['valor_total'].min() if total_ctes > 0 else 0.0
    
    # Análise temporal (receita mensal)
    receita_mensal_media = 0.0
    crescimento_mensal = 0.0
    
    if 'data_emissao' in df.columns and df['data_emissao'].notna().any():
        try:
            df_temp = df[df['data_emissao'].notna()].copy()
            df_temp['mes_ano'] = df_temp['data_emissao'].dt.to_period('M')
            receita_mensal = df_temp.groupby('mes_ano')['valor_total'].sum()
            
            if len(receita_mensal) > 0:
                receita_mensal_media = receita_mensal.mean()
                
                if len(receita_mensal) >= 2:
                    ultimo_mes = receita_mensal.iloc[-1]
                    penultimo_mes = receita_mensal.iloc[-2]
                    if penultimo_mes > 0:
                        crescimento_mensal = ((ultimo_mes - penultimo_mes) / penultimo_mes) * 100
        except:
            pass
    
    return {
        'total_ctes': int(total_ctes),
        'clientes_unicos': int(clientes_unicos),
        'valor_total': float(valor_total),
        'faturas_pagas': int(faturas_pagas),
        'faturas_pendentes': int(faturas_pendentes),
        'valor_pago': float(valor_pago),
        'valor_pendente': float(valor_pendente),
        'ctes_com_fatura': int(ctes_com_fatura),
        'ctes_sem_fatura': int(ctes_sem_fatura),
        'valor_com_fatura': float(valor_com_fatura),
        'valor_sem_fatura': float(valor_sem_fatura),
        'veiculos_ativos': int(veiculos_ativos),
        'processos_completos': int(processos_completos),
        'processos_incompletos': int(processos_incompletos),
        'ticket_medio': float(ticket_medio),
        'maior_valor': float(maior_valor),
        'menor_valor': float(menor_valor),
        'receita_mensal_media': float(receita_mensal_media),
        'crescimento_mensal': float(crescimento_mensal),
        'taxa_conclusao': float((processos_completos / total_ctes * 100) if total_ctes > 0 else 0),
        'taxa_pagamento': float((faturas_pagas / total_ctes * 100) if total_ctes > 0 else 0),
        'taxa_faturamento': float((ctes_com_fatura / total_ctes * 100) if total_ctes > 0 else 0)
    }

def calcular_alertas_inteligentes(df):
    """Sistema de alertas inteligentes"""
    alertas = {
        'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'envio_final_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'faturas_vencidas': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'ctes_sem_faturas': {'qtd': 0, 'valor': 0.0, 'lista': []}
    }

    if df.empty:
        return alertas

    hoje = pd.Timestamp.now().normalize()

    try:
        # 1. Primeiro envio pendente (10 dias após emissão)
        mask_primeiro_envio = (
            df['data_emissao'].notna() & 
            ((hoje - df['data_emissao']).dt.days > 10) &
            df['primeiro_envio'].isna()
        )
        if mask_primeiro_envio.any():
            ctes_problema = df[mask_primeiro_envio]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']),
                    'destinatario_nome': str(row['destinatario_nome']),
                    'valor_total': float(row['valor_total']),
                    'data_emissao': row['data_emissao'].isoformat() if pd.notna(row['data_emissao']) else None
                }
                lista_segura.append(item)

            alertas['primeiro_envio_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

        # 2. Envio Final Pendente (5 dias após atesto)
        mask_envio_final = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 5) &
            df['envio_final'].isna()
        )
        if mask_envio_final.any():
            ctes_problema = df[mask_envio_final]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']),
                    'destinatario_nome': str(row['destinatario_nome']),
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'].isoformat() if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)

            alertas['envio_final_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

        # 3. Faturas vencidas (90 dias após atesto, sem baixa)
        mask_vencidas = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 90) &
            df['data_baixa'].isna()
        )
        if mask_vencidas.any():
            ctes_problema = df[mask_vencidas]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']),
                    'destinatario_nome': str(row['destinatario_nome']),
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'].isoformat() if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)

            alertas['faturas_vencidas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

        # 4. CTEs sem faturas (3 dias após atesto)
        mask_sem_faturas = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 3) &
            (df['numero_fatura'].isna() | (df['numero_fatura'] == ''))
        )
        if mask_sem_faturas.any():
            ctes_problema = df[mask_sem_faturas]
            lista_segura = []
            for _, row in ctes_problema.iterrows():
                item = {
                    'numero_cte': int(row['numero_cte']),
                    'destinatario_nome': str(row['destinatario_nome']),
                    'valor_total': float(row['valor_total']),
                    'data_atesto': row['data_atesto'].isoformat() if pd.notna(row['data_atesto']) else None
                }
                lista_segura.append(item)

            alertas['ctes_sem_faturas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }

    except Exception as e:
        print(f"⚠️ Aviso no cálculo de alertas: {str(e)}")

    return alertas

def calcular_variacoes_tempo(df):
    """Calcula variações de tempo entre processos - VERSÃO CORRIGIDA"""
    variacoes = {}
    
    if df.empty:
        return variacoes
    
    # Configurações das variações
    variacoes_config = [
        {
            'nome': 'RQ/TMC → 1º Envio',
            'campo_inicio': 'data_rq_tmc',
            'campo_fim': 'primeiro_envio',
            'meta_dias': 3,
            'codigo': 'rq_tmc_primeiro_envio'
        },
        {
            'nome': '1º Envio → Atesto',
            'campo_inicio': 'primeiro_envio',
            'campo_fim': 'data_atesto',
            'meta_dias': 7,
            'codigo': 'primeiro_envio_atesto'
        },
        {
            'nome': 'Atesto → Envio Final',
            'campo_inicio': 'data_atesto',
            'campo_fim': 'envio_final',
            'meta_dias': 2,
            'codigo': 'atesto_envio_final'
        },
        {
            'nome': 'CTE → Inclusão Fatura',
            'campo_inicio': 'data_emissao',
            'campo_fim': 'data_inclusao_fatura',
            'meta_dias': 2,
            'codigo': 'cte_inclusao_fatura'
        },
        {
            'nome': 'CTE → Baixa',
            'campo_inicio': 'data_emissao',
            'campo_fim': 'data_baixa',
            'meta_dias': 30,
            'codigo': 'cte_baixa'
        }
    ]
    
    for config in variacoes_config:
        campo_inicio = config['campo_inicio']
        campo_fim = config['campo_fim']
        codigo = config['codigo']
        meta_dias = config['meta_dias']
        
        # Verificar se as colunas existem
        if campo_inicio in df.columns and campo_fim in df.columns:
            # Filtrar registros com ambas as datas
            mask = df[campo_inicio].notna() & df[campo_fim].notna()
            
            if mask.any():
                df_filtrado = df[mask].copy()
                
                # Calcular diferença em dias
                try:
                    dias = (df_filtrado[campo_fim] - df_filtrado[campo_inicio]).dt.days
                    
                    # Filtrar apenas valores válidos (>= 0)
                    dias_validos = dias[dias >= 0]
                    
                    if len(dias_validos) > 0:
                        media = float(dias_validos.mean())
                        mediana = float(dias_validos.median())
                        
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
                            'qtd': len(dias_validos),
                            'meta_dias': meta_dias,
                            'performance': performance,
                            'min': int(dias_validos.min()),
                            'max': int(dias_validos.max())
                        }
                        
                except Exception as e:
                    print(f"Erro ao calcular {codigo}: {e}")
                    continue
    
    return variacoes

def gerar_graficos_dados(df):
    """Gera dados para os gráficos"""
    graficos = {
        'evolucao_mensal': {'labels': [], 'valores': [], 'quantidades': []},
        'top_clientes': {'labels': [], 'valores': []},
        'distribuicao_status': {
            'baixas': {'labels': [], 'valores': []}, 
            'processos': {'labels': [], 'valores': []}
        },
        'performance_veiculos': {'labels': [], 'valores': [], 'quantidades': []}
    }
    
    if df.empty:
        return graficos
    
    try:
        # 1. Evolução mensal
        if 'data_emissao' in df.columns:
            df_temp = df[df['data_emissao'].notna() & df['valor_total'].notna()].copy()
            if not df_temp.empty:
                df_temp['mes_ano'] = df_temp['data_emissao'].dt.to_period('M')
                receita_mensal = df_temp.groupby('mes_ano').agg({
                    'valor_total': 'sum',
                    'numero_cte': 'count'
                }).reset_index()
                
                # Pegar últimos 12 meses
                receita_mensal = receita_mensal.tail(12)
                
                graficos['evolucao_mensal'] = {
                    'labels': [str(periodo) for periodo in receita_mensal['mes_ano']],
                    'valores': [float(valor) for valor in receita_mensal['valor_total']],
                    'quantidades': [int(qtd) for qtd in receita_mensal['numero_cte']]
                }
        
        # 2. Top 10 clientes
        if 'destinatario_nome' in df.columns:
            top_clientes = df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False).head(10)
            
            graficos['top_clientes'] = {
                'labels': [str(cliente) for cliente in top_clientes.index],
                'valores': [float(valor) for valor in top_clientes.values]
            }
        
        # 3. Distribuição de status
        baixas_com = len(df[df['data_baixa'].notna()])
        baixas_sem = len(df[df['data_baixa'].isna()])
        
        processos_completos = len(df[(df['data_emissao'].notna()) & (df['primeiro_envio'].notna()) & (df['data_atesto'].notna()) & (df['envio_final'].notna())])
        processos_incompletos = len(df) - processos_completos
        
        graficos['distribuicao_status'] = {
            'baixas': {
                'labels': ['Com Baixa', 'Sem Baixa'],
                'valores': [baixas_com, baixas_sem]
            },
            'processos': {
                'labels': ['Completos', 'Incompletos'],
                'valores': [processos_completos, processos_incompletos]
            }
        }
        
        # 4. Performance de veículos
        if 'veiculo_placa' in df.columns:
            veiculos = df.groupby('veiculo_placa').agg({
                'valor_total': 'sum',
                'numero_cte': 'count'
            }).sort_values('valor_total', ascending=False).head(10)
            
            graficos['performance_veiculos'] = {
                'labels': [str(veiculo) for veiculo in veiculos.index],
                'valores': [float(valor) for valor in veiculos['valor_total']],
                'quantidades': [int(qtd) for qtd in veiculos['numero_cte']]
            }
        
    except Exception as e:
        print(f"Erro ao gerar dados dos gráficos: {e}")
    
    return graficos

def metricas_vazias():
    """Retorna métricas zeradas"""
    return {
        'total_ctes': 0, 'clientes_unicos': 0, 'valor_total': 0.0,
        'faturas_pagas': 0, 'faturas_pendentes': 0, 'valor_pago': 0.0,
        'valor_pendente': 0.0, 'veiculos_ativos': 0,
        'processos_completos': 0, 'processos_incompletos': 0,
        'ticket_medio': 0.0, 'maior_valor': 0.0, 'menor_valor': 0.0,
        'receita_mensal_media': 0.0, 'crescimento_mensal': 0.0,
        'taxa_conclusao': 0.0, 'taxa_pagamento': 0.0, 'taxa_faturamento': 0.0
    }

def graficos_vazios():
    """Retorna estrutura vazia para gráficos"""
    return {
        'evolucao_mensal': {'labels': [], 'valores': [], 'quantidades': []},
        'top_clientes': {'labels': [], 'valores': []},
        'distribuicao_status': {
            'baixas': {'labels': [], 'valores': []}, 
            'processos': {'labels': [], 'valores': []}
        },
        'performance_veiculos': {'labels': [], 'valores': [], 'quantidades': []}
    }

@bp.route('/api/graficos')
@login_required
def api_graficos():
    """API para dados dos gráficos - REDIRECIONAMENTO"""
    # Redirecionar para a API de métricas que já inclui os gráficos
    return api_metricas()

@bp.route('/relatorios')
@login_required
def relatorios():
    """Página de relatórios"""
    return render_template('dashboard/relatorios.html')

@bp.route('/api/relatorio/executivo')
@login_required
def api_relatorio_executivo():
    """Gera relatório executivo em JSON"""
    try:
        # Usar o cálculo completo
        response_data = calcular_metricas_completas()
        data = response_data.get_json()
        
        if not data.get('success'):
            raise Exception(data.get('error', 'Erro desconhecido'))
        
        metricas = data['metricas']
        alertas = data['alertas']
        variacoes = data.get('variacoes', {})
        
        # Montar relatório
        relatorio = {
            'titulo': 'Relatório Executivo - Dashboard Baker',
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'resumo_financeiro': {
                'total_ctes': metricas['total_ctes'],
                'valor_total': metricas['valor_total'],
                'receita_realizada': metricas['valor_pago'],
                'valor_pendente': metricas['valor_pendente'],
                'ticket_medio': metricas['ticket_medio'],
                'crescimento_mensal': metricas['crescimento_mensal']
            },
            'indicadores_chave': {
                'taxa_conclusao': metricas['taxa_conclusao'],
                'taxa_pagamento': metricas['taxa_pagamento'],
                'taxa_faturamento': metricas['taxa_faturamento'],
                'clientes_ativos': metricas['clientes_unicos'],
                'veiculos_ativos': metricas['veiculos_ativos']
            },
            'alertas_criticos': {
                'total_alertas': sum(alerta.get('qtd', 0) for alerta in alertas.values()),
                'valor_em_risco': sum(alerta.get('valor', 0) for alerta in alertas.values()),
                'detalhes': alertas
            },
            'performance_temporal': variacoes
        }
        
        return jsonify({
            'success': True,
            'relatorio': relatorio
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# ADICIONAR ao final de app/routes/dashboard.py

@bp.route('/api/metricas-clean')
@login_required
def api_metricas_clean():
    '''API de métricas SEM debug excessivo'''
    try:
        from app.services.metricas_service_clean import MetricasService
        resultado = MetricasService.calcular_metricas_resumidas()
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular métricas',
            'metricas': {},
            'alertas': {},
            'variacoes': {}
        })
