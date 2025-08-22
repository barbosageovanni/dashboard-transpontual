from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, send_file
from flask_login import login_required
from app.models.cte import CTE
from app import db
from datetime import datetime
from sqlalchemy import and_, or_, func
import pandas as pd
from io import BytesIO
import tempfile
import os
from app.services.importacao_service import ImportacaoService
from werkzeug.utils import secure_filename
from flask import make_response, current_app


bp = Blueprint('ctes', __name__, url_prefix='/ctes')

@bp.route('/')
@bp.route('/listar')
@login_required
def listar():
    """PÃ¡gina principal de listagem de CTEs"""
    return render_template('ctes/index.html')

@bp.route('/api/listar')
@login_required
def api_listar():
    """API para listar CTEs com filtros avanÃ§ados"""
    try:
        # ParÃ¢metros de busca
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
                print(f"Erro no filtro de busca: {e}")
        
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
        
        # Filtro por perÃ­odo
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
                print(f"Erro ao converter CTE {cte.numero_cte}: {e}")
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
        print(f"Erro na listagem: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# âœ… ADICIONADO: Rota para inserir (compatibilidade com frontend)
@bp.route('/api/inserir', methods=['POST'])
@login_required
def api_inserir():
    """API para inserir novo CTE - COMPATIBILIDADE COM FRONTEND"""
    try:
        dados = request.get_json()
        
        if not dados.get('numero_cte'):
            return jsonify({'success': False, 'message': 'NÃºmero do CTE Ã© obrigatÃ³rio'}), 400
        
        if not dados.get('valor_total'):
            return jsonify({'success': False, 'message': 'Valor total Ã© obrigatÃ³rio'}), 400
        
        # Verificar se CTE jÃ¡ existe
        cte_existente = CTE.buscar_por_numero(dados['numero_cte'])
        if cte_existente:
            return jsonify({'success': False, 'message': 'CTE jÃ¡ existe'}), 400
        
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

# âœ… ADICIONADO: Rota para buscar (compatibilidade com frontend)
@bp.route('/api/buscar/<int:numero_cte>')
@login_required
def api_buscar(numero_cte):
    """API para buscar CTE especÃ­fico - COMPATIBILIDADE COM FRONTEND"""
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': 'CTE nÃ£o encontrado'}), 404
        
        return jsonify({
            'success': True,
            'cte': cte.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/atualizar/<int:numero_cte>', methods=['PUT'])
@login_required
def api_atualizar(numero_cte):
    """API para atualizar CTE"""
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': 'CTE nÃ£o encontrado'}), 404
        
        dados = request.get_json()
        sucesso, mensagem = cte.atualizar(dados)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem,
                'cte': cte.to_dict()
            })
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
            return jsonify({'success': False, 'message': 'CTE nÃ£o encontrado'}), 404
        
        db.session.delete(cte)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'CTE {numero_cte} excluÃ­do com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# âœ… ADICIONADO: Rotas de download que estavam faltando

# SISTEMA DE ATUALIZAÇÃO EM LOTE - ÚNICA VERSÃO
# ============================================================================
@bp.route('/atualizar-lote')
@login_required
def atualizar_lote():
    '''PÃ¡gina de atualizaÃ§Ã£o em lote de CTEs'''
    try:
        # EstatÃ­sticas atuais
        stats = {
            'total_ctes': CTE.query.count(),
            'atualizacoes_hoje': CTE.query.filter(
                func.date(CTE.updated_at) == datetime.now().date()
            ).count() if CTE.updated_at else 0,
            'ultimo_update': CTE.query.order_by(CTE.updated_at.desc()).first()
        }
        
        return render_template('ctes/atualizar_lote.html', stats=stats)
        
    except Exception as e:
        flash(f'Erro ao carregar pÃ¡gina: {str(e)}', 'error')
        return redirect(url_for('ctes.listar'))

@bp.route('/api/atualizar-lote', methods=['POST'])
@login_required
def api_atualizar_lote():
    '''API para processar atualizaÃ§Ã£o em lote'''
    try:
        arquivo = request.files.get('arquivo')
        modo = request.form.get('modo', 'empty_only')
        
        if not arquivo:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo enviado'
            }), 400
        
        # Usar serviÃ§o de atualizaÃ§Ã£o
        from app.services.bulk_update_service import BulkUpdateService
        
        service = BulkUpdateService()
        resultado = service.processar_arquivo_web(arquivo, modo)
        
        if resultado['sucesso']:
            flash(f'''AtualizaÃ§Ã£o concluÃ­da!
            â€¢ Processados: {resultado['stats']['total_processados']}
            â€¢ Atualizados: {resultado['stats']['atualizados']}
            â€¢ Sem alteraÃ§Ã£o: {resultado['stats']['sem_alteracao']}
            â€¢ Erros: {resultado['stats']['erros']}''', 'success')
        else:
            flash(f'Erro na atualizaÃ§Ã£o: {resultado["erro"]}', 'error')
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@bp.route('/api/download/excel')
@login_required
def download_excel():
    """Download dos CTEs em Excel"""
    try:
        # Aplicar mesmos filtros da listagem
        search = request.args.get('search', '').strip()
        status_baixa = request.args.get('status_baixa', '')
        status_processo = request.args.get('status_processo', '')
        
        query = CTE.query
        
        # Aplicar filtros
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
        
        # Buscar dados
        ctes = query.order_by(CTE.numero_cte.desc()).all()
        
        # Converter para DataFrame
        dados = []
        for cte in ctes:
            dados.append({
                'NÃºmero CTE': cte.numero_cte,
                'Cliente': cte.destinatario_nome or '',
                'Valor Total': float(cte.valor_total or 0),
                'Data EmissÃ£o': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                'Placa VeÃ­culo': cte.veiculo_placa or '',
                'data InclusÃ£o Fatura': cte.data_inclusao_fatura.strftime('%d/%m/%Y') if cte.data_inclusao_fatura else '',
                'NÃºmero Fatura': cte.numero_fatura or '',
                'Primeiro Envio': cte.primeiro_envio.strftime('%d/%m/%Y') if cte.primeiro_envio else '',
                'Envio Final': cte.envio_final.strftime('%d/%m/%Y') if cte.envio_final else '',
                'Data Atesto': cte.data_atesto.strftime('%d/%m/%Y') if cte.data_atesto else '',
                'Data Baixa': cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else '',
                'Status Baixa': 'Pago' if cte.data_baixa else 'Pendente',
                'Status Processo': cte.status_processo,
                'ObservaÃ§Ã£o': cte.observacao or ''
            })
        
        df = pd.DataFrame(dados)
        
        # Criar arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CTEs', index=False)
        
        output.seek(0)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ctes_export_{timestamp}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/download/csv')
@login_required
def download_csv():
    """Download dos CTEs em CSV"""
    try:
        # Mesma lÃ³gica do Excel, mas para CSV
        query = CTE.query
        ctes = query.order_by(CTE.numero_cte.desc()).all()
        
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
        
        # Criar arquivo CSV
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ctes_export_{timestamp}.csv'
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/download/pdf')
@login_required
def download_pdf():
    """Download dos CTEs em PDF - Placeholder"""
    try:
        # Por enquanto, redirecionar para Excel
        return redirect(url_for('ctes.download_excel'))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# âœ… FUNÃ‡Ã•ES DE AUDITORIA E CORREÃ‡ÃƒO PARA RESOLVER O BUG
@bp.route('/api/auditoria')
@login_required
def api_auditoria():
    """API para auditar inconsistÃªncias nos CTEs"""
    try:
        problemas = []
        ctes_verificados = 0
        
        # Buscar todos os CTEs
        ctes = CTE.query.all()
        
        for cte in ctes:
            ctes_verificados += 1
            
            # Verificar inconsistÃªncias
            datas_preenchidas = [
                ('data_emissao', cte.data_emissao),
                ('primeiro_envio', cte.primeiro_envio),
                ('data_atesto', cte.data_atesto),
                ('envio_final', cte.envio_final),
                ('data_baixa', cte.data_baixa)
            ]
            
            datas_vazias = [nome for nome, data in datas_preenchidas if data is None]
            datas_preenchidas_count = sum(1 for nome, data in datas_preenchidas if data is not None)
            
            # Identificar problemas
            problema = None
            if cte.processo_completo and len(datas_vazias) > 1:  # Se estÃ¡ marcado completo mas tem muitas datas vazias
                problema = f"Marcado como completo mas faltam: {', '.join(datas_vazias)}"
            elif not cte.processo_completo and len(datas_vazias) <= 1:  # Se nÃ£o estÃ¡ completo mas tem quase tudo
                problema = f"Pode estar completo - apenas falta: {', '.join(datas_vazias) if datas_vazias else 'nenhuma'}"
            
            if problema:
                problemas.append({
                    'numero_cte': cte.numero_cte,
                    'cliente': cte.destinatario_nome,
                    'status_atual': cte.status_processo,
                    'processo_completo': cte.processo_completo,
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
            'problemas': problemas[:50]  # Limitar a 50 para nÃ£o sobrecarregar
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/corrigir-status')
@login_required  
def api_corrigir_status():
    """API para forÃ§ar recÃ¡lculo de todos os status"""
    try:
        ctes_corrigidos = 0
        
        # Buscar todos os CTEs e forÃ§ar recÃ¡lculo
        ctes = CTE.query.all()
        
        for cte in ctes:
            # ForÃ§ar recÃ¡lculo atualizando o timestamp
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    # ============================================================================
# ADICIONAR ESTAS ROTAS AO ARQUIVO app/routes/ctes.py
# ============================================================================

@bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar_ctes():
    """
    PÃ¡gina de importaÃ§Ã£o incremental de CTEs
    Baseada no padrÃ£o do sistema de baixas
    """
    if request.method == 'GET':
        # Obter estatÃ­sticas atuais para exibir no dashboard
        stats = ImportacaoService.obter_estatisticas_importacao()
        return render_template('ctes/importar.html', stats=stats)
    
    # POST - Processar upload do arquivo
    try:
        # Verificar se arquivo foi enviado
        if 'arquivo_csv' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('ctes.importar_ctes'))
        
        arquivo = request.files['arquivo_csv']
        
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('ctes.importar_ctes'))
        
        # Verificar extensÃ£o
        if not arquivo.filename.lower().endswith('.csv'):
            flash('Apenas arquivos CSV sÃ£o permitidos', 'error')
            return redirect(url_for('ctes.importar_ctes'))
        
        # Processar importaÃ§Ã£o
        resultado = ImportacaoService.processar_importacao_completa(arquivo)
        
        if resultado['sucesso']:
            stats = resultado['estatisticas']
            insercao = stats['insercao']
            
            # Mensagem de sucesso detalhada
            flash(f'''ImportaÃ§Ã£o concluÃ­da com sucesso!
                     â€¢ CTEs processados: {insercao['processados']}
                     â€¢ CTEs inseridos: {insercao['sucessos']} 
                     â€¢ CTEs com erro: {insercao['erros']}
                     â€¢ CTEs jÃ¡ existentes: {stats['processamento']['ctes_existentes']}''', 'success')
            
            # Log da operaÃ§Ã£o
            current_app.logger.info(f"ImportaÃ§Ã£o incremental realizada por {current_user.username}: "
                                   f"{insercao['sucessos']} CTEs inseridos")
            
            return render_template('ctes/importar_resultado.html', 
                                 resultado=resultado, 
                                 detalhes=resultado['detalhes'])
        else:
            flash(f'Erro na importaÃ§Ã£o: {resultado["erro"]}', 'error')
            return redirect(url_for('ctes.importar_ctes'))
            
    except Exception as e:
        current_app.logger.error(f"Erro na importaÃ§Ã£o de CTEs: {str(e)}")
        flash(f'Erro interno: {str(e)}', 'error')
        return redirect(url_for('ctes.importar_ctes'))

@bp.route('/template-csv')
@login_required 
def download_template():
    """
    Download do template CSV para importaÃ§Ã£o
    Similar ao padrÃ£o de baixas
    """
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        
        # Criar response com CSV
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=template_ctes.csv'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar template: {str(e)}")
        flash('Erro ao gerar template CSV', 'error')
        return redirect(url_for('ctes.importar_ctes'))

@bp.route('/validar-csv', methods=['POST'])
@login_required
def validar_csv():
    """
    Endpoint AJAX para validaÃ§Ã£o prÃ©via do CSV
    Retorna JSON com estatÃ­sticas antes da importaÃ§Ã£o
    """
    try:
        if 'arquivo_csv' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'})
        
        arquivo = request.files['arquivo_csv']
        
        # Validar arquivo
        valido, mensagem, df = ImportacaoService.validar_csv_upload(arquivo)
        
        if not valido:
            return jsonify({'sucesso': False, 'erro': mensagem})
        
        # Processar dados para estatÃ­sticas
        df_limpo, stats_proc = ImportacaoService.processar_dados_csv(df)
        
        if df_limpo.empty:
            return jsonify({'sucesso': False, 'erro': 'Nenhum registro vÃ¡lido no arquivo'})
        
        # Identificar CTEs novos vs existentes
        df_novos, df_existentes, stats_novos = ImportacaoService.identificar_ctes_novos(df_limpo)
        
        # Verificar duplicatas internas
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
    """
    PÃ¡gina com histÃ³rico de importaÃ§Ãµes realizadas
    """
    try:
        # Buscar CTEs importados via CSV (Ãºltimos 30 dias)
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
        current_app.logger.error(f"Erro ao buscar histÃ³rico: {str(e)}")
        flash('Erro ao carregar histÃ³rico de importaÃ§Ãµes', 'error')
        return redirect(url_for('ctes.index'))
    
    # Adicionar em app/routes/ctes.py
# Adicionar ao arquivo app/routes/ctes.py

@bp.route('/api/importar/lote', methods=['POST'])
@login_required
def api_importar_lote():
    """
    API para importaÃ§Ã£o de CTEs em lote - Similar ao sistema de baixas
    Processa arquivo CSV e insere CTEs sem duplicar dados existentes
    """
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo enviado'
            }), 400
        
        # Validar arquivo
        if not arquivo.filename.lower().endswith('.csv'):
            return jsonify({
                'sucesso': False,
                'erro': 'Apenas arquivos CSV sÃ£o permitidos'
            }), 400
        
        # Processar importaÃ§Ã£o usando o serviÃ§o existente
        resultado = ImportacaoService.processar_importacao_completa(arquivo)
        
        if resultado['sucesso']:
            # Formatear resposta similar ao sistema de baixas
            stats_insercao = resultado['estatisticas']['insercao']
            stats_analise = resultado['estatisticas']['analise']
            
            resultados_formatados = {
                'processados': stats_insercao['processados'],
                'sucessos': stats_insercao['sucessos'],
                'erros': stats_insercao['erros'],
                'ctes_existentes': stats_analise['ctes_existentes'],
                'detalhes': stats_insercao.get('detalhes', [])[:50],  # Limitar a 50
                'tempo_processamento': resultado.get('tempo_processamento', 0)
            }
            
            return jsonify({
                'sucesso': True,
                'resultados': resultados_formatados,
                'estatisticas_completas': resultado['estatisticas']
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': resultado['erro']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro na importaÃ§Ã£o em lote: {str(e)}")
        return jsonify({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

@bp.route('/api/validar-csv', methods=['POST'])
@login_required
def api_validar_csv():
    """
    API para validaÃ§Ã£o prÃ©via do CSV antes da importaÃ§Ã£o
    Retorna estatÃ­sticas do arquivo sem processar
    """
    try:
        arquivo = request.files.get('arquivo_csv')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'})
        
        # Validar arquivo bÃ¡sico
        valido, mensagem, df = ImportacaoService.validar_csv_upload(arquivo)
        
        if not valido:
            return jsonify({'sucesso': False, 'erro': mensagem})
        
        # Processar dados para estatÃ­sticas
        df_limpo, stats_proc = ImportacaoService.processar_dados_csv(df)
        
        if df_limpo.empty:
            return jsonify({'sucesso': False, 'erro': 'Nenhum registro vÃ¡lido no arquivo'})
        
        # Identificar CTEs novos vs existentes
        df_novos, df_existentes, stats_novos = ImportacaoService.identificar_ctes_novos(df_limpo)
        
        # Verificar duplicatas internas
        duplicatas = ImportacaoService.verificar_duplicatas_internas(df_limpo)
        
        # Preview dos primeiros registros
        preview_data = []
        if not df_novos.empty:
            preview_data = df_novos.head(5).to_dict('records')
        
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
    """Download do template CSV para importaÃ§Ã£o"""
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        
        # Criar response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=template_importacao_ctes.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@bp.route('/api/estatisticas-importacao')
@login_required
def api_estatisticas_importacao():
    """EstatÃ­sticas para dashboard de importaÃ§Ã£o"""
    try:
        stats = ImportacaoService.obter_estatisticas_importacao()
        
        return jsonify({
            'sucesso': True,
            'estatisticas': stats
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        })
    
@bp.route('/importar-lote')
@login_required
def importar_lote():
    """PÃ¡gina de importaÃ§Ã£o em lote de CTEs"""
    # Buscar estatÃ­sticas atuais
    stats = ImportacaoService.obter_estatisticas_importacao()
    return render_template('ctes/importar_lote.html', stats=stats)
# ============================================================================
# SISTEMA DE ATUALIZAÃ‡ÃƒO EM LOTE - WEB INTERFACE
# ============================================================================

@bp.route('/api/preview-atualizacao', methods=['POST'])
@login_required
def api_preview_atualizacao():
    '''API para preview da atualizaÃ§Ã£o sem executar'''
    try:
        arquivo = request.files.get('arquivo')
        modo = request.form.get('modo', 'empty_only')
        
        if not arquivo:
            return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
        
        from app.services.bulk_update_service import BulkUpdateService
        import io
        import pandas as pd
        
        service = BulkUpdateService()
        
        # Processar arquivo para preview
        if arquivo.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(arquivo.read()), encoding='utf-8')
        elif arquivo.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(arquivo.read()))
        else:
            return jsonify({'erro': 'Formato nÃ£o suportado'}), 400
        
        df_normalized = service.normalize_data(df)
        is_valid, errors = service.validate_data(df_normalized)
        
        if not is_valid:
            return jsonify({'erro': f'Dados invÃ¡lidos: {errors}'}), 400
        
        update_plan = service.generate_update_plan(df_normalized, modo)
        
        # Preparar preview limitado
        preview_data = []
        for i, plan in enumerate(update_plan[:10]):  # MÃ¡ximo 10 para preview
            preview_data.append({
                'numero_cte': plan['numero_cte'],
                'changes': {
                    field: f"{change['old_value']} â†’ {change['new_value']}"
                    for field, change in plan['changes'].items()
                }
            })
        
        return jsonify({
            'sucesso': True,
            'total_para_atualizar': len(update_plan),
            'preview': preview_data,
            'total_linhas_arquivo': len(df_normalized),
            'modo': modo
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@bp.route('/template-atualizacao')
@login_required
def download_template_atualizacao():
    '''Download template Excel para atualizaÃ§Ã£o'''
    from flask import make_response
    import io
    import pandas as pd
    
    try:
        # Criar template com exemplos
        template_data = {
            'numero_cte': [1001, 1002, 1003],
            'destinatario_nome': ['Cliente A', 'Cliente B', 'Cliente C'],
            'valor_total': [5500.00, 3200.50, 7800.00],
            'veiculo_placa': ['ABC1234', 'XYZ5678', 'DEF9012'],
            'data_emissao': ['01/01/2025', '02/01/2025', '03/01/2025'],
            'data_baixa': ['15/01/2025', '', '20/01/2025'],
            'numero_fatura': ['NF001', 'NF002', 'NF003'],
            'observacao': ['ObservaÃ§Ã£o exemplo', '', 'Outra observaÃ§Ã£o']
        }
        
        df = pd.DataFrame(template_data)
        
        # Criar arquivo Excel em memÃ³ria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CTEs_Atualizacao', index=False)
        
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=template_atualizacao_ctes.xlsx'
        
        return response
        
    except Exception as e:
        flash(f'Erro ao gerar template: {str(e)}', 'error')
        return redirect(url_for('ctes.atualizar_lote'))

# ============================================================================
# SISTEMA DE ATUALIZAÃ‡ÃƒO EM LOTE - TRANSPONTUAL
# ============================================================================

@bp.route('/template-atualizacao')
@login_required
def download_template_atualizacao():
    '''Download template para atualizaÃ§Ã£o'''
    from flask import make_response
    
    template = '''numero_cte,destinatario_nome,valor_total,veiculo_placa,data_emissao,data_baixa,observacao
1001,Cliente A,5500.00,ABC1234,01/01/2025,15/01/2025,Exemplo
1002,Cliente B,3200.50,XYZ5678,02/01/2025,,Pendente
'''
    
    response = make_response(template)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=template_atualizacao_transpontual.csv'
    
    return response
# Adicionar no FINAL do arquivo app/routes/ctes.py (substitua as rotas duplicadas)

# ============================================================================
# SISTEMA DE ATUALIZAÃ‡ÃƒO EM LOTE - VERSÃƒO CORRIGIDA
# ============================================================================

@bp.route('/template-atualizacao')
@login_required
def template_atualizacao():
    '''Download template CSV para atualizaÃ§Ã£o'''
    from flask import make_response
    
    template = '''numero_cte,destinatario_nome,valor_total,veiculo_placa,data_emissao,data_baixa,numero_fatura,observacao
1001,Cliente A,5500.00,ABC1234,01/01/2025,15/01/2025,NF001,Exemplo de atualizaÃ§Ã£o
1002,Cliente B,3200.50,XYZ5678,02/01/2025,,NF002,Pendente de baixa
1003,Cliente C,7800.00,DEF9012,03/01/2025,20/01/2025,NF003,ConcluÃ­do
'''
    
    response = make_response(template)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=template_atualizacao_transpontual.csv'
    
    return response

# ============================================================================
# ROTA DE TESTE PARA DIAGNÃ“STICO
# ============================================================================

@bp.route('/teste-update')
@login_required  
def teste_update():
    '''Rota de teste para diagnÃ³stico'''
    return f'''
    <div style="font-family: Arial; padding: 20px; background: #f8f9fa; min-height: 100vh;">
        <h1>ðŸ”§ Sistema de AtualizaÃ§Ã£o - DIAGNÃ“STICO</h1>
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>âœ… Status das Rotas:</h3>
            <ul>
                <li>âœ… Rota de teste funcionando</li>
                <li>âœ… Sistema Flask operacional</li>
                <li>âœ… Login autenticado</li>
                <li>âœ… UsuÃ¡rio: {current_user.username}</li>
            </ul>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>ðŸ”— Links de Teste:</h3>
            <ul>
                <li><a href="/ctes/atualizar-lote" style="color: #0066cc;">ðŸ“‹ AtualizaÃ§Ã£o em Lote</a></li>
                <li><a href="/ctes/template-atualizacao" style="color: #0066cc;">ðŸ“„ Download Template</a></li>
                <li><a href="/ctes" style="color: #0066cc;">ðŸ“Š Voltar para CTEs</a></li>
                <li><a href="/dashboard" style="color: #0066cc;">ðŸ  Dashboard</a></li>
            </ul>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px;">
            <h3>ðŸ“Š InformaÃ§Ãµes do Sistema:</h3>
            <p><strong>Total CTEs:</strong> {CTE.query.count()}</p>
            <p><strong>Sistema:</strong> Dashboard Transpontual</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
        </div>
    </div>
    '''

