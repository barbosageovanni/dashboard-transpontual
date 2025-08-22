#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes para Análise Financeira - Dashboard Baker Flask
app/routes/analise_financeira.py
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.services.analise_financeira_service import AnaliseFinanceiraService
from datetime import datetime
import logging
from flask import send_file, make_response
from app.services.exportacao_service import ExportacaoService

bp = Blueprint('analise_financeira', __name__, url_prefix='/analise-financeira')

@bp.route('/')
@login_required
def index():
    """Página principal da análise financeira"""
    return render_template('analise_financeira/index.html')

@bp.route('/api/analise-completa')
@login_required
def api_analise_completa():
    """API para análise financeira completa"""
    try:
        # Parâmetros de filtro
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        # Validar filtro de dias
        if filtro_dias not in [15, 30, 90, 180, 360]:
            return jsonify({
                'success': False,
                'error': 'Período inválido. Use: 15, 30, 90, 180 ou 360 dias'
            }), 400
        
        # Processar filtro de cliente
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        return jsonify({
            'success': True,
            'analise': analise,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Parâmetro inválido: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro na API de análise financeira: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@bp.route('/api/clientes')
@login_required
def api_lista_clientes():
    """API para lista de clientes (filtro)"""
    try:
        clientes = AnaliseFinanceiraService.obter_lista_clientes()
        
        return jsonify({
            'success': True,
            'clientes': clientes,
            'total': len(clientes)
        })
        
    except Exception as e:
        logging.error(f"Erro ao obter lista de clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao carregar lista de clientes'
        }), 500

@bp.route('/api/receita-mensal')
@login_required
def api_receita_mensal():
    """API específica para receita mensal"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        return jsonify({
            'success': True,
            'receita_mensal': analise['receita_mensal'],
            'graficos': {
                'receita_mensal': analise['graficos']['receita_mensal'],
                'tendencia_linear': analise['graficos']['tendencia_linear']
            }
        })
        
    except Exception as e:
        logging.error(f"Erro na API de receita mensal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular receita mensal'
        }), 500

@bp.route('/api/concentracao-clientes')
@login_required
def api_concentracao_clientes():
    """API específica para concentração de clientes"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=None  # Não filtrar por cliente para concentração
        )
        
        return jsonify({
            'success': True,
            'concentracao_clientes': analise['concentracao_clientes'],
            'stress_test': analise['stress_test_receita'],
            'graficos': {
                'concentracao_clientes': analise['graficos']['concentracao_clientes']
            }
        })
        
    except Exception as e:
        logging.error(f"Erro na API de concentração de clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular concentração de clientes'
        }), 500

@bp.route('/api/tempo-cobranca')
@login_required
def api_tempo_cobranca():
    """API específica para análise de tempo de cobrança"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        return jsonify({
            'success': True,
            'tempo_cobranca': analise['tempo_medio_cobranca'],
            'graficos': {
                'tempo_cobranca': analise['graficos']['tempo_cobranca'],
                'distribuicao_valores': analise['graficos']['distribuicao_valores']
            }
        })
        
    except Exception as e:
        logging.error(f"Erro na API de tempo de cobrança: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular tempo de cobrança'
        }), 500

@bp.route('/api/tendencia')
@login_required
def api_tendencia():
    """API específica para análise de tendência"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        return jsonify({
            'success': True,
            'tendencia_linear': analise['tendencia_linear'],
            'ticket_medio': analise['ticket_medio'],
            'graficos': {
                'tendencia_linear': analise['graficos']['tendencia_linear'],
                'receita_mensal': analise['graficos']['receita_mensal']
            }
        })
        
    except Exception as e:
        logging.error(f"Erro na API de tendência: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular tendência'
        }), 500

@bp.route('/api/resumo-executivo')
@login_required
def api_resumo_executivo():
    """API para resumo executivo (dashboard principal)"""
    try:
        # Análise padrão (últimos 180 dias)
        analise = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=360)
        
        # Montar resumo executivo
        resumo = {
            'receita_atual': analise['receita_mensal']['receita_mes_corrente'],
            'variacao_mensal': analise['receita_mensal']['variacao_percentual'],
            'ticket_medio': analise['ticket_medio']['valor'],
            'tempo_medio_cobranca': analise['tempo_medio_cobranca']['dias_medio'],
            'concentracao_top5': analise['concentracao_clientes']['percentual_top5'],
            'tendencia_inclinacao': analise['tendencia_linear']['inclinacao'],
            'previsao_proximo_mes': analise['tendencia_linear']['previsao_proximo_mes'],
            'maior_cliente': analise['concentracao_clientes']['top_clientes'][0] if analise['concentracao_clientes']['top_clientes'] else None
        }
        
        return jsonify({
            'success': True,
            'resumo': resumo,
            'periodo_analise': analise['resumo_filtro']
        })
        
    except Exception as e:
        logging.error(f"Erro na API de resumo executivo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao gerar resumo executivo'
        }), 500

@bp.route('/api/exportar')
@login_required
def api_exportar():
    """API para exportar dados da análise"""
    try:
        formato = request.args.get('formato', 'json').lower()
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise completa
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        if formato == 'json':
            return jsonify({
                'success': True,
                'dados': analise,
                'metadata': {
                    'gerado_em': datetime.now().isoformat(),
                    'formato': 'json',
                    'filtros_aplicados': {
                        'periodo_dias': filtro_dias,
                        'cliente': filtro_cliente
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Formato não suportado. Use: json'
            }), 400
            
    except Exception as e:
        logging.error(f"Erro na API de exportação: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao exportar dados'
        }), 500

# Tratamento de erros específicos do blueprint
@bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado'
    }), 404

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor'
    }), 500

# 🆕 NOVAS ROTAS DE EXPORTAÇÃO

@bp.route('/api/exportar/json')
@login_required
def api_exportar_json():
    """API para exportar dados em JSON"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise completa
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        # Metadata
        metadata = {
            'gerado_em': datetime.now().isoformat(),
            'formato': 'json',
            'versao': '1.0',
            'filtros_aplicados': {
                'periodo_dias': filtro_dias,
                'cliente': filtro_cliente
            },
            'fonte': 'Dashboard Baker - Análise Financeira'
        }
        
        # Gerar JSON
        json_content = ExportacaoService.exportar_json(analise, metadata)
        
        # Criar response
        response = make_response(json_content)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=analise_financeira_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return response
        
    except Exception as e:
        logging.error(f"Erro na exportação JSON: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao exportar JSON'
        }), 500

@bp.route('/api/exportar/excel')
@login_required
def api_exportar_excel():
    """API para exportar dados em Excel"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise completa
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        # Metadata
        metadata = {
            'gerado_em': datetime.now().isoformat(),
            'formato': 'excel',
            'filtros_aplicados': {
                'periodo_dias': filtro_dias,
                'cliente': filtro_cliente
            }
        }
        
        # Gerar Excel
        excel_buffer = ExportacaoService.exportar_excel(analise, metadata)
        
        # Criar nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'analise_financeira_{timestamp}.xlsx'
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logging.error(f"Erro na exportação Excel: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao exportar Excel'
        }), 500

@bp.route('/api/exportar/csv')
@login_required
def api_exportar_csv():
    """API para exportar dados em CSV"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        aba = request.args.get('aba', 'resumo')  # resumo, clientes, receita
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise completa
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        # Gerar CSV
        csv_content = ExportacaoService.exportar_csv(analise, aba)
        
        # Criar response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'analise_financeira_{aba}_{timestamp}.csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        logging.error(f"Erro na exportação CSV: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao exportar CSV'
        }), 500

@bp.route('/api/exportar/pdf')
@login_required
def api_exportar_pdf():
    """API para exportar relatório em PDF"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise completa
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        # Metadata
        metadata = {
            'gerado_em': datetime.now().isoformat(),
            'formato': 'pdf',
            'filtros_aplicados': {
                'periodo_dias': filtro_dias,
                'cliente': filtro_cliente
            }
        }
        
        # Gerar PDF
        pdf_buffer = ExportacaoService.exportar_pdf(analise, metadata)
        
        # Criar nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'relatorio_analise_financeira_{timestamp}.pdf'
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logging.error(f"Erro na exportação PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao exportar PDF'
        }), 500

# 🆕 ROTA PARA EXPORTAÇÃO MÚLTIPLA
@bp.route('/api/exportar/multiplo')
@login_required
def api_exportar_multiplo():
    """API para exportar em múltiplos formatos (ZIP)"""
    try:
        import zipfile
        from io import BytesIO
        
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        formatos = request.args.getlist('formatos')  # json,excel,csv,pdf
        
        if not formatos:
            formatos = ['json', 'excel', 'csv']  # Padrão (PDF é pesado)
        
        if filtro_cliente and filtro_cliente.lower() in ['todos', 'all', '']:
            filtro_cliente = None
        
        # Gerar análise uma vez
        analise = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )
        
        # Metadata
        metadata = {
            'gerado_em': datetime.now().isoformat(),
            'formatos': formatos,
            'filtros_aplicados': {
                'periodo_dias': filtro_dias,
                'cliente': filtro_cliente
            }
        }
        
        # Criar ZIP
        zip_buffer = BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # JSON
            if 'json' in formatos:
                json_content = ExportacaoService.exportar_json(analise, metadata)
                zip_file.writestr(f'analise_financeira_{timestamp}.json', json_content)
            
            # Excel
            if 'excel' in formatos:
                excel_buffer = ExportacaoService.exportar_excel(analise, metadata)
                zip_file.writestr(f'analise_financeira_{timestamp}.xlsx', excel_buffer.getvalue())
            
            # CSV (múltiplas abas)
            if 'csv' in formatos:
                for aba in ['resumo', 'clientes', 'receita']:
                    csv_content = ExportacaoService.exportar_csv(analise, aba)
                    zip_file.writestr(f'analise_financeira_{aba}_{timestamp}.csv', csv_content.encode('utf-8'))
            
            # PDF
            if 'pdf' in formatos:
                pdf_buffer = ExportacaoService.exportar_pdf(analise, metadata)
                zip_file.writestr(f'relatorio_analise_financeira_{timestamp}.pdf', pdf_buffer.getvalue())
        
        zip_buffer.seek(0)
        
        # Retornar ZIP
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'analise_financeira_completa_{timestamp}.zip'
        )
        
    except Exception as e:
        logging.error(f"Erro na exportação múltipla: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao exportar múltiplos formatos'
        }), 500

# 🆕 ROTA PARA METADADOS DE EXPORTAÇÃO
@bp.route('/api/exportar/info')
@login_required
def api_exportar_info():
    """API para informações sobre exportação disponível"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 360))
        filtro_cliente = request.args.get('filtro_cliente', '').strip()
        
        # Obter estatísticas básicas
        resumo = AnaliseFinanceiraService.gerar_analise_completa(
            filtro_dias=filtro_dias,
            filtro_cliente=filtro_cliente
        )['resumo_filtro']
        
        info = {
            'formatos_disponiveis': ['json', 'excel', 'csv', 'pdf'],
            'abas_csv': ['resumo', 'clientes', 'receita'],
            'tamanho_estimado': {
                'json': '< 100KB',
                'excel': '< 500KB',
                'csv': '< 50KB',
                'pdf': '< 1MB'
            },
            'resumo_dados': resumo,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'info': info
        })
        
    except Exception as e:
        logging.error(f"Erro ao obter info de exportação: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao obter informações'
        }), 500

# 🆕 NOVA ROTA: Faturamento por Inclusão de Fatura
@bp.route('/api/faturamento-inclusao')
@login_required
def api_faturamento_inclusao():
    """API para faturamento baseado em data_inclusao_fatura"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 30))
        
        # Validar filtro
        if filtro_dias not in [7,15,30, 60, 90]:
            return jsonify({
                'success': False,
                'error': 'Período inválido. Use: 7, 15, 30, 60 ou 90 dias'
            }), 400
        
        # Obter dados
        dados = AnaliseFinanceiraService.obter_faturamento_por_inclusao(filtro_dias)
        
        return jsonify({
            'success': True,
            'dados': dados,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Parâmetro inválido: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro na API de faturamento por inclusão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500