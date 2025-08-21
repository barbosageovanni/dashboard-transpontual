from flask import (
    Blueprint, render_template, jsonify, request, redirect, url_for,
    flash, send_file, make_response, current_app
)
from flask_login import login_required, current_user
from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
import pandas as pd
from io import BytesIO
import tempfile
import os
from app.services.importacao_service import ImportacaoService
from werkzeug.utils import secure_filename

bp = Blueprint('ctes', __name__, url_prefix='/ctes')

# =============================================================================
# LISTAGEM / API
# =============================================================================
@bp.route('/')
@bp.route('/listar')
@login_required
def listar():
    """Página principal de listagem de CTEs"""
    return render_template('ctes/index.html')

@bp.route('/api/listar')
@login_required
def api_listar():
    """API para listar CTEs com filtros avançados"""
    try:
        # Parâmetros de busca
        search = request.args.get('search', '').strip()
        status_baixa = request.args.get('status_baixa', '')
        status_processo = request.args.get('status_processo', '')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        # Query base
        query = CTE.query

        # Filtro de busca por texto
        if search:
            try:
                if search.isdigit():
                    numero_cte = int(search)
                    search_filter = CTE.numero_cte == numero_cte
                else:
                    search_pattern = f'%{search}%'
                    search_filter = or_(
                        CTE.destinatario_nome.ilike(search_pattern),
                        CTE.numero_fatura.ilike(search_pattern),
                        CTE.veiculo_placa.ilike(search_pattern),
                        CTE.observacao.ilike(search_pattern)
                    )
                query = query.filter(search_filter)
            except Exception as e:
                current_app.logger.warning(f"Erro no filtro de busca: {e}")

        # Filtro por status de baixa
        if status_baixa == 'com_baixa':
            query = query.filter(CTE.data_baixa.isnot(None))
        elif status_baixa == 'sem_baixa':
            query = query.filter(CTE.data_baixa.is_(None))

        # Filtro por status de processo
        if status_processo == 'completo':
            query = query.filter(
                and_(
                    CTE.data_emissao.isnot(None),
                    CTE.primeiro_envio.isnot(None),
                    CTE.data_atesto.isnot(None),
                    CTE.envio_final.isnot(None)
                )
            )
        elif status_processo == 'incompleto':
            query = query.filter(
                or_(
                    CTE.data_emissao.is_(None),
                    CTE.primeiro_envio.is_(None),
                    CTE.data_atesto.is_(None),
                    CTE.envio_final.is_(None)
                )
            )

        # Filtro por período
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao >= data_inicio_obj)
            except ValueError:
                pass

        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao <= data_fim_obj)
            except ValueError:
                pass

        # Executar query
        pagination = query.order_by(CTE.numero_cte.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Converter para dict
        ctes = []
        for cte in pagination.items:
            try:
                ctes.append(cte.to_dict())
            except Exception as e:
                current_app.logger.warning(f"Erro ao converter CTE {cte.numero_cte}: {e}")
                ctes.append({
                    'numero_cte': cte.numero_cte,
                    'destinatario_nome': cte.destinatario_nome or '',
                    'valor_total': float(cte.valor_total or 0),
                    'data_emissao': cte.data_emissao.isoformat() if cte.data_emissao else None,
                    'has_baixa': cte.data_baixa is not None,
                    'processo_completo': False,
                    'status_processo': 'Erro'
                })

        return jsonify({
            'success': True,
            'ctes': ctes,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })

    except Exception as e:
        current_app.logger.exception("Erro na listagem")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# CRUD / API COMPAT
# =============================================================================
@bp.route('/api/inserir', methods=['POST'])
@login_required
def api_inserir():
    """API para inserir novo CTE - compatibilidade com frontend"""
    try:
        dados = request.get_json()

        if not dados.get('numero_cte'):
            return jsonify({'success': False, 'message': 'Número do CTE é obrigatório'}), 400

        if not dados.get('valor_total'):
            return jsonify({'success': False, 'message': 'Valor total é obrigatório'}), 400

        # Verificar se CTE já existe
        cte_existente = CTE.buscar_por_numero(dados['numero_cte'])
        if cte_existente:
            return jsonify({'success': False, 'message': 'CTE já existe'}), 400

        # Criar CTE
        sucesso, resultado = CTE.criar_cte(dados)

        if sucesso:
            return jsonify({
                'success': True,
                'message': 'CTE inserido com sucesso',
                'cte': resultado.to_dict()
            })
        else:
            return jsonify({'success': False, 'message': resultado}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/buscar/<int:numero_cte>')
@login_required
def api_buscar(numero_cte):
    """API para buscar CTE específico - compatibilidade com frontend"""
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': 'CTE não encontrado'}), 404

        return jsonify({'success': True, 'cte': cte.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/atualizar/<int:numero_cte>', methods=['PUT'])
@login_required
def api_atualizar(numero_cte):
    """API para atualizar CTE"""
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': 'CTE não encontrado'}), 404

        dados = request.get_json()
        sucesso, mensagem = cte.atualizar(dados)

        if sucesso:
            return jsonify({'success': True, 'message': mensagem, 'cte': cte.to_dict()})
        else:
            return jsonify({'success': False, 'message': mensagem}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/excluir/<int:numero_cte>', methods=['DELETE'])
@login_required
def api_excluir(numero_cte):
    """API para excluir CTE"""
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': 'CTE não encontrado'}), 404

        db.session.delete(cte)
        db.session.commit()

        return jsonify({'success': True, 'message': f'CTE {numero_cte} excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# =============================================================================
# TEMPLATES PARA ATUALIZAÇÃO EM LOTE
# =============================================================================
@bp.route('/template-atualizacao')
@login_required
def template_atualizacao():
    """Baixa um CSV-modelo para atualização em lote de CTEs (todos os campos editáveis)."""
    headers = [
        "numero_cte",
        "destinatario_nome",
        "valor_total",
        "veiculo_placa",
        "data_emissao",
        "data_inclusao_fatura",
        "numero_fatura",
        "primeiro_envio",
        "envio_final",
        "data_atesto",
        "data_baixa",
        "status_baixa",
        "status_processo",
        "observacao",
    ]

    # Exemplos com todas as colunas preenchidas (datas em dd/mm/aaaa)
    amostras = [
        ["1001", "Cliente A", "5500.00", "ABC1A23",
         "01/01/2025", "05/01/2025", "NF001", "06/01/2025", "10/01/2025",
         "12/01/2025", "15/01/2025", "Pago", "Completo", "Exemplo de atualização"],
        ["1002", "Cliente B", "3200.50", "XYZ4B56",
         "02/01/2025", "", "NF002", "08/01/2025", "",
         "", "", "Pendente", "Em andamento", "Pendente de baixa"],
        ["1003", "Cliente C", "7800.00", "DEF7C89",
         "03/01/2025", "07/01/2025", "NF003", "", "20/01/2025",
         "22/01/2025", "25/01/2025", "Pago", "Completo", "Concluído"],
    ]

    linhas = [",".join(headers)]
    for r in amostras:
        linhas.append(",".join(str(x) for x in r))

    csv_content = "\n".join(linhas) + "\n"
    resp = make_response(csv_content)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = 'attachment; filename="template_atualizacao_ctes.csv"'
    return resp


@bp.route('/template-atualizacao.xlsx')
@login_required
def template_atualizacao_xlsx():
    """Baixa um XLSX-modelo para atualização em lote de CTEs (todos os campos editáveis)."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font
        from io import BytesIO
    except Exception as e:
        return make_response(
            f"openpyxl não disponível ({e}). Use /template-atualizacao para CSV.",
            500
        )

    headers = [
        "numero_cte",
        "destinatario_nome",
        "valor_total",
        "veiculo_placa",
        "data_emissao",
        "data_inclusao_fatura",
        "numero_fatura",
        "primeiro_envio",
        "envio_final",
        "data_atesto",
        "data_baixa",
        "status_baixa",
        "status_processo",
        "observacao",
    ]

    amostras = [
        ["1001", "Cliente A", 5500.00, "ABC1A23",
         "01/01/2025", "05/01/2025", "NF001", "06/01/2025", "10/01/2025",
         "12/01/2025", "15/01/2025", "Pago", "Completo", "Exemplo de atualização"],
        ["1002", "Cliente B", 3200.50, "XYZ4B56",
         "02/01/2025", "", "NF002", "08/01/2025", "",
         "", "", "Pendente", "Em andamento", "Pendente de baixa"],
        ["1003", "Cliente C", 7800.00, "DEF7C89",
         "03/01/2025", "07/01/2025", "NF003", "", "20/01/2025",
         "22/01/2025", "25/01/2025", "Pago", "Completo", "Concluído"],
    ]

    wb = Workbook()
    ws = wb.active
    ws.title = "Atualização CTEs"

    # Cabeçalho
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Linhas de exemplo
    for r in amostras:
        ws.append(r)

    # Largura amigável (opcional)
    widths = [14, 28, 14, 14, 14, 20, 16, 16, 16, 14, 12, 14, 16, 30]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = w  # A, B, C...

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="template_atualizacao_ctes.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        max_age=0,
        conditional=False,
        etag=False,
        last_modified=None
    )

# =============================================================================
# EXPORTS
# =============================================================================
@bp.route('/api/download/excel')
@login_required
def download_excel():
    """Download dos CTEs em Excel"""
    try:
        # Filtros similares à listagem
        search = request.args.get('search', '').strip()
        status_baixa = request.args.get('status_baixa', '')
        status_processo = request.args.get('status_processo', '')

        query = CTE.query

        if search:
            if search.isdigit():
                query = query.filter(CTE.numero_cte == int(search))
            else:
                search_pattern = f'%{search}%'
                query = query.filter(or_(
                    CTE.destinatario_nome.ilike(search_pattern),
                    CTE.numero_fatura.ilike(search_pattern),
                    CTE.veiculo_placa.ilike(search_pattern)
                ))

        if status_baixa == 'com_baixa':
            query = query.filter(CTE.data_baixa.isnot(None))
        elif status_baixa == 'sem_baixa':
            query = query.filter(CTE.data_baixa.is_(None))

        ctes = query.order_by(CTE.numero_cte.desc()).all()

        dados = []
        for cte in ctes:
            dados.append({
                'Número CTE': cte.numero_cte,
                'Cliente': cte.destinatario_nome or '',
                'Valor Total': float(cte.valor_total or 0),
                'Data Emissão': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                'Placa Veículo': cte.veiculo_placa or '',
                'Data Inclusão Fatura': cte.data_inclusao_fatura.strftime('%d/%m/%Y') if getattr(cte, 'data_inclusao_fatura', None) else '',
                'Número Fatura': cte.numero_fatura or '',
                'Primeiro Envio': cte.primeiro_envio.strftime('%d/%m/%Y') if cte.primeiro_envio else '',
                'Envio Final': cte.envio_final.strftime('%d/%m/%Y') if cte.envio_final else '',
                'Data Atesto': cte.data_atesto.strftime('%d/%m/%Y') if cte.data_atesto else '',
                'Data Baixa': cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else '',
                'Status Baixa': 'Pago' if cte.data_baixa else 'Pendente',
                'Status Processo': getattr(cte, 'status_processo', ''),
                'Observação': cte.observacao or ''
            })

        df = pd.DataFrame(dados)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CTEs', index=False)
        output.seek(0)

        filename = f'ctes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.exception("Erro no download Excel")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/download/csv')
@login_required
def download_csv():
    """Download dos CTEs em CSV"""
    try:
        query = CTE.query.order_by(CTE.numero_cte.desc())
        ctes = query.all()

        dados = []
        for cte in ctes:
            dados.append({
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome or '',
                'valor_total': float(cte.valor_total or 0),
                'data_emissao': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                'status_baixa': 'Pago' if cte.data_baixa else 'Pendente'
            })

        df = pd.DataFrame(dados)

        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)

        filename = f'ctes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)

    except Exception as e:
        current_app.logger.exception("Erro no download CSV")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/download/pdf')
@login_required
def download_pdf():
    """Download dos CTEs em PDF - Placeholder (redireciona para Excel)"""
    try:
        return redirect(url_for('ctes.download_excel'))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# AUDITORIA / CORREÇÃO
# =============================================================================
@bp.route('/api/auditoria')
@login_required
def api_auditoria():
    """API para auditar inconsistências nos CTEs"""
    try:
        problemas = []
        ctes_verificados = 0

        ctes = CTE.query.all()
        for cte in ctes:
            ctes_verificados += 1

            datas_preenchidas = [
                ('data_emissao', cte.data_emissao),
                ('primeiro_envio', cte.primeiro_envio),
                ('data_atesto', cte.data_atesto),
                ('envio_final', cte.envio_final),
                ('data_baixa', cte.data_baixa)
            ]

            datas_vazias = [nome for nome, data in datas_preenchidas if data is None]
            datas_preenchidas_count = sum(1 for _, data in datas_preenchidas if data is not None)

            problema = None
            if getattr(cte, 'processo_completo', False) and len(datas_vazias) > 1:
                problema = f"Marcado como completo mas faltam: {', '.join(datas_vazias)}"
            elif not getattr(cte, 'processo_completo', False) and len(datas_vazias) <= 1:
                problema = f"Pode estar completo - apenas falta: {', '.join(datas_vazias) if datas_vazias else 'nenhuma'}"

            if problema:
                problemas.append({
                    'numero_cte': cte.numero_cte,
                    'cliente': cte.destinatario_nome,
                    'status_atual': getattr(cte, 'status_processo', ''),
                    'processo_completo': getattr(cte, 'processo_completo', False),
                    'problema': problema,
                    'datas_vazias': datas_vazias,
                    'datas_preenchidas': datas_preenchidas_count,
                    'datas_detalhes': {
                        'data_emissao': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else None,
                        'primeiro_envio': cte.primeiro_envio.strftime('%d/%m/%Y') if cte.primeiro_envio else None,
                        'data_atesto': cte.data_atesto.strftime('%d/%m/%Y') if cte.data_atesto else None,
                        'envio_final': cte.envio_final.strftime('%d/%m/%Y') if cte.envio_final else None,
                        'data_baixa': cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else None
                    }
                })

        return jsonify({
            'success': True,
            'ctes_verificados': ctes_verificados,
            'problemas_encontrados': len(problemas),
            'problemas': problemas[:50]
        })

    except Exception as e:
        current_app.logger.exception("Erro na auditoria")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/corrigir-status')
@login_required
def api_corrigir_status():
    """API para forçar recálculo de todos os status"""
    try:
        ctes_corrigidos = 0
        ctes = CTE.query.all()
        for cte in ctes:
            cte.updated_at = datetime.utcnow()
            ctes_corrigidos += 1
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Status recalculado para {ctes_corrigidos} CTEs',
            'ctes_corrigidos': ctes_corrigidos
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao corrigir status")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# IMPORTAÇÃO VIA CSV (páginas e APIs)
# =============================================================================
@bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar_ctes():
    """Página de importação incremental de CTEs (CSV)"""
    if request.method == 'GET':
        stats = ImportacaoService.obter_estatisticas_importacao()
        return render_template('ctes/importar.html', stats=stats)

    # POST - Processar upload do arquivo
    try:
        if 'arquivo_csv' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('ctes.importar_ctes'))

        arquivo = request.files['arquivo_csv']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('ctes.importar_ctes'))

        if not arquivo.filename.lower().endswith('.csv'):
            flash('Apenas arquivos CSV são permitidos', 'error')
            return redirect(url_for('ctes.importar_ctes'))

        resultado = ImportacaoService.processar_importacao_completa(arquivo)

        if resultado['sucesso']:
            stats = resultado['estatisticas']
            insercao = stats['insercao']

            flash(
                f"Importação concluída com sucesso!\n"
                f"• CTEs processados: {insercao['processados']}\n"
                f"• CTEs inseridos: {insercao['sucessos']}\n"
                f"• CTEs com erro: {insercao['erros']}\n"
                f"• CTEs já existentes: {stats['processamento']['ctes_existentes']}",
                'success'
            )
            current_app.logger.info(
                f"Importação incremental realizada por {current_user.username}: "
                f"{insercao['sucessos']} CTEs inseridos"
            )

            return render_template('ctes/importar_resultado.html',
                                   resultado=resultado,
                                   detalhes=resultado['detalhes'])
        else:
            flash(f'Erro na importação: {resultado["erro"]}', 'error')
            return redirect(url_for('ctes.importar_ctes'))

    except Exception as e:
        current_app.logger.exception("Erro na importação de CTEs")
        flash(f'Erro interno: {str(e)}', 'error')
        return redirect(url_for('ctes.importar_ctes'))

@bp.route('/template-csv')
@login_required
def download_template():
    """Download do template CSV para importação"""
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=template_ctes.csv'
        return response
    except Exception as e:
        current_app.logger.exception("Erro ao gerar template CSV")
        flash('Erro ao gerar template CSV', 'error')
        return redirect(url_for('ctes.importar_ctes'))

@bp.route('/validar-csv', methods=['POST'])
@login_required
def validar_csv():
    """Endpoint AJAX para validação prévia do CSV"""
    try:
        if 'arquivo_csv' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'})

        arquivo = request.files['arquivo_csv']
        valido, mensagem, df = ImportacaoService.validar_csv_upload(arquivo)
        if not valido:
            return jsonify({'sucesso': False, 'erro': mensagem})

        df_limpo, stats_proc = ImportacaoService.processar_dados_csv(df)
        if df_limpo.empty:
            return jsonify({'sucesso': False, 'erro': 'Nenhum registro válido no arquivo'})

        df_novos, df_existentes, stats_novos = ImportacaoService.identificar_ctes_novos(df_limpo)
        duplicatas = ImportacaoService.verificar_duplicatas_internas(df_limpo)

        return jsonify({
            'sucesso': True,
            'estatisticas': {
                'arquivo': stats_proc,
                'analise': stats_novos,
                'duplicatas': duplicatas
            }
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)})

@bp.route('/historico-importacoes')
@login_required
def historico_importacoes():
    """Página com histórico de importações realizadas"""
    try:
        data_limite = datetime.now().date() - timedelta(days=30)
        importacoes = db.session.query(
            func.date(CTE.created_at).label('data'),
            func.count(CTE.id).label('quantidade'),
            func.sum(CTE.valor_total).label('valor_total'),
            CTE.origem_dados
        ).filter(
            CTE.created_at >= data_limite,
            CTE.origem_dados.like('%CSV%')
        ).group_by(
            func.date(CTE.created_at),
            CTE.origem_dados
        ).order_by(
            func.date(CTE.created_at).desc()
        ).all()

        return render_template('ctes/historico_importacoes.html', importacoes=importacoes)
    except Exception as e:
        current_app.logger.exception("Erro ao buscar histórico")
        flash('Erro ao carregar histórico de importações', 'error')
        return redirect(url_for('ctes.listar'))

@bp.route('/api/importar/lote', methods=['POST'])
@login_required
def api_importar_lote():
    """API para importação de CTEs em lote a partir de CSV"""
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400

        if not arquivo.filename.lower().endswith('.csv'):
            return jsonify({'sucesso': False, 'erro': 'Apenas arquivos CSV são permitidos'}), 400

        resultado = ImportacaoService.processar_importacao_completa(arquivo)

        if resultado['sucesso']:
            stats_insercao = resultado['estatisticas']['insercao']
            stats_analise = resultado['estatisticas']['analise']

            resultados_formatados = {
                'processados': stats_insercao['processados'],
                'sucessos': stats_insercao['sucessos'],
                'erros': stats_insercao['erros'],
                'ctes_existentes': stats_analise['ctes_existentes'],
                'detalhes': stats_insercao.get('detalhes', [])[:50],
                'tempo_processamento': resultado.get('tempo_processamento', 0)
            }

            return jsonify({
                'sucesso': True,
                'resultados': resultados_formatados,
                'estatisticas_completas': resultado['estatisticas']
            })
        else:
            return jsonify({'sucesso': False, 'erro': resultado['erro']}), 500

    except Exception as e:
        current_app.logger.exception("Erro na importação em lote")
        return jsonify({'sucesso': False, 'erro': f'Erro interno: {str(e)}'}), 500

@bp.route('/api/validar-csv', methods=['POST'])
@login_required
def api_validar_csv():
    """API para validação prévia do CSV antes da importação"""
    try:
        arquivo = request.files.get('arquivo_csv')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'})

        valido, mensagem, df = ImportacaoService.validar_csv_upload(arquivo)
        if not valido:
            return jsonify({'sucesso': False, 'erro': mensagem})

        df_limpo, stats_proc = ImportacaoService.processar_dados_csv(df)
        if df_limpo.empty:
            return jsonify({'sucesso': False, 'erro': 'Nenhum registro válido no arquivo'})

        df_novos, df_existentes, stats_novos = ImportacaoService.identificar_ctes_novos(df_limpo)
        duplicatas = ImportacaoService.verificar_duplicatas_internas(df_limpo)

        preview_data = df_novos.head(5).to_dict('records') if not df_novos.empty else []

        return jsonify({
            'sucesso': True,
            'estatisticas': {
                'arquivo': {
                    'nome': arquivo.filename,
                    'linhas_totais': len(df),
                    'linhas_validas': stats_proc['linhas_validas'],
                    'linhas_descartadas': stats_proc['linhas_descartadas']
                },
                'analise': stats_novos,
                'duplicatas': duplicatas,
                'preview': preview_data
            }
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)})

@bp.route('/api/template-csv')
@login_required
def api_template_csv():
    """Download do template CSV para importação (via API)"""
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=template_importacao_ctes.csv'
        return response
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@bp.route('/api/estatisticas-importacao')
@login_required
def api_estatisticas_importacao():
    """Estatísticas para dashboard de importação"""
    try:
        stats = ImportacaoService.obter_estatisticas_importacao()
        return jsonify({'sucesso': True, 'estatisticas': stats})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)})

@bp.route('/importar-lote')
@login_required
def importar_lote():
    """Página de importação em lote de CTEs"""
    stats = ImportacaoService.obter_estatisticas_importacao()
    return render_template('ctes/importar_lote.html', stats=stats)

# =============================================================================
# DIAGNÓSTICO
# =============================================================================
@bp.route('/teste-update')
@login_required
def teste_update():
    """Rota de teste para diagnóstico"""
    return f"""
    <div style="font-family: Arial; padding: 20px; background: #f8f9fa; min-height: 100vh;">
        <h1>🔧 Sistema de Atualização - DIAGNÓSTICO</h1>
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>✅ Status das Rotas:</h3>
            <ul>
                <li>✅ Rota de teste funcionando</li>
                <li>✅ Sistema Flask operacional</li>
                <li>✅ Login autenticado</li>
                <li>✅ Usuário: {current_user.username}</li>
            </ul>
        </div>

        <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>🔗 Links de Teste:</h3>
            <ul>
                <li><a href="/ctes/importar-lote" style="color: #0066cc;">📑 Importação em Lote</a></li>
                <li><a href="/ctes/template-atualizacao" style="color: #0066cc;">🗂️ Download Template CSV</a></li>
                <li><a href="/ctes/template-atualizacao.xlsx" style="color: #0066cc;">🗂️ Download Template XLSX</a></li>
                <li><a href="/ctes" style="color: #0066cc;">📊 Voltar para CTEs</a></li>
                <li><a href="/dashboard" style="color: #0066cc;">🏠 Dashboard</a></li>
            </ul>
        </div>

        <div style="background: white; padding: 20px; border-radius: 10px;">
            <h3>📈 Informações do Sistema:</h3>
            <p><strong>Total CTEs:</strong> {CTE.query.count()}</p>
        </div>
    </div>
    """
