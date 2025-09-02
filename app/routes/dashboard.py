# app/routes/dashboard.py
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Mantido: compat para serviços opcionais
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
try:
    from app.services.metricas_service import MetricasService
    METRICAS_SERVICE_OK = True
except Exception as e:
    print(f"⚠️ MetricasService não disponível: {e}")
    METRICAS_SERVICE_OK = False

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html')

@bp.route('/api/debug')
@login_required
def api_debug():
    """Diagnóstico rápido do backend e conversão"""
    try:
        total_ctes = CTE.query.count()
        exemplos = CTE.query.limit(5).all()
        exemplos_dict = []
        for cte in exemplos:
            try:
                exemplos_dict.append({
                    'numero_cte': cte.numero_cte,
                    'valor_total': float(cte.valor_total or 0),
                    'destinatario_nome': cte.destinatario_nome,
                    'has_baixa': bool(cte.data_baixa is not None),
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
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/metricas')
@login_required
def api_metricas():
    """Métricas principais do dashboard (corrigidas)"""
    try:
        return _calcular_metricas_completas()
    except Exception as e:
        print(f"❌ Erro na API de métricas: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'metricas': _metricas_vazias(),
            'alertas': {},
            'variacoes': {},
            'graficos': _graficos_vazios()
        }), 500

def _carregar_df_cte() -> pd.DataFrame:
    """
    🔧 FUNÇÃO CORRIGIDA - Carrega dados usando SQL string ao invés de SQLAlchemy statement
    """
    try:
        # ✅ CORREÇÃO PRINCIPAL: Usar SQL string diretamente
        sql_query = """
            SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                   data_emissao, numero_fatura, data_baixa, observacao,
                   data_inclusao_fatura, data_envio_processo, primeiro_envio,
                   data_rq_tmc, data_atesto, envio_final, origem_dados
            FROM dashboard_baker 
            ORDER BY numero_cte DESC
        """
        
        # ✅ Usando connection() ao invés de bind para evitar warnings
        df = pd.read_sql_query(sql_query, db.engine)
        
        # Consertos de tipo
        if 'valor_total' in df.columns:
            df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)

        date_cols = [
            'data_emissao', 'data_baixa', 'data_inclusao_fatura', 'data_envio_processo',
            'primeiro_envio', 'data_rq_tmc', 'data_atesto', 'envio_final'
        ]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        print(f"✅ DataFrame carregado: {len(df)} registros")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar DataFrame: {e}")
        # Fallback: retornar DataFrame vazio com colunas necessárias
        return pd.DataFrame(columns=[
            'numero_cte', 'destinatario_nome', 'veiculo_placa', 'valor_total',
            'data_emissao', 'numero_fatura', 'data_baixa', 'observacao',
            'data_inclusao_fatura', 'data_envio_processo', 'primeiro_envio',
            'data_rq_tmc', 'data_atesto', 'envio_final', 'origem_dados'
        ])

def _calcular_metricas_completas():
    """Calcula métricas, alertas, variações e dados para gráficos."""
    df = _carregar_df_cte()

    if df.empty:
        print("⚠️ DataFrame vazio - retornando métricas zeradas")
        return jsonify({
            'success': True,
            'metricas': _metricas_vazias(),
            'alertas': {},
            'variacoes': {},
            'graficos': _graficos_vazios(),
            'timestamp': datetime.now().isoformat(),
            'total_registros': 0
        })

    print(f"📊 Calculando métricas para {len(df)} registros")
    metricas = _metricas_basicas(df)
    alertas = calcular_alertas_inteligentes(df)  # ✅ CORRIGIDO!
    variacoes = _variacoes(df)
    graficos = _graficos(df)

    return jsonify({
        'success': True,
        'metricas': metricas,
        'alertas': alertas,
        'variacoes': variacoes,
        'graficos': graficos,
        'timestamp': datetime.now().isoformat(),
        'total_registros': int(len(df))
    })

def _metricas_basicas(df: pd.DataFrame) -> dict:
    """Calcula métricas básicas com tratamento de erros robusto"""
    if df.empty:
        return _metricas_vazias()

    try:
        total_ctes = int(len(df))
        clientes_unicos = int(df['destinatario_nome'].nunique()) if 'destinatario_nome' in df.columns else 0
        veiculos_ativos = int(df['veiculo_placa'].nunique()) if 'veiculo_placa' in df.columns else 0

        # Garantir que valor_total seja numérico
        valores = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)
        valor_total = float(valores.sum())

        # Métricas de baixa
        has_baixa = df['data_baixa'].notna() if 'data_baixa' in df.columns else pd.Series([False] * len(df))
        f_pagas = int(has_baixa.sum())
        f_pend = int((~has_baixa).sum())
        valor_pago = float(valores[has_baixa].sum()) if any(has_baixa) else 0.0
        valor_pend = float(valores[~has_baixa].sum()) if any(~has_baixa) else valor_total

        # Métricas de fatura
        tem_fatura = False
        if 'numero_fatura' in df.columns:
            tem_fatura = df['numero_fatura'].notna() & (df['numero_fatura'] != '')
        
        ctes_com_fatura = int(tem_fatura.sum()) if hasattr(tem_fatura, 'sum') else 0
        ctes_sem_fatura = int(total_ctes - ctes_com_fatura)
        valor_com_fatura = float(valores[tem_fatura].sum()) if hasattr(tem_fatura, 'sum') and any(tem_fatura) else 0.0
        valor_sem_fatura = float(valor_total - valor_com_fatura)

        # Processos completos
        proc_completos = 0
        if all(col in df.columns for col in ['data_emissao', 'primeiro_envio', 'data_atesto', 'envio_final']):
            proc_completos_mask = (
                df['data_emissao'].notna() &
                df['primeiro_envio'].notna() &
                df['data_atesto'].notna() &
                df['envio_final'].notna()
            )
            proc_completos = int(proc_completos_mask.sum())
        
        proc_incompletos = int(total_ctes - proc_completos)

        # Estatísticas de valor
        ticket_medio = float(valores.mean()) if total_ctes > 0 else 0.0
        maior_valor = float(valores.max()) if total_ctes > 0 else 0.0
        menor_valor = float(valores.min()) if total_ctes > 0 else 0.0

        # Receita mensal e crescimento
        receita_mensal_media = 0.0
        crescimento_mensal = 0.0
        if 'data_emissao' in df.columns and df['data_emissao'].notna().any():
            try:
                tmp = df[df['data_emissao'].notna()].copy()
                tmp['mes_ano'] = tmp['data_emissao'].dt.to_period('M')
                receita = tmp.groupby('mes_ano')['valor_total'].sum()
                if len(receita) > 0:
                    receita_mensal_media = float(receita.mean())
                    if len(receita) >= 2 and float(receita.iloc[-2]) > 0:
                        crescimento_mensal = float((receita.iloc[-1] - receita.iloc[-2]) / receita.iloc[-2] * 100)
            except Exception as e:
                print(f"⚠️ Erro no cálculo de receita mensal: {e}")

        return {
            'total_ctes': total_ctes,
            'clientes_unicos': clientes_unicos,
            'veiculos_ativos': veiculos_ativos,
            'valor_total': valor_total,
            'valor_pago': valor_pago,
            'valor_pendente': valor_pend,
            'faturas_pagas': f_pagas,
            'faturas_pendentes': f_pend,
            'ctes_com_fatura': ctes_com_fatura,
            'ctes_sem_fatura': ctes_sem_fatura,
            'valor_com_fatura': valor_com_fatura,
            'valor_sem_fatura': valor_sem_fatura,
            'processos_completos': proc_completos,
            'processos_incompletos': proc_incompletos,
            'ticket_medio': ticket_medio,
            'maior_valor': maior_valor,
            'menor_valor': menor_valor,
            'receita_mensal_media': receita_mensal_media,
            'crescimento_mensal': crescimento_mensal,
            'taxa_conclusao': float(proc_completos / total_ctes * 100) if total_ctes else 0.0,
            'taxa_pagamento': float(f_pagas / total_ctes * 100) if total_ctes else 0.0,
            'taxa_faturamento': float(ctes_com_fatura / total_ctes * 100) if total_ctes else 0.0
        }
        
    except Exception as e:
        print(f"❌ Erro no cálculo de métricas básicas: {e}")
        return _metricas_vazias()

def _alertas(df: pd.DataFrame) -> dict:
    """Calcula alertas inteligentes com tratamento robusto de erros"""
    alertas = {
        'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'envio_final_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'faturas_vencidas': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'ctes_sem_faturas': {'qtd': 0, 'valor': 0.0, 'lista': []}
    }
    
    if df.empty:
        return alertas
    
    try:
        hoje = pd.Timestamp.now().normalize()
        valores = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)

        def _safe_item(row, extra_field):
            """Cria item seguro para lista de alertas"""
            try:
                base = {
                    'numero_cte': int(row['numero_cte']) if pd.notna(row['numero_cte']) else 0,
                    'destinatario_nome': str(row['destinatario_nome']) if pd.notna(row['destinatario_nome']) else 'N/A',
                    'valor_total': float(valores[row.name]) if pd.notna(valores[row.name]) else 0.0
                }
                if extra_field in row and pd.notna(row[extra_field]):
                    if hasattr(row[extra_field], 'isoformat'):
                        base[extra_field] = row[extra_field].isoformat()
                    else:
                        base[extra_field] = str(row[extra_field])
                else:
                    base[extra_field] = None
                return base
            except Exception as e:
                print(f"⚠️ Erro ao criar item de alerta: {e}")
                return {'numero_cte': 0, 'destinatario_nome': 'Erro', 'valor_total': 0.0, extra_field: None}

        # 1) Primeiro envio pendente (>1 dias após emissão)
        if all(col in df.columns for col in ['data_emissao', 'primeiro_envio']):
            mask = (df['data_emissao'].notna() &
                    ((hoje - df['data_emissao']).dt.days > 10) &
                    df['primeiro_envio'].isna())
            if mask.any():
                c = df[mask]
                alertas['primeiro_envio_pendente'] = {
                    'qtd': int(len(c)),
                    'valor': float(valores[mask].sum()),
                    'lista': [_safe_item(r, 'data_emissao') for _, r in c.iterrows()]
                }

        # 2) Envio final pendente (>1 dias após atesto)
        if all(col in df.columns for col in ['data_atesto', 'envio_final']):
            mask_envio_final = (
                df['data_atesto'].notna() & 
                ((hoje - df['data_atesto']).dt.days > 1) &  # MUDAR DE 5 PARA 1
                df['envio_final'].isna()
            )
            if mask_envio_final.any():
                c = df[mask_envio_final]
                alertas['envio_final_pendente'] = {
                    'qtd': int(len(c)),
                    'valor': float(valores[mask_envio_final].sum()),
                    'lista': [_safe_item(r, 'data_atesto') for _, r in c.iterrows()]
                }

        # 3) Faturas vencidas (>90 dias do atesto, sem baixa)
        if all(col in df.columns for col in ['data_atesto', 'data_baixa']):
            mask_vencidas = (
                    df['envio_final'].notna() &  # MUDAR DE data_atesto PARA envio_final
                    ((hoje - df['envio_final']).dt.days > 90) &
                    df['data_baixa'].isna()
                )
            if mask_vencidas.any():
                c = df[mask_vencidas]
                alertas['faturas_vencidas'] = {
                    'qtd': int(len(c)),
                    'valor': float(valores[mask_vencidas].sum()),
                    'lista': [_safe_item(r, 'data_atesto') for _, r in c.iterrows()]
                }

        # 4) CTEs sem fatura (>3 dias do atesto)
        if all(col in df.columns for col in ['data_atesto', 'numero_fatura']):
            mask = (df['data_atesto'].notna() &
                    ((hoje - df['data_atesto']).dt.days > 3) &
                    (df['numero_fatura'].isna() | (df['numero_fatura'] == '')))
            if mask.any():
                c = df[mask]
                alertas['ctes_sem_faturas'] = {
                    'qtd': int(len(c)),
                    'valor': float(valores[mask].sum()),
                    'lista': [_safe_item(r, 'data_atesto') for _, r in c.iterrows()]
                }

    except Exception as e:
        print(f"⚠️ Erro no cálculo de alertas: {e}")

    return alertas

def _variacoes(df: pd.DataFrame) -> dict:
    """Calcula variações de tempo entre processos"""
    configs = [
        ('rq_tmc_primeiro_envio', 'RQ/TMC → 1º Envio', 'data_rq_tmc', 'primeiro_envio', 3),
        ('primeiro_envio_atesto', '1º Envio → Atesto', 'primeiro_envio', 'data_atesto', 7),
        ('atesto_envio_final', 'Atesto → Envio Final', 'data_atesto', 'envio_final', 2),
        ('cte_inclusao_fatura', 'CTE → Inclusão Fatura', 'data_emissao', 'data_inclusao_fatura', 2),
        ('cte_baixa', 'CTE → Baixa', 'data_emissao', 'data_baixa', 30),
    ]
    
    out = {}
    if df.empty:
        return out

    try:
        for code, nome, inicio, fim, meta in configs:
            if inicio in df.columns and fim in df.columns:
                m = df[inicio].notna() & df[fim].notna()
                if not m.any():
                    continue
                
                _dif = (df.loc[m, fim] - df.loc[m, inicio]).dt.days
                _dif = _dif[_dif >= 0]  # Apenas diferenças positivas
                
                if len(_dif) == 0:
                    continue
                
                media = float(_dif.mean())
                mediana = float(_dif.median())
                
                # Determinar performance
                if media <= meta:
                    perf = 'excelente'
                elif media <= meta * 1.5:
                    perf = 'bom'
                elif media <= meta * 2:
                    perf = 'atencao'
                else:
                    perf = 'critico'
                
                out[code] = {
                    'nome': nome,
                    'media': round(media, 1),
                    'mediana': round(mediana, 1),
                    'qtd': int(len(_dif)),
                    'meta_dias': int(meta),
                    'performance': perf,
                    'min': int(_dif.min()),
                    'max': int(_dif.max())
                }
                
    except Exception as e:
        print(f"⚠️ Erro no cálculo de variações: {e}")

    return out

def _graficos(df: pd.DataFrame) -> dict:
    """Gera dados para gráficos do dashboard"""
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
        valores = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)

        # Evolução mensal
        if 'data_emissao' in df.columns and df['data_emissao'].notna().any():
            try:
                tmp = df[df['data_emissao'].notna() & valores.notna()].copy()
                if not tmp.empty:
                    tmp['mes_ano'] = tmp['data_emissao'].dt.to_period('M')
                    receita = tmp.groupby('mes_ano').agg(
                        valor_total=('valor_total', lambda x: pd.to_numeric(x, errors='coerce').sum()),
                        qtd=('numero_cte', 'count')
                    ).reset_index().tail(12)
                    
                    if not receita.empty:
                        graficos['evolucao_mensal'] = {
                            'labels': [str(p) for p in receita['mes_ano']],
                            'valores': [float(v) for v in receita['valor_total']],
                            'quantidades': [int(q) for q in receita['qtd']]
                        }
            except Exception as e:
                print(f"⚠️ Erro na evolução mensal: {e}")

        # Top clientes
        if 'destinatario_nome' in df.columns:
            try:
                tmp_df = df.copy()
                tmp_df['valor_total'] = valores
                top = tmp_df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False).head(10)
                if not top.empty:
                    graficos['top_clientes'] = {
                        'labels': [str(i) for i in top.index],
                        'valores': [float(v) for v in top.values]
                    }
            except Exception as e:
                print(f"⚠️ Erro no top clientes: {e}")

        # Distribuição de status
        try:
            com_baixa = int(df['data_baixa'].notna().sum()) if 'data_baixa' in df.columns else 0
            sem_baixa = int(len(df) - com_baixa)
            
            proc_compl = 0
            if all(col in df.columns for col in ['data_emissao', 'primeiro_envio', 'data_atesto', 'envio_final']):
                proc_compl = int((df['data_emissao'].notna() & df['primeiro_envio'].notna() &
                                  df['data_atesto'].notna() & df['envio_final'].notna()).sum())
            proc_incompl = int(len(df) - proc_compl)
            
            graficos['distribuicao_status'] = {
                'baixas': {'labels': ['Com Baixa', 'Sem Baixa'], 'valores': [com_baixa, sem_baixa]},
                'processos': {'labels': ['Completos', 'Incompletos'], 'valores': [proc_compl, proc_incompl]}
            }
        except Exception as e:
            print(f"⚠️ Erro na distribuição de status: {e}")

        # Performance de veículos
        if 'veiculo_placa' in df.columns:
            try:
                tmp_df = df.copy()
                tmp_df['valor_total'] = valores
                v = tmp_df.groupby('veiculo_placa').agg(
                    valor_total=('valor_total', 'sum'),
                    qtd=('numero_cte', 'count')
                ).sort_values('valor_total', ascending=False).head(10)
                
                if not v.empty:
                    graficos['performance_veiculos'] = {
                        'labels': [str(i) for i in v.index],
                        'valores': [float(x) for x in v['valor_total']],
                        'quantidades': [int(x) for x in v['qtd']]
                    }
            except Exception as e:
                print(f"⚠️ Erro na performance de veículos: {e}")

    except Exception as e:
        print(f"⚠️ Erro geral nos gráficos: {e}")

    return graficos

def _metricas_vazias():
    """Retorna estrutura de métricas zeradas"""
    return {
        'total_ctes': 0, 'clientes_unicos': 0, 'valor_total': 0.0,
        'faturas_pagas': 0, 'faturas_pendentes': 0, 'valor_pago': 0.0,
        'valor_pendente': 0.0, 'veiculos_ativos': 0,
        'processos_completos': 0, 'processos_incompletos': 0,
        'ticket_medio': 0.0, 'maior_valor': 0.0, 'menor_valor': 0.0,
        'receita_mensal_media': 0.0, 'crescimento_mensal': 0.0,
        'taxa_conclusao': 0.0, 'taxa_pagamento': 0.0, 'taxa_faturamento': 0.0
    }

def _graficos_vazios():
    """Retorna estrutura de gráficos vazia"""
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
    """API de gráficos - retorna mesma estrutura de métricas"""
    return api_metricas()

@bp.route('/relatorios')
@login_required
def relatorios():
    return render_template('dashboard/relatorios.html')

@bp.route('/api/relatorio/executivo')
@login_required
def api_relatorio_executivo():
    """Gera relatório executivo baseado nas métricas"""
    try:
        data = _calcular_metricas_completas().get_json()
        if not data.get('success'):
            raise Exception(data.get('error', 'Erro desconhecido'))
        
        m = data['metricas']
        a = data['alertas']
        v = data.get('variacoes', {})
        
        relatorio = {
            'titulo': 'Relatório Executivo - Dashboard Baker',
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'resumo_financeiro': {
                'total_ctes': m['total_ctes'],
                'valor_total': m['valor_total'],
                'receita_realizada': m['valor_pago'],
                'valor_pendente': m['valor_pendente'],
                'ticket_medio': m['ticket_medio'],
                'crescimento_mensal': m['crescimento_mensal']
            },
            'indicadores_chave': {
                'taxa_conclusao': m['taxa_conclusao'],
                'taxa_pagamento': m['taxa_pagamento'],
                'taxa_faturamento': m['taxa_faturamento'],
                'clientes_ativos': m['clientes_unicos'],
                'veiculos_ativos': m['veiculos_ativos']
            },
            'alertas_criticos': {
                'total_alertas': sum(x.get('qtd', 0) for x in a.values()),
                'valor_em_risco': sum(x.get('valor', 0.0) for x in a.values()),
                'detalhes': a
            },
            'performance_temporal': v
        }
        
        return jsonify({'success': True, 'relatorio': relatorio})
        
    except Exception as e:
        print(f"❌ Erro no relatório executivo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    # ================================
# ADICIONAR ESTAS FUNÇÕES no arquivo dashboard.py
# ================================

def calcular_alertas_inteligentes(df):
    """Sistema de alertas inteligentes - VERSÃO CORRIGIDA"""
    print(f"🚨 Iniciando cálculo de alertas para {len(df)} registros")
    
    alertas = {
        'primeiro_envio_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'envio_final_pendente': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'faturas_vencidas': {'qtd': 0, 'valor': 0.0, 'lista': []},
        'ctes_sem_faturas': {'qtd': 0, 'valor': 0.0, 'lista': []}
    }

    if df.empty:
        print("⚠️ DataFrame vazio para alertas")
        return alertas

    hoje = pd.Timestamp.now().normalize()

    try:
        # 1. Primeiro envio pendente (10 dias após emissão) - ✅ MANTIDO
        print("🔍 Calculando primeiro envio pendente...")
        mask_primeiro_envio = (
            df['data_emissao'].notna() & 
            ((hoje - df['data_emissao']).dt.days > 10) &
            df['primeiro_envio'].isna()
        )
        if mask_primeiro_envio.any():
            ctes_problema = df[mask_primeiro_envio]
            lista_segura = []
            for _, row in ctes_problema.head(10).iterrows():  # Limitar a 10 por segurança
                try:
                    item = {
                        'numero_cte': int(row['numero_cte']),
                        'destinatario_nome': str(row['destinatario_nome']),
                        'valor_total': float(row['valor_total']),
                        'data_emissao': row['data_emissao'].isoformat() if pd.notna(row['data_emissao']) else None
                    }
                    lista_segura.append(item)
                except Exception as e:
                    print(f"⚠️ Erro ao processar CTE: {e}")
                    continue

            alertas['primeiro_envio_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }
            print(f"✅ Primeiro envio pendente: {len(ctes_problema)} CTEs")

        # 2. Envio Final Pendente - 🔧 CORRIGIDO: 1 dia após atesto (era 5)
        print("🔍 Calculando envio final pendente...")
        mask_envio_final = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 1) &  # MUDANÇA: 5 → 1
            df['envio_final'].isna()
        )
        if mask_envio_final.any():
            ctes_problema = df[mask_envio_final]
            lista_segura = []
            for _, row in ctes_problema.head(10).iterrows():
                try:
                    item = {
                        'numero_cte': int(row['numero_cte']),
                        'destinatario_nome': str(row['destinatario_nome']),
                        'valor_total': float(row['valor_total']),
                        'data_atesto': row['data_atesto'].isoformat() if pd.notna(row['data_atesto']) else None
                    }
                    lista_segura.append(item)
                except Exception as e:
                    print(f"⚠️ Erro ao processar CTE: {e}")
                    continue

            alertas['envio_final_pendente'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }
            print(f"✅ Envio final pendente: {len(ctes_problema)} CTEs")

        # 3. Faturas vencidas - 🔧 CORRIGIDO: 90 dias após ENVIO FINAL (era após atesto)
        print("🔍 Calculando faturas vencidas...")
        mask_vencidas = (
            df['envio_final'].notna() &  # MUDANÇA: data_atesto → envio_final
            ((hoje - df['envio_final']).dt.days > 90) &  # MUDANÇA: data_atesto → envio_final
            df['data_baixa'].isna()
        )
        if mask_vencidas.any():
            ctes_problema = df[mask_vencidas]
            lista_segura = []
            for _, row in ctes_problema.head(10).iterrows():
                try:
                    item = {
                        'numero_cte': int(row['numero_cte']),
                        'destinatario_nome': str(row['destinatario_nome']),
                        'valor_total': float(row['valor_total']),
                        'envio_final': row['envio_final'].isoformat() if pd.notna(row['envio_final']) else None  # MUDANÇA: data_atesto → envio_final
                    }
                    lista_segura.append(item)
                except Exception as e:
                    print(f"⚠️ Erro ao processar CTE: {e}")
                    continue

            alertas['faturas_vencidas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }
            print(f"✅ Faturas vencidas: {len(ctes_problema)} CTEs")

        # 4. CTEs sem faturas (3 dias após atesto) - ✅ MANTIDO
        print("🔍 Calculando CTEs sem faturas...")
        mask_sem_faturas = (
            df['data_atesto'].notna() & 
            ((hoje - df['data_atesto']).dt.days > 3) &
            (df['numero_fatura'].isna() | (df['numero_fatura'] == ''))
        )
        if mask_sem_faturas.any():
            ctes_problema = df[mask_sem_faturas]
            lista_segura = []
            for _, row in ctes_problema.head(10).iterrows():
                try:
                    item = {
                        'numero_cte': int(row['numero_cte']),
                        'destinatario_nome': str(row['destinatario_nome']),
                        'valor_total': float(row['valor_total']),
                        'data_atesto': row['data_atesto'].isoformat() if pd.notna(row['data_atesto']) else None
                    }
                    lista_segura.append(item)
                except Exception as e:
                    print(f"⚠️ Erro ao processar CTE: {e}")
                    continue

            alertas['ctes_sem_faturas'] = {
                'qtd': len(ctes_problema),
                'valor': float(ctes_problema['valor_total'].sum()),
                'lista': lista_segura
            }
            print(f"✅ CTEs sem faturas: {len(ctes_problema)} CTEs")

        print("✅ Todos os alertas calculados com sucesso!")

    except Exception as e:
        print(f"⚠️ Erro no cálculo de alertas: {str(e)}")
        import traceback
        traceback.print_exc()

    return alertas


def _variacoes(df):
    """Calcula variações de tempo entre processos"""
    print(f"⏱️ Calculando variações para {len(df)} registros")
    
    configs = [
        ('rq_tmc_primeiro_envio', 'RQ/TMC → 1º Envio', 'data_rq_tmc', 'primeiro_envio', 3),
        ('primeiro_envio_atesto', '1º Envio → Atesto', 'primeiro_envio', 'data_atesto', 7),
        ('atesto_envio_final', 'Atesto → Envio Final', 'data_atesto', 'envio_final', 2),
        ('cte_inclusao_fatura', 'CTE → Inclusão Fatura', 'data_emissao', 'data_inclusao_fatura', 2),
        ('cte_baixa', 'CTE → Baixa', 'data_emissao', 'data_baixa', 30),
    ]
    
    out = {}
    if df.empty:
        return out

    try:
        for code, nome, inicio, fim, meta in configs:
            if inicio in df.columns and fim in df.columns:
                m = df[inicio].notna() & df[fim].notna()
                if not m.any():
                    continue
                
                _dif = (df.loc[m, fim] - df.loc[m, inicio]).dt.days
                _dif = _dif[_dif >= 0]  # Apenas diferenças positivas
                
                if len(_dif) == 0:
                    continue
                
                media = float(_dif.mean())
                mediana = float(_dif.median())
                
                # Determinar performance
                if media <= meta:
                    perf = 'excelente'
                elif media <= meta * 1.5:
                    perf = 'bom'
                elif media <= meta * 2:
                    perf = 'atencao'
                else:
                    perf = 'critico'
                
                out[code] = {
                    'nome': nome,
                    'media': round(media, 1),
                    'mediana': round(mediana, 1),
                    'qtd': int(len(_dif)),
                    'meta_dias': int(meta),
                    'performance': perf,
                    'min': int(_dif.min()),
                    'max': int(_dif.max())
                }
                print(f"✅ {nome}: {len(_dif)} registros, média {media:.1f} dias")
                
    except Exception as e:
        print(f"⚠️ Erro no cálculo de variações: {e}")

    return out


def _graficos(df):
    """Gera dados para gráficos do dashboard"""
    print(f"📈 Gerando gráficos para {len(df)} registros")
    
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
        valores = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0)

        # Evolução mensal
        if 'data_emissao' in df.columns and df['data_emissao'].notna().any():
            try:
                tmp = df[df['data_emissao'].notna() & valores.notna()].copy()
                if not tmp.empty:
                    tmp['mes_ano'] = tmp['data_emissao'].dt.to_period('M')
                    receita = tmp.groupby('mes_ano').agg(
                        valor_total=('valor_total', lambda x: pd.to_numeric(x, errors='coerce').sum()),
                        qtd=('numero_cte', 'count')
                    ).reset_index().tail(12)
                    
                    if not receita.empty:
                        graficos['evolucao_mensal'] = {
                            'labels': [str(p) for p in receita['mes_ano']],
                            'valores': [float(v) for v in receita['valor_total']],
                            'quantidades': [int(q) for q in receita['qtd']]
                        }
                        print(f"✅ Evolução mensal: {len(receita)} períodos")
            except Exception as e:
                print(f"⚠️ Erro na evolução mensal: {e}")

        # Top clientes
        if 'destinatario_nome' in df.columns:
            try:
                tmp_df = df.copy()
                tmp_df['valor_total'] = valores
                top = tmp_df.groupby('destinatario_nome')['valor_total'].sum().sort_values(ascending=False).head(5)
                if not top.empty:
                    graficos['top_clientes'] = {
                        'labels': [str(i) for i in top.index],
                        'valores': [float(v) for v in top.values]
                    }
                    print(f"✅ Top clientes: {len(top)} clientes")
            except Exception as e:
                print(f"⚠️ Erro no top clientes: {e}")

        # Distribuição de status
        try:
            com_baixa = int(df['data_baixa'].notna().sum()) if 'data_baixa' in df.columns else 0
            sem_baixa = int(len(df) - com_baixa)
            
            proc_compl = 0
            if all(col in df.columns for col in ['data_emissao', 'primeiro_envio', 'data_atesto', 'envio_final']):
                proc_compl = int((df['data_emissao'].notna() & df['primeiro_envio'].notna() &
                                  df['data_atesto'].notna() & df['envio_final'].notna()).sum())
            proc_incompl = int(len(df) - proc_compl)
            
            graficos['distribuicao_status'] = {
                'baixas': {'labels': ['Com Baixa', 'Sem Baixa'], 'valores': [com_baixa, sem_baixa]},
                'processos': {'labels': ['Completos', 'Incompletos'], 'valores': [proc_compl, proc_incompl]}
            }
            print(f"✅ Distribuição: {com_baixa} com baixa, {proc_compl} completos")
        except Exception as e:
            print(f"⚠️ Erro na distribuição de status: {e}")

        # Performance de veículos
        if 'veiculo_placa' in df.columns:
            try:
                tmp_df = df.copy()
                tmp_df['valor_total'] = valores
                v = tmp_df.groupby('veiculo_placa').agg(
                    valor_total=('valor_total', 'sum'),
                    qtd=('numero_cte', 'count')
                ).sort_values('valor_total', ascending=False).head(10)
                
                if not v.empty:
                    graficos['performance_veiculos'] = {
                        'labels': [str(i) for i in v.index],
                        'valores': [float(x) for x in v['valor_total']],
                        'quantidades': [int(x) for x in v['qtd']]
                    }
                    print(f"✅ Performance veículos: {len(v)} veículos")
            except Exception as e:
                print(f"⚠️ Erro na performance de veículos: {e}")

        print("✅ Gráficos gerados com sucesso!")

    except Exception as e:
        print(f"⚠️ Erro geral nos gráficos: {e}")

    return graficos