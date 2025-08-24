#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes para CTEs - Dashboard Baker Flask
Versão limpa - sem duplicatas
"""

from flask import Blueprint, render_template, request, jsonify, make_response, current_app
from flask_login import login_required, current_user
from app.models.cte import CTE
from app.services.importacao_service import ImportacaoService
from datetime import datetime
import pandas as pd
import io

bp = Blueprint('ctes', __name__, url_prefix='/ctes')

@bp.route('/')
@login_required
def index():
    """Página principal de CTEs"""
    return render_template('ctes/index.html')

@bp.route('/listar')
@login_required  
def listar():
    """Lista CTEs"""
    return render_template('ctes/index.html')

@bp.route('/api/listar')
@login_required
def api_listar():
    """API para listar CTEs"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        pagination = CTE.query.order_by(CTE.numero_cte.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        ctes = []
        for cte in pagination.items:
            try:
                cte_dict = {
                    'numero_cte': cte.numero_cte,
                    'destinatario_nome': cte.destinatario_nome or '',
                    'valor_total': float(cte.valor_total or 0),
                    'data_emissao': cte.data_emissao.isoformat() if cte.data_emissao else None,
                    'has_baixa': cte.data_baixa is not None if hasattr(cte, 'data_baixa') else False,
                    'status_processo': 'Completo' if hasattr(cte, 'data_atesto') and cte.data_atesto else 'Pendente'
                }
                ctes.append(cte_dict)
            except Exception as e:
                print(f"Erro ao converter CTE {cte.numero_cte}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'ctes': ctes,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        print(f"Erro na listagem: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/salvar', methods=['POST'])
@login_required
def api_salvar_cte():
    """API para salvar CTE"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        numero_cte = dados.get('numero_cte')
        if not numero_cte:
            return jsonify({
                'success': False,
                'message': 'Número do CTE é obrigatório'
            }), 400
        
        # Verificar se CTE já existe
        cte_existente = CTE.query.filter_by(numero_cte=numero_cte).first()
        
        from app import db
        
        if cte_existente:
            # Atualizar CTE existente
            campos_atualizados = 0
            
            for campo, valor in dados.items():
                if campo != 'numero_cte' and hasattr(cte_existente, campo):
                    if valor is not None and str(valor).strip():
                        try:
                            if 'data' in campo.lower() and isinstance(valor, str):
                                valor_data = datetime.strptime(valor.strip(), '%Y-%m-%d').date()
                                setattr(cte_existente, campo, valor_data)
                            else:
                                setattr(cte_existente, campo, valor)
                            campos_atualizados += 1
                        except Exception:
                            continue
            
            if campos_atualizados > 0:
                if hasattr(cte_existente, 'updated_at'):
                    cte_existente.updated_at = datetime.utcnow()
                db.session.commit()
                mensagem = f"CTE {numero_cte} atualizado"
            else:
                mensagem = f"CTE {numero_cte} - sem alterações"
        else:
            # Criar novo CTE
            novo_cte = CTE(
                numero_cte=numero_cte,
                destinatario_nome=dados.get('destinatario_nome', ''),
                valor_total=dados.get('valor_total', 0),
                veiculo_placa=dados.get('veiculo_placa'),
                observacao=dados.get('observacao')
            )
            
            # Processar datas se fornecidas
            campos_data = ['data_emissao', 'data_envio_processo', 'primeiro_envio', 'data_rq_tmc', 'data_atesto', 'envio_final']
            for campo in campos_data:
                valor_data = dados.get(campo)
                if valor_data:
                    try:
                        data_obj = datetime.strptime(valor_data, '%Y-%m-%d').date()
                        setattr(novo_cte, campo, data_obj)
                    except Exception:
                        pass
            
            db.session.add(novo_cte)
            db.session.commit()
            mensagem = f"CTE {numero_cte} criado"
        
        return jsonify({
            'success': True,
            'message': mensagem
        })
    
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar CTE: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@bp.route('/api/validar-csv', methods=['POST'])
@login_required
def api_validar_csv():
    """API para validar CSV"""
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo enviado'
            }), 400
        
        # ImportacaoService sempre retorna tupla correta
        valido, mensagem, df = ImportacaoService.validar_csv_upload(arquivo)
        
        if not valido:
            return jsonify({
                'sucesso': False,
                'erro': mensagem
            }), 400
        
        df_limpo, stats = ImportacaoService.processar_dados_csv(df)
        
        return jsonify({
            'sucesso': True,
            'linhas_totais': stats['linhas_totais'],
            'linhas_validas': stats['linhas_validas'],
            'linhas_descartadas': stats['linhas_descartadas']
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@bp.route('/api/template-csv')
@login_required
def api_template_csv():
    """Download template CSV"""
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=template_ctes.csv'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ✅ ROTAS ADICIONAIS PARA TEMPLATES

@bp.route('/importar-lote', methods=['GET', 'POST'])
@login_required
def importar_lote():
    """Página de importação em lote"""
    if request.method == 'GET':
        return render_template('ctes/importar_lote.html')
    
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo enviado'
            }), 400
        
        # Usar ImportacaoService
        resultado = ImportacaoService.processar_importacao_completa(arquivo)
        
        if resultado['sucesso']:
            return jsonify({
                'success': True,
                'message': 'Importação realizada com sucesso',
                'estatisticas': resultado['estatisticas']
            })
        else:
            return jsonify({
                'success': False,
                'message': resultado['erro']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@bp.route('/atualizar-lote', methods=['GET', 'POST'])
@login_required
def atualizar_lote():
    """Página de atualização em lote"""
    if request.method == 'GET':
        # Retornar template básico se não existir
        try:
            return render_template('ctes/atualizar_lote.html')
        except:
            return render_template('ctes/index.html')
    
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo enviado'
            }), 400
        
        # Processar arquivo CSV simples
        import pandas as pd
        import io
        
        content = arquivo.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content))
        
        dados_lote = df.to_dict('records')
        
        # Processar atualização simples
        from app import db
        atualizados = 0
        erros = 0
        
        for item in dados_lote:
            numero_cte = item.get('numero_cte')
            if numero_cte:
                cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                if cte:
                    # Atualizar observação como exemplo
                    if item.get('observacao'):
                        cte.observacao = item['observacao']
                        atualizados += 1
                else:
                    erros += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'atualizados': atualizados,
            'erros': erros,
            'message': f'Processados: {len(dados_lote)}, Atualizados: {atualizados}, Erros: {erros}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@bp.route('/inserir')
@login_required
def inserir():
    """Redirect para página principal com aba inserir"""
    return render_template('ctes/index.html')

@bp.route('/buscar')
@login_required
def buscar():
    """Redirect para página principal com aba buscar"""
    return render_template('ctes/index.html')

@bp.route('/api/buscar/<int:numero_cte>')
@login_required
def api_buscar_cte(numero_cte):
    """API para buscar CTE específico"""
    try:
        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
        
        if not cte:
            return jsonify({
                'success': False,
                'message': 'CTE não encontrado'
            }), 404
        
        cte_dict = {
            'numero_cte': cte.numero_cte,
            'destinatario_nome': cte.destinatario_nome or '',
            'valor_total': float(cte.valor_total or 0),
            'veiculo_placa': cte.veiculo_placa,
            'data_emissao': cte.data_emissao.isoformat() if cte.data_emissao else None,
            'observacao': cte.observacao
        }
        
        return jsonify({
            'success': True,
            'cte': cte_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/api/inserir', methods=['POST'])
@login_required
def api_inserir_cte():
    """API para inserir novo CTE"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        numero_cte = dados.get('numero_cte')
        if not numero_cte:
            return jsonify({
                'success': False,
                'message': 'Número do CTE é obrigatório'
            }), 400
        
        # Verificar se já existe
        if CTE.query.filter_by(numero_cte=numero_cte).first():
            return jsonify({
                'success': False,
                'message': f'CTE {numero_cte} já existe'
            }), 400
        
        # Criar novo CTE
        novo_cte = CTE(
            numero_cte=numero_cte,
            destinatario_nome=dados.get('destinatario_nome', ''),
            valor_total=dados.get('valor_total', 0),
            veiculo_placa=dados.get('veiculo_placa'),
            observacao=dados.get('observacao')
        )
        
        from app import db
        db.session.add(novo_cte)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'CTE {numero_cte} inserido com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
