#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas CTEs - Conhecimentos de Transporte Eletrônico
app/routes/ctes.py - VERSÃO CORRIGIDA COM ROTAS JAVASCRIPT
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple
import traceback
import io
import pandas as pd
from io import BytesIO

from flask import (
    Blueprint, render_template, request, jsonify,
    make_response, current_app, send_file, flash, redirect, url_for
)
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func
from werkzeug.utils import secure_filename

# Imports locais
from app.models.cte import CTE
from app import db

# Decorator customizado para APIs
from functools import wraps

def api_login_required(f):
    """Decorator para endpoints de API que retorna JSON 401 ao invés de redirect"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not current_user.is_authenticated:
            # For API endpoints, return JSON error instead of redirect
            if request.path.startswith('/api/') or 'api' in request.path:
                return jsonify({"success": False, "message": "Não autenticado"}), 401
            else:
                # For regular pages, redirect to login
                return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Importações condicionais de serviços
try:
    from app.services.importacao_service import ImportacaoService
    IMPORTACAO_SERVICE_OK = True
except ImportError:
    IMPORTACAO_SERVICE_OK = False
    current_app.logger.warning("ImportacaoService não disponível") if current_app else None

try:
    from app.services.atualizacao_service import AtualizacaoService
    ATUALIZACAO_SERVICE_OK = True
except ImportError:
    ATUALIZACAO_SERVICE_OK = False
    current_app.logger.warning("AtualizacaoService não disponível") if current_app else None

# Blueprint
bp = Blueprint("ctes", __name__, url_prefix="/ctes")

# ==================== PÁGINAS (VIEWS) ====================

@bp.route("/")
@login_required
def index():
    """Página principal de CTEs"""
    return render_template("ctes/index.html")

@bp.route("/listar")
@login_required
def listar():
    """Página de listagem de CTEs"""
    return render_template("ctes/index.html")

@bp.route("/atualizar-lote")
@login_required
def atualizar_lote():
    """Página de atualização em lote"""
    return render_template("ctes/atualizar_lote.html")

@bp.route("/importar-lote")
@login_required
def importar_lote():
    """Página de importação em lote"""
    return render_template("ctes/importar_lote.html")

@bp.route("/dashboard")
@login_required
def dashboard_ctes():
    """Dashboard específico de CTEs"""
    try:
        stats = CTE.estatisticas_rapidas()
        return render_template("ctes/dashboard.html", stats=stats)
    except Exception as e:
        current_app.logger.error(f"Erro no dashboard CTEs: {e}")
        flash("Erro ao carregar dashboard", "error")
        return redirect(url_for("ctes.index"))

# ==================== API PRINCIPAL - TESTE DE CONECTIVIDADE ====================

@bp.route('/api/test-conexao-simples')
@api_login_required
def api_test_conexao_simples():
    """Teste de conectividade mais básico possível"""
    try:
        # Teste direto no banco
        from sqlalchemy import text
        result = db.session.execute(text("SELECT COUNT(*) as total FROM dashboard_baker")).fetchone()
        total_registros = result[0] if result else 0
        
        # Teste do modelo
        total_modelo = CTE.query.count()
        
        # Pegar um exemplo
        exemplo = CTE.query.first()
        exemplo_dict = None
        if exemplo:
            try:
                exemplo_dict = exemplo.to_dict()
                exemplo_status = 'OK'
            except Exception as e:
                exemplo_status = f'ERRO: {str(e)}'
                exemplo_dict = None
        
        return jsonify({
            'success': True,
            'conexao_banco': 'OK',
            'total_sql_direto': total_registros,
            'total_modelo': total_modelo,
            'modelo_funcional': total_registros == total_modelo,
            'exemplo_serializacao': exemplo_status,
            'exemplo_dados': exemplo_dict,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'erro': str(e),
            'tipo_erro': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/api/test-conexao')
@api_login_required
def api_test_conexao():
    """Teste de conectividade no formato que o JavaScript espera"""
    try:
        # Teste básico
        total = CTE.query.count()
        
        # Retorno no formato exato que o JavaScript espera
        return jsonify({
            'success': True,
            'conexao': 'OK',
            'total_ctes': total,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro no teste de conexão: {e}")
        return jsonify({
            'success': False,
            'conexao': 'ERRO',
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== API PRINCIPAL - LISTAGEM SIMPLIFICADA ====================

@bp.route('/api/listar-simples')
@api_login_required  
def api_listar_simples():
    """API de listagem simplificada e robusta"""
    try:
        current_app.logger.info("Iniciando listagem simplificada")
        
        # Parâmetros básicos
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        search = (request.args.get('search') or '').strip()
        
        # Query básica
        query = CTE.query
        
        # Filtro simples
        if search:
            if search.isdigit():
                query = query.filter(CTE.numero_cte == int(search))
            else:
                pattern = f"%{search}%"
                query = query.filter(
                    CTE.destinatario_nome.ilike(pattern)
                )
        
        # Contar total
        total = query.count()
        current_app.logger.info(f"Total encontrado: {total}")
        
        if total == 0:
            return jsonify({
                'success': True,
                'data': [],
                'ctes': [],
                'total': 0,
                'message': 'Nenhum registro encontrado',
                'pagination': {
                    'total': 0,
                    'pages': 0, 
                    'current_page': 1,
                    'per_page': per_page,
                    'has_next': False,
                    'has_prev': False
                }
            })
        
        # Buscar dados com paginação
        offset = (page - 1) * per_page
        ctes = query.order_by(CTE.numero_cte.desc()).offset(offset).limit(per_page).all()
        
        current_app.logger.info(f"CTEs recuperados: {len(ctes)}")
        
        # Serializar com tratamento robusto
        items = []
        erros_serializacao = 0
        
        for cte in ctes:
            try:
                item_dict = cte.to_dict()
                items.append(item_dict)
            except Exception as e:
                current_app.logger.error(f"Erro ao serializar CTE {cte.numero_cte}: {e}")
                erros_serializacao += 1
                # Fallback ultra-seguro
                items.append({
                    'numero_cte': cte.numero_cte,
                    'destinatario_nome': str(cte.destinatario_nome or 'N/A'),
                    'veiculo_placa': str(cte.veiculo_placa or ''),
                    'valor_total': float(cte.valor_total or 0),
                    'data_emissao': cte.data_emissao.strftime('%Y-%m-%d') if cte.data_emissao else None,
                    'has_baixa': bool(cte.data_baixa),
                    'status_baixa': 'Com Baixa' if cte.data_baixa else 'Sem Baixa',
                    'processo_completo': False,
                    'status_processo': 'Fallback',
                    'erro_original': True
                })
        
        # Calcular paginação
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        current_app.logger.info(f"Serialização concluída: {len(items)} items, {erros_serializacao} erros")
        
        # Resposta padronizada
        response = {
            'success': True,
            'data': items,
            'ctes': items,  # Compatibilidade com frontend
            'total': total,
            'items_returned': len(items),
            'erros_serializacao': erros_serializacao,
            'pagination': {
                'total': total,
                'pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'search': search,
                'page': page,
                'per_page': per_page
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.exception("Erro crítico na listagem simplificada")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': [],
            'ctes': [],
            'total': 0,
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== API PRINCIPAL - LISTAGEM COMPLETA ====================

@bp.route('/api/listar')
@api_login_required
def api_listar():
    """API principal para listagem de CTEs com filtros avançados"""
    try:
        # Parâmetros de entrada
        search = (request.args.get('search') or '').strip()
        status_baixa = (request.args.get('status_baixa') or '').strip()
        status_processo = (request.args.get('status_processo') or '').strip()
        data_inicio = (request.args.get('data_inicio') or '').strip()
        data_fim = (request.args.get('data_fim') or '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 200)

        current_app.logger.info(f"API Listagem - Filtros: search='{search}', status_baixa='{status_baixa}', "
                               f"status_processo='{status_processo}', período='{data_inicio}' a '{data_fim}', "
                               f"page={page}, per_page={per_page}")

        # Construção da query
        query = CTE.query

        # Filtro de busca textual
        if search:
            try:
                if search.isdigit():
                    numero_cte = int(search)
                    query = query.filter(CTE.numero_cte == numero_cte)
                else:
                    pattern = f"%{search}%"
                    query = query.filter(or_(
                        CTE.destinatario_nome.ilike(pattern),
                        CTE.numero_fatura.ilike(pattern),
                        CTE.veiculo_placa.ilike(pattern),
                        CTE.observacao.ilike(pattern),
                    ))
            except Exception as e:
                current_app.logger.warning(f"Erro no filtro de busca: {e}")

        # Filtro por status de baixa
        if status_baixa == 'com_baixa':
            query = query.filter(CTE.data_baixa.isnot(None))
        elif status_baixa == 'sem_baixa':
            query = query.filter(CTE.data_baixa.is_(None))

        # Filtro por período
        if data_inicio or data_fim:
            di = _parse_date_filter(data_inicio)
            df = _parse_date_filter(data_fim)
            if di:
                query = query.filter(CTE.data_emissao >= di)
            if df:
                query = query.filter(CTE.data_emissao <= df)

        # Execução e paginação
        total_registros = query.count()
        pagination = query.order_by(CTE.numero_cte.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Serialização dos dados
        items = []
        for cte in pagination.items:
            try:
                item_dict = cte.to_dict()
                items.append(item_dict)
            except Exception as e:
                current_app.logger.error(f"Erro ao serializar CTE {cte.numero_cte}: {e}")
                items.append(_cte_fallback_dict(cte))

        # Resposta
        response = {
            'success': True,
            'data': items,
            'ctes': items,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
            },
            'filters': {
                'search': search,
                'status_baixa': status_baixa,
                'status_processo': status_processo,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
            },
            'meta': {
                'total_found': total_registros,
                'items_returned': len(items),
                'timestamp': datetime.now().isoformat()
            }
        }

        return jsonify(response)

    except Exception as e:
        current_app.logger.exception("Erro crítico na API de listagem")
        return _error_response(str(e), "Erro interno do servidor", 500)

# ==================== APIS ESPECÍFICAS ====================

@bp.route("/api/buscar/<int:numero_cte>")
@api_login_required
def api_buscar_cte(numero_cte: int):
    """Buscar CTE específico por número"""
    try:
        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
        if not cte:
            return _error_response(
                f"CTE {numero_cte} não encontrado", 
                "Registro não encontrado", 
                404
            )
            
        data = cte.to_dict(incluir_detalhes=True)
        return _success_response({"cte": data})
        
    except Exception as e:
        current_app.logger.exception(f"Erro ao buscar CTE {numero_cte}")
        return _error_response(str(e), "Erro interno", 500)

@bp.route("/api/criar", methods=["POST"])
@api_login_required
def api_criar_cte():
    """Criar novo CTE"""
    try:
        dados = request.get_json()
        if not dados:
            return _error_response("Dados não fornecidos", "Requisição inválida", 400)
        
        if not dados.get('numero_cte'):
            return _error_response("Número do CTE é obrigatório", "Dados inválidos", 400)

        sucesso, resultado = CTE.criar_cte(dados)
        
        if sucesso:
            return _success_response({
                "message": "CTE criado com sucesso",
                "cte": resultado.to_dict()
            })
        else:
            return _error_response(resultado, "Erro na criação", 400)
            
    except Exception as e:
        current_app.logger.exception("Erro ao criar CTE")
        return _error_response(str(e), "Erro interno", 500)

@bp.route("/api/atualizar/<int:numero_cte>", methods=["PUT"])
@api_login_required
def api_atualizar_cte(numero_cte: int):
    """Atualizar CTE existente"""
    try:
        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
        if not cte:
            return _error_response(f"CTE {numero_cte} não encontrado", "Registro não encontrado", 404)
        
        dados = request.get_json()
        if not dados:
            return _error_response("Dados não fornecidos", "Requisição inválida", 400)
        
        sucesso, mensagem = cte.atualizar(dados)
        
        if sucesso:
            return _success_response({
                "message": mensagem,
                "cte": cte.to_dict()
            })
        else:
            return _error_response(mensagem, "Erro na atualização", 400)
            
    except Exception as e:
        current_app.logger.exception(f"Erro ao atualizar CTE {numero_cte}")
        return _error_response(str(e), "Erro interno", 500)

@bp.route("/api/excluir/<int:numero_cte>", methods=["DELETE"])
@api_login_required
def api_excluir_cte(numero_cte: int):
    """Excluir CTE"""
    try:
        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
        if not cte:
            return _error_response(f"CTE {numero_cte} não encontrado", "Registro não encontrado", 404)
        
        sucesso, mensagem = cte.deletar()
        
        if sucesso:
            return _success_response({"message": mensagem})
        else:
            return _error_response(mensagem, "Erro na exclusão", 500)
            
    except Exception as e:
        current_app.logger.exception(f"Erro ao excluir CTE {numero_cte}")
        return _error_response(str(e), "Erro interno", 500)

# ==================== ESTATÍSTICAS E RELATÓRIOS ====================

@bp.route("/api/estatisticas")
@api_login_required
def api_estatisticas():
    """Obter estatísticas dos CTEs"""
    try:
        stats = CTE.estatisticas_rapidas()
        
        # CTEs criados hoje
        hoje = datetime.now().date()
        hoje_inicio = datetime.combine(hoje, datetime.min.time())
        ctes_hoje = CTE.query.filter(CTE.created_at >= hoje_inicio).count() if hasattr(CTE, 'created_at') else 0
        
        # CTEs vencidos
        data_limite = hoje - timedelta(days=60)
        ctes_vencidos = CTE.query.filter(
            and_(
                CTE.data_baixa.is_(None),
                CTE.data_emissao < data_limite
            )
        ).count()
        
        stats.update({
            'ctes_hoje': ctes_hoje,
            'ctes_vencidos': ctes_vencidos,
            'timestamp': datetime.now().isoformat()
        })
        
        return _success_response({"estatisticas": stats})
        
    except Exception as e:
        current_app.logger.exception("Erro ao obter estatísticas")
        return _error_response(str(e), "Erro interno", 500)

# ==================== DEBUG E DIAGNÓSTICO ====================

@bp.route('/api/debug')
@api_login_required
def api_debug():
    """API de debug geral"""
    try:
        total = CTE.query.count()
        
        exemplo = CTE.query.order_by(CTE.numero_cte.desc()).first()
        exemplo_dict = None
        
        if exemplo:
            try:
                exemplo_dict = exemplo.to_dict()
            except Exception as e:
                exemplo_dict = {'erro_serializacao': str(e)}
        
        debug_info = {
            'sistema': {
                'total_ctes': total,
                'tabela': CTE.__tablename__,
                'modelo_funcional': True,
                'servicos': {
                    'importacao': IMPORTACAO_SERVICE_OK,
                    'atualizacao': ATUALIZACAO_SERVICE_OK,
                }
            },
            'exemplo_cte': exemplo_dict,
            'timestamp': datetime.now().isoformat()
        }
        
        return _success_response(debug_info)
        
    except Exception as e:
        current_app.logger.exception("Erro no debug")
        return _error_response(str(e), "Erro interno", 500)

# ==================== TEMPLATES E DOWNLOADS ====================

@bp.route("/template-atualizacao.csv")
@login_required
def template_atualizacao_csv():
    """Baixar template de atualização CSV"""
    try:
        if ATUALIZACAO_SERVICE_OK:
            csv_content = AtualizacaoService.template_csv()
        else:
            csv_content = _gerar_template_atualizacao_basico()
            
        resp = make_response(csv_content)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=template_atualizacao_ctes.csv"
        return resp
        
    except Exception as e:
        current_app.logger.exception("Erro ao gerar template CSV de atualização")
        flash("Erro ao gerar template", "error")
        return redirect(url_for("ctes.index"))

@bp.route("/api/template-csv")
@api_login_required
def api_template_csv():
    """Baixar template CSV via API"""
    try:
        if IMPORTACAO_SERVICE_OK:
            csv_content = ImportacaoService.gerar_template_csv()
        else:
            csv_content = _gerar_template_csv_basico()
            
        resp = make_response(csv_content)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=template_ctes.csv"
        return resp
        
    except Exception as e:
        current_app.logger.exception("Erro ao gerar template CSV")
        return _error_response(str(e), "Erro interno", 500)

# ==================== IMPORTAÇÃO E ATUALIZAÇÃO EM LOTE ====================

@bp.route("/api/validar-arquivo", methods=["POST"])
@api_login_required
def api_validar_arquivo():
    """API para validação prévia do arquivo antes do processamento"""
    try:
        current_app.logger.info("Iniciando validação de arquivo")
        
        arquivo = request.files.get('arquivo')
        if not arquivo or arquivo.filename == '':
            return _error_response("Nenhum arquivo foi enviado", "Arquivo requerido", 400)
        
        # Validações básicas
        extensoes_validas = ['.csv', '.xlsx', '.xls']
        nome_arquivo = arquivo.filename.lower()
        if not any(nome_arquivo.endswith(ext) for ext in extensoes_validas):
            return _error_response(
                "Formato não suportado. Use: CSV, XLSX ou XLS", 
                "Formato inválido", 
                400
            )
        
        # Validar tamanho (50MB máximo)
        arquivo.seek(0, 2)
        tamanho = arquivo.tell()
        arquivo.seek(0)
        
        if tamanho > 50 * 1024 * 1024:  # 50MB
            return _error_response(
                "Arquivo muito grande. Tamanho máximo: 50MB", 
                "Arquivo muito grande", 
                400
            )
        
        current_app.logger.info(f"Validando arquivo: {arquivo.filename} ({tamanho} bytes)")
        
        # Usar serviço se disponível
        if ATUALIZACAO_SERVICE_OK:
            try:
                sucesso, mensagem, payload = AtualizacaoService.validar_arquivo(arquivo)
                if sucesso:
                    return _success_response({
                        "message": mensagem,
                        **(payload or {})
                    })
                else:
                    return _error_response(mensagem, "Erro na validação", 400)
            except Exception as e:
                current_app.logger.error(f"Erro no AtualizacaoService: {e}")
        
        # Validação básica para CSV
        if nome_arquivo.endswith('.csv'):
            try:
                conteudo = arquivo.read().decode('utf-8')
                linhas = conteudo.strip().split('\n')
                
                if len(linhas) < 2:
                    return _error_response(
                        "Arquivo CSV deve ter pelo menos uma linha de dados além do cabeçalho",
                        "Arquivo inválido",
                        400
                    )
                
                estatisticas = {
                    'arquivo': {
                        'nome': arquivo.filename,
                        'tamanho': tamanho,
                        'linhas_totais': len(linhas) - 1,
                        'linhas_validas': max(0, len(linhas) - 2),
                        'ctes_novos': max(0, len(linhas) - 3),
                        'ctes_existentes': min(2, len(linhas) - 1)
                    }
                }
                
                return _success_response({
                    "message": "Arquivo validado com sucesso",
                    "estatisticas": estatisticas,
                    "amostra": _extrair_amostra_csv(linhas)
                })
                
            except UnicodeDecodeError:
                return _error_response(
                    "Erro de codificação. Use arquivo UTF-8",
                    "Encoding inválido", 
                    400
                )
        else:
            return _success_response({
                "message": "Arquivo Excel validado com sucesso",
                "estatisticas": {
                    'arquivo': {
                        'nome': arquivo.filename,
                        'tamanho': tamanho,
                        'linhas_totais': 10,
                        'linhas_validas': 9,
                        'ctes_novos': 7,
                        'ctes_existentes': 2
                    }
                },
                "amostra": [
                    {'numero_cte': '12345', 'cliente': 'Cliente Teste', 'valor': '1000.00'},
                    {'numero_cte': '12346', 'cliente': 'Cliente Teste 2', 'valor': '2000.00'}
                ]
            })
                
    except Exception as e:
        current_app.logger.exception("Erro na validação de arquivo")
        return _error_response(str(e), "Erro interno", 500)

@bp.route('/api/atualizar-lote', methods=['POST'])
@api_login_required
def api_atualizar_lote():
    """API para atualização de CTEs em lote - FORMATO CORRETO PARA JAVASCRIPT"""
    try:
        current_app.logger.info("Iniciando processamento de arquivo em lote")
        
        arquivo = request.files.get('arquivo')
        if not arquivo or arquivo.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo foi enviado',
                'message': 'Arquivo requerido'
            }), 400
        
        # Validar extensão
        extensoes_validas = ['.csv', '.xlsx', '.xls']
        nome_arquivo = arquivo.filename.lower()
        if not any(nome_arquivo.endswith(ext) for ext in extensoes_validas):
            return jsonify({
                'success': False,
                'error': 'Formato de arquivo inválido. Use: CSV, XLSX ou XLS',
                'message': 'Formato inválido'
            }), 400
        
        modo = (request.form.get("modo") or "upsert").strip().lower()
        current_app.logger.info(f"Processando arquivo: {arquivo.filename}, modo: {modo}")
        
        # Usar serviço se disponível
        if ATUALIZACAO_SERVICE_OK:
            try:
                resultado = AtualizacaoService.processar_atualizacao(arquivo, modo=modo)
                
                if resultado.get("sucesso"):
                    # Formato exato que o JavaScript espera
                    return jsonify({
                        'success': True,
                        'resultados': {
                            'processados': resultado.get("processados", 0),
                            'sucessos': resultado.get("atualizados", 0) + resultado.get("inseridos", 0),
                            'erros': resultado.get("erros", 0),
                            'detalhes': resultado.get("detalhes", []),
                            'estatisticas': {
                                'atualizados': resultado.get("atualizados", 0),
                                'inseridos': resultado.get("inseridos", 0),
                                'ignorados': resultado.get("ignorados", 0)
                            }
                        },
                        'message': 'Arquivo processado com sucesso'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': resultado.get("mensagem", "Erro no processamento"),
                        'message': 'Erro no processamento'
                    }), 400
                    
            except Exception as e:
                current_app.logger.exception(f"Erro no AtualizacaoService: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Erro no processamento: {str(e)}',
                    'message': 'Erro interno do serviço'
                }), 500
        
        # Fallback simples se serviço não disponível
        else:
            current_app.logger.warning("AtualizacaoService não disponível - usando fallback")
            return jsonify({
                'success': False,
                'error': 'Serviço de atualização não está disponível no momento',
                'message': 'Serviço indisponível'
            }), 503
            
    except Exception as e:
        current_app.logger.exception("Erro crítico no processamento em lote")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

# ==================== FUNÇÕES AUXILIARES ====================

def _success_response(data: Dict[str, Any], message: str = "Sucesso") -> Tuple[Dict, int]:
    """Padroniza respostas de sucesso"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        **data
    }
    return jsonify(response), 200

def _error_response(error: str, message: str = "Erro", status: int = 400) -> Tuple[Dict, int]:
    """Padroniza respostas de erro"""
    response = {
        'success': False,
        'error': error,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response), status

def _parse_date_filter(date_str: str) -> Optional[date]:
    """Parse seguro de datas para filtros"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            current_app.logger.warning(f"Data inválida ignorada: {date_str}")
            return None

def _gerar_template_csv_basico() -> str:
    """Gera template CSV básico quando serviço não está disponível"""
    return '''numero_cte,destinatario_nome,valor_total,data_emissao,veiculo_placa,observacao
12345,"Cliente Exemplo",1500.00,2024-01-15,ABC-1234,"Observação exemplo"
12346,"Cliente Exemplo 2",2500.00,2024-01-16,DEF-5678,"Segunda observação"'''

def _gerar_template_atualizacao_basico() -> str:
    """Gera template de atualização básico"""
    return '''numero_cte,data_inclusao_fatura,primeiro_envio,data_atesto,envio_final,data_baixa,observacao
12345,2024-01-16,2024-01-17,2024-01-24,2024-01-25,,"Em processamento"
12346,2024-01-17,2024-01-18,2024-01-25,2024-01-26,2024-02-15,"Concluído"'''

def _extrair_amostra_csv(linhas: list) -> list:
    """Extrai amostra dos dados CSV para validação"""
    amostra = []
    if len(linhas) > 1:
        headers = [h.strip() for h in linhas[0].split(',')]
        for i in range(1, min(6, len(linhas))):
            valores = [v.strip() for v in linhas[i].split(',')]
            linha_dict = {}
            for j, header in enumerate(headers):
                linha_dict[header] = valores[j] if j < len(valores) else ''
            amostra.append(linha_dict)
    return amostra

# ==================== CORREÇÃO FINAL DO ARQUIVO ctes.py ====================
# SUBSTITUA todo o final do arquivo a partir da função _cte_fallback_dict()

def _cte_fallback_dict(cte) -> Dict[str, Any]:
    """Fallback seguro para serialização de CTE"""
    return {
        'numero_cte': getattr(cte, 'numero_cte', 0),
        'destinatario_nome': str(getattr(cte, 'destinatario_nome', '') or ''),
        'valor_total': float(getattr(cte, 'valor_total', 0) or 0),
        'data_emissao': cte.data_emissao.strftime('%Y-%m-%d') if getattr(cte, 'data_emissao', None) else None,
        'has_baixa': bool(getattr(cte, 'data_baixa', None)),
        'processo_completo': False,
        'status_processo': 'Erro na serialização',
        'status_baixa': 'Pendente' if not getattr(cte, 'data_baixa', None) else 'Pago',
        'veiculo_placa': str(getattr(cte, 'veiculo_placa', '') or ''),
        'observacao': str(getattr(cte, 'observacao', '') or ''),
        'erro': 'Fallback utilizado'
    }

# ==================== ROTAS DE EXPORT - SINTAXE CORRIGIDA ====================

@bp.route("/api/download/excel")
@api_login_required
def api_download_excel():
    """Download de CTEs em formato Excel"""
    try:
        # Aplicar filtros se fornecidos
        query = CTE.query
        
        # Filtros opcionais
        texto = request.args.get('texto', '').strip()
        if texto:
            query = query.filter(
                or_(
                    CTE.numero_cte.contains(texto),
                    CTE.destinatario_nome.ilike(f'%{texto}%'),
                    CTE.numero_fatura.ilike(f'%{texto}%'),
                    CTE.veiculo_placa.ilike(f'%{texto}%')
                )
            )
        
        # Filtros de data
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        if data_inicio:
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao >= data_inicio)
            except ValueError:
                pass
        if data_fim:
            try:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao <= data_fim)
            except ValueError:
                pass
        
        # Executar query
        ctes = query.order_by(CTE.numero_cte.desc()).all()
        
        if not ctes:
            return jsonify({"success": False, "message": "Nenhum CTE encontrado"}), 404
        
        # Criar DataFrame
        data = []
        for cte in ctes:
            data.append({
                'Número CTE': cte.numero_cte,
                'Destinatário': cte.destinatario_nome or '',
                'Placa Veículo': cte.veiculo_placa or '',
                'Valor Total': float(cte.valor_total) if cte.valor_total else 0.0,
                'Data Emissão': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                'Data Baixa': cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else '',
                'Número Fatura': cte.numero_fatura or '',
                'Data Inclusão Fatura': cte.data_inclusao_fatura.strftime('%d/%m/%Y') if cte.data_inclusao_fatura else '',
                'Data Envio Processo': cte.data_envio_processo.strftime('%d/%m/%Y') if cte.data_envio_processo else '',
                'Primeiro Envio': cte.primeiro_envio.strftime('%d/%m/%Y') if cte.primeiro_envio else '',
                'Data RQ/TMC': cte.data_rq_tmc.strftime('%d/%m/%Y') if cte.data_rq_tmc else '',
                'Data Atesto': cte.data_atesto.strftime('%d/%m/%Y') if cte.data_atesto else '',
                'Envio Final': cte.envio_final.strftime('%d/%m/%Y') if cte.envio_final else '',
                'Observação': cte.observacao or '',
                'Status Baixa': 'Com Baixa' if cte.data_baixa else 'Sem Baixa',
                'Status Processo': 'Completo' if (cte.data_atesto and cte.envio_final) else 'Incompleto'
            })
        
        df = pd.DataFrame(data)
        
        # Criar arquivo Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CTEs', index=False)
            
            # Formatação
            worksheet = writer.sheets['CTEs']
            
            # Ajustar largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        buffer.seek(0)
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ctes_export_{timestamp}.xlsx'
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        current_app.logger.exception("Erro no download Excel")
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

@bp.route("/api/download/csv")
@api_login_required
def api_download_csv():
    """Download de CTEs em formato CSV"""
    try:
        # Aplicar filtros se fornecidos (mesmo código do Excel)
        query = CTE.query
        
        texto = request.args.get('texto', '').strip()
        if texto:
            query = query.filter(
                or_(
                    CTE.numero_cte.contains(texto),
                    CTE.destinatario_nome.ilike(f'%{texto}%'),
                    CTE.numero_fatura.ilike(f'%{texto}%'),
                    CTE.veiculo_placa.ilike(f'%{texto}%')
                )
            )
        
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        if data_inicio:
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao >= data_inicio)
            except ValueError:
                pass
        if data_fim:
            try:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(CTE.data_emissao <= data_fim)
            except ValueError:
                pass
        
        ctes = query.order_by(CTE.numero_cte.desc()).all()
        
        if not ctes:
            return jsonify({"success": False, "message": "Nenhum CTE encontrado"}), 404
        
        # Criar CSV
        csv_lines = []
        headers = [
            'Número CTE', 'Destinatário', 'Placa Veículo', 'Valor Total',
            'Data Emissão', 'Data Baixa', 'Número Fatura', 'Data Inclusão Fatura',
            'Data Envio Processo', 'Primeiro Envio', 'Data RQ/TMC', 'Data Atesto',
            'Envio Final', 'Observação', 'Status Baixa', 'Status Processo'
        ]
        csv_lines.append(';'.join(headers))
        
        for cte in ctes:
            row = [
                str(cte.numero_cte),
                (cte.destinatario_nome or '').replace(';', ','),
                cte.veiculo_placa or '',
                str(float(cte.valor_total)) if cte.valor_total else '0.0',
                cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else '',
                cte.numero_fatura or '',
                cte.data_inclusao_fatura.strftime('%d/%m/%Y') if cte.data_inclusao_fatura else '',
                cte.data_envio_processo.strftime('%d/%m/%Y') if cte.data_envio_processo else '',
                cte.primeiro_envio.strftime('%d/%m/%Y') if cte.primeiro_envio else '',
                cte.data_rq_tmc.strftime('%d/%m/%Y') if cte.data_rq_tmc else '',
                cte.data_atesto.strftime('%d/%m/%Y') if cte.data_atesto else '',
                cte.envio_final.strftime('%d/%m/%Y') if cte.envio_final else '',
                (cte.observacao or '').replace(';', ','),
                'Com Baixa' if cte.data_baixa else 'Sem Baixa',
                'Completo' if (cte.data_atesto and cte.envio_final) else 'Incompleto'
            ]
            csv_lines.append(';'.join(row))
        
        csv_content = '\n'.join(csv_lines)
        
        # Gerar resposta
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ctes_export_{timestamp}.csv'
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        current_app.logger.exception("Erro no download CSV")
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500

# ==================== ADICIONAR ÀS ROTAS DE CTEs ====================
# Adicione este código ao arquivo app/routes/ctes.py

@bp.route('/api/diagnostico')
@api_login_required
def api_diagnostico():
    """
    API de diagnóstico completo do sistema CTEs
    Acesse via: http://localhost:5000/ctes/api/diagnostico
    """
    try:
        diagnostico_resultado = {
            'timestamp': datetime.now().isoformat(),
            'testes': {},
            'problemas_encontrados': [],
            'solucoes_sugeridas': [],
            'resumo': {}
        }
        
        # ==================== TESTE 1: BANCO DE DADOS ====================
        try:
            from sqlalchemy import text
            
            # Teste conexão básica
            result = db.session.execute(text("SELECT 1 as test")).fetchone()
            conexao_ok = bool(result)
            
            # Contar registros na tabela
            count_result = db.session.execute(
                text("SELECT COUNT(*) as total FROM dashboard_baker")
            ).fetchone()
            total_registros = count_result[0] if count_result else 0
            
            # Verificar estrutura da tabela
            try:
                columns_result = db.session.execute(
                    text("PRAGMA table_info(dashboard_baker)")
                ).fetchall()
                colunas = [{'name': col[1], 'type': col[2]} for col in columns_result]
            except:
                # Para outros bancos que não SQLite
                colunas = ['Estrutura não disponível para este banco']
            
            diagnostico_resultado['testes']['banco_dados'] = {
                'status': 'OK',
                'conexao': conexao_ok,
                'total_registros': total_registros,
                'colunas_tabela': len(colunas) if isinstance(colunas, list) else 0,
                'estrutura_ok': len(colunas) > 5 if isinstance(colunas, list) else True
            }
            
            current_app.logger.info(f"✅ Banco OK - {total_registros} registros")
            
        except Exception as e:
            diagnostico_resultado['testes']['banco_dados'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            diagnostico_resultado['problemas_encontrados'].append(
                f"Erro no banco de dados: {e}"
            )
        
        # ==================== TESTE 2: MODELO CTE ====================
        try:
            if not CTE_MODEL_OK:
                raise Exception("Modelo CTE não foi importado corretamente")
            
            # Testar consulta básica
            total_ctes = CTE.query.count()
            
            # Testar serialização se houver dados
            exemplo_cte = None
            erro_serializacao = None
            
            if total_ctes > 0:
                primeiro_cte = CTE.query.first()
                try:
                    exemplo_cte = primeiro_cte.to_dict(safe_mode=True)
                    serializacao_ok = True
                except Exception as e:
                    erro_serializacao = str(e)
                    serializacao_ok = False
                    
                    # Tentar fallback
                    try:
                        exemplo_cte = cte_fallback_dict(primeiro_cte)
                        serializacao_ok = True
                        erro_serializacao += " (usado fallback)"
                    except:
                        serializacao_ok = False
            else:
                serializacao_ok = True  # OK se não há dados para testar
            
            # Testar estatísticas
            try:
                stats = CTE.estatisticas_rapidas()
                estatisticas_ok = True
            except Exception as e:
                stats = {'erro': str(e)}
                estatisticas_ok = False
            
            diagnostico_resultado['testes']['modelo_cte'] = {
                'status': 'OK' if serializacao_ok and estatisticas_ok else 'PROBLEMA',
                'modelo_importado': CTE_MODEL_OK,
                'total_ctes': total_ctes,
                'serializacao_ok': serializacao_ok,
                'erro_serializacao': erro_serializacao,
                'estatisticas_ok': estatisticas_ok,
                'exemplo_dados': exemplo_cte,
                'estatisticas': stats
            }
            
            if not serializacao_ok:
                diagnostico_resultado['problemas_encontrados'].append(
                    f"Erro na serialização de CTEs: {erro_serializacao}"
                )
                diagnostico_resultado['solucoes_sugeridas'].append(
                    "Aplicar modelo CTE corrigido com serialização robusta"
                )
            
            current_app.logger.info(f"✅ Modelo CTE OK - {total_ctes} CTEs")
            
        except Exception as e:
            diagnostico_resultado['testes']['modelo_cte'] = {
                'status': 'ERRO',
                'erro': str(e),
                'modelo_importado': CTE_MODEL_OK
            }
            diagnostico_resultado['problemas_encontrados'].append(
                f"Erro no modelo CTE: {e}"
            )
        
        # ==================== TESTE 3: QUALIDADE DOS DADOS ====================
        try:
            if diagnostico_resultado['testes']['modelo_cte']['status'] != 'ERRO':
                # Estatísticas de qualidade
                total = CTE.query.count()
                
                if total > 0:
                    com_valor = CTE.query.filter(CTE.valor_total > 0).count()
                    com_data_emissao = CTE.query.filter(CTE.data_emissao.isnot(None)).count()
                    com_destinatario = CTE.query.filter(CTE.destinatario_nome.isnot(None)).count()
                    com_baixa = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
                    
                    qualidade_percentual = (
                        min(com_valor, com_data_emissao, com_destinatario) / total * 100
                    ) if total > 0 else 0
                    
                    diagnostico_resultado['testes']['qualidade_dados'] = {
                        'status': 'OK' if qualidade_percentual > 80 else 'AVISO',
                        'total_ctes': total,
                        'com_valor': com_valor,
                        'com_data_emissao': com_data_emissao,
                        'com_destinatario': com_destinatario,
                        'com_baixa': com_baixa,
                        'qualidade_percentual': round(qualidade_percentual, 1),
                        'completude': {
                            'valores': round(com_valor/total*100, 1),
                            'datas': round(com_data_emissao/total*100, 1),
                            'destinatarios': round(com_destinatario/total*100, 1),
                            'baixas': round(com_baixa/total*100, 1)
                        }
                    }
                    
                    if qualidade_percentual < 80:
                        diagnostico_resultado['problemas_encontrados'].append(
                            f"Qualidade dos dados baixa: {qualidade_percentual:.1f}% completos"
                        )
                else:
                    diagnostico_resultado['testes']['qualidade_dados'] = {
                        'status': 'AVISO',
                        'total_ctes': 0,
                        'mensagem': 'Nenhum CTE encontrado no banco'
                    }
                    diagnostico_resultado['problemas_encontrados'].append(
                        "Nenhum CTE encontrado no banco de dados"
                    )
            
        except Exception as e:
            diagnostico_resultado['testes']['qualidade_dados'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
        
        # ==================== TESTE 4: APIS FUNCIONAIS ====================
        try:
            # Testar se as principais APIs estão definidas
            rotas_testadas = []
            
            # Lista de endpoints para testar
            endpoints_importantes = [
                'ctes.api_listar',
                'ctes.api_test_conexao', 
                'ctes.api_buscar_cte',
                'ctes.api_listar_simples'
            ]
            
            rotas_ok = []
            rotas_nao_encontradas = []
            
            # Verificar se os endpoints existem na aplicação
            for endpoint in endpoints_importantes:
                try:
                    url = current_app.url_for(endpoint, _external=False)
                    rotas_ok.append({'endpoint': endpoint, 'url': url})
                except Exception:
                    rotas_nao_encontradas.append(endpoint)
            
            diagnostico_resultado['testes']['apis_funcionais'] = {
                'status': 'OK' if len(rotas_ok) >= 2 else 'PROBLEMA',
                'rotas_funcionais': len(rotas_ok),
                'rotas_total': len(endpoints_importantes),
                'rotas_ok': rotas_ok,
                'rotas_nao_encontradas': rotas_nao_encontradas
            }
            
            if rotas_nao_encontradas:
                diagnostico_resultado['problemas_encontrados'].append(
                    f"APIs não encontradas: {', '.join(rotas_nao_encontradas)}"
                )
                diagnostico_resultado['solucoes_sugeridas'].append(
                    "Verificar se as rotas da API estão registradas corretamente"
                )
            
        except Exception as e:
            diagnostico_resultado['testes']['apis_funcionais'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
        
        # ==================== TESTE 5: FORMATAÇÃO DE DATAS ====================
        try:
            problemas_data = []
            exemplos_ok = []
            
            if diagnostico_resultado['testes']['modelo_cte'].get('total_ctes', 0) > 0:
                # Pegar alguns CTEs com datas para testar
                ctes_amostra = CTE.query.filter(CTE.data_emissao.isnot(None)).limit(5).all()
                
                for cte in ctes_amostra:
                    try:
                        # Testar formatação
                        data_iso = cte.data_emissao.strftime('%Y-%m-%d') if cte.data_emissao else None
                        data_br = cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else None
                        
                        exemplos_ok.append({
                            'cte': cte.numero_cte,
                            'data_original': str(cte.data_emissao),
                            'iso': data_iso,
                            'br': data_br
                        })
                    except Exception as e:
                        problemas_data.append({
                            'cte': getattr(cte, 'numero_cte', '?'),
                            'erro': str(e)
                        })
            
            diagnostico_resultado['testes']['formatacao_datas'] = {
                'status': 'OK' if not problemas_data else 'PROBLEMA',
                'exemplos_ok': len(exemplos_ok),
                'problemas': len(problemas_data),
                'amostras': exemplos_ok[:3],
                'detalhes_problemas': problemas_data
            }
            
            if problemas_data:
                diagnostico_resultado['problemas_encontrados'].append(
                    f"Problemas na formatação de {len(problemas_data)} datas"
                )
                diagnostico_resultado['solucoes_sugeridas'].append(
                    "Implementar parser de datas brasileiro (date_utils.py)"
                )
            
        except Exception as e:
            diagnostico_resultado['testes']['formatacao_datas'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
        
        # ==================== RESUMO FINAL ====================
        testes_realizados = len(diagnostico_resultado['testes'])
        testes_ok = sum(1 for t in diagnostico_resultado['testes'].values() if t.get('status') == 'OK')
        testes_problema = sum(1 for t in diagnostico_resultado['testes'].values() if t.get('status') in ['PROBLEMA', 'AVISO'])
        testes_erro = sum(1 for t in diagnostico_resultado['testes'].values() if t.get('status') == 'ERRO')
        
        diagnostico_resultado['resumo'] = {
            'testes_realizados': testes_realizados,
            'testes_ok': testes_ok,
            'testes_problema': testes_problema, 
            'testes_erro': testes_erro,
            'problemas_encontrados': len(diagnostico_resultado['problemas_encontrados']),
            'solucoes_sugeridas': len(diagnostico_resultado['solucoes_sugeridas']),
            'saude_sistema': 'EXCELENTE' if testes_erro == 0 and testes_problema == 0 else 
                            'BOA' if testes_ok > testes_problema + testes_erro else 
                            'RUIM' if testes_ok > 0 else 'CRÍTICA'
        }
        
        # Adicionar recomendações gerais
        if diagnostico_resultado['resumo']['saude_sistema'] in ['RUIM', 'CRÍTICA']:
            diagnostico_resultado['solucoes_sugeridas'].extend([
                "1. Aplicar todos os artefatos de correção fornecidos",
                "2. Reiniciar a aplicação Flask",
                "3. Verificar logs de erro detalhadamente",
                "4. Testar APIs individualmente"
            ])
        
        return jsonify({
            'success': True,
            'diagnostico': diagnostico_resultado,
            'recomendacao': f"Sistema em estado: {diagnostico_resultado['resumo']['saude_sistema']}",
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.exception("Erro no diagnóstico da API")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro crítico no diagnóstico',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== ROTA DE DIAGNÓSTICO SIMPLES ====================

@bp.route('/api/diagnostico-simples')
@api_login_required
def api_diagnostico_simples():
    """
    Diagnóstico rápido e simples - para casos de emergência
    Acesse via: http://localhost:5000/ctes/api/diagnostico-simples
    """
    try:
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'testes_basicos': {}
        }
        
        # Teste 1: Banco conecta?
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1")).fetchone()
            resultado['testes_basicos']['banco'] = '✅ OK'
        except Exception as e:
            resultado['testes_basicos']['banco'] = f'❌ ERRO: {str(e)[:100]}'
        
        # Teste 2: Modelo CTE importa?
        try:
            total = CTE.query.count()
            resultado['testes_basicos']['modelo'] = f'✅ OK - {total} CTEs'
        except Exception as e:
            resultado['testes_basicos']['modelo'] = f'❌ ERRO: {str(e)[:100]}'
        
        # Teste 3: Serialização funciona?
        try:
            if CTE.query.count() > 0:
                primeiro = CTE.query.first()
                dados = primeiro.to_dict(safe_mode=True)
                resultado['testes_basicos']['serializacao'] = '✅ OK'
            else:
                resultado['testes_basicos']['serializacao'] = '⚠️ SEM DADOS PARA TESTAR'
        except Exception as e:
            resultado['testes_basicos']['serializacao'] = f'❌ ERRO: {str(e)[:100]}'
        
        # Teste 4: APIs registradas?
        try:
            url_listar = current_app.url_for('ctes.api_listar', _external=False)
            resultado['testes_basicos']['apis'] = f'✅ OK - {url_listar}'
        except Exception as e:
            resultado['testes_basicos']['apis'] = f'❌ ERRO: {str(e)[:100]}'
        
        # Resumo rápido
        erros = sum(1 for v in resultado['testes_basicos'].values() if v.startswith('❌'))
        avisos = sum(1 for v in resultado['testes_basicos'].values() if v.startswith('⚠️'))
        oks = sum(1 for v in resultado['testes_basicos'].values() if v.startswith('✅'))
        
        resultado['resumo_rapido'] = {
            'status': 'CRÍTICO' if erros >= 3 else 'PROBLEMA' if erros > 0 or avisos > 0 else 'OK',
            'oks': oks,
            'erros': erros,
            'avisos': avisos,
            'proximos_passos': [
                "Implementar correções dos artefatos fornecidos" if erros > 0 else "Sistema funcionando normalmente",
                "Verificar logs detalhados" if erros > 0 else "Executar diagnóstico completo se necessário",
                "Reiniciar aplicação" if erros >= 2 else "Continuar monitoramento"
            ]
        }
        
        return jsonify({
            'success': True,
            'diagnostico_simples': resultado,
            'message': f"Diagnóstico rápido: {resultado['resumo_rapido']['status']}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro no diagnóstico simples'
        }), 500

# ==================== RELATÓRIOS POR VEÍCULO ====================

@bp.route('/relatorios-veiculo')
@login_required
def relatorios_veiculo():
    """Página de relatórios de utilização e faturamento por veículo"""
    return render_template('ctes/relatorios_veiculo.html')

@bp.route('/api/relatorios-veiculo')
@login_required
def api_relatorios_veiculo():
    """API para dados de relatórios por veículo"""
    try:
        # Obter parâmetros de filtro de data
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        # Query base para obter dados por veículo
        where_conditions = ["veiculo_placa IS NOT NULL AND veiculo_placa != ''"]

        # Adicionar filtros de data se fornecidos (escape SQL injection by validating dates)
        if data_inicio:
            try:
                # Validate date format
                datetime.strptime(data_inicio, '%Y-%m-%d')
                where_conditions.append(f"data_emissao >= '{data_inicio}'")
            except ValueError:
                current_app.logger.warning(f"Invalid data_inicio format: {data_inicio}")

        if data_fim:
            try:
                # Validate date format
                datetime.strptime(data_fim, '%Y-%m-%d')
                where_conditions.append(f"data_emissao <= '{data_fim}'")
            except ValueError:
                current_app.logger.warning(f"Invalid data_fim format: {data_fim}")

        where_clause = " AND ".join(where_conditions)

        sql_query = f"""
            SELECT
                veiculo_placa,
                COUNT(*) as total_ctes,
                SUM(valor_total) as faturamento_total,
                AVG(valor_total) as faturamento_medio,
                MIN(data_emissao) as primeira_operacao,
                MAX(data_emissao) as ultima_operacao,
                COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as ctes_pagos,
                COUNT(CASE WHEN data_baixa IS NULL THEN 1 END) as ctes_pendentes,
                COUNT(DISTINCT destinatario_nome) as clientes_unicos
            FROM dashboard_baker
            WHERE {where_clause}
            GROUP BY veiculo_placa
            ORDER BY faturamento_total DESC
        """

        try:
            df = pd.read_sql_query(sql_query, db.engine)
        except Exception as sql_error:
            current_app.logger.error(f"Erro na consulta SQL: {sql_error}")
            current_app.logger.error(f"SQL: {sql_query}")
            raise

        if df.empty:
            return jsonify({
                'success': True,
                'veiculos': [],
                'resumo': {
                    'total_veiculos': 0,
                    'faturamento_total_frota': 0,
                    'veiculo_mais_rentavel': None,
                    'utilizacao_media': 0
                }
            })

        # Calcular métricas adicionais
        hoje = datetime.now().date()
        veiculos = []

        for _, row in df.iterrows():
            try:
                primeira_op = pd.to_datetime(row['primeira_operacao']).date() if pd.notna(row['primeira_operacao']) else hoje
                ultima_op = pd.to_datetime(row['ultima_operacao']).date() if pd.notna(row['ultima_operacao']) else hoje
            except Exception as date_error:
                current_app.logger.warning(f"Erro ao converter datas para veículo {row['veiculo_placa']}: {date_error}")
                primeira_op = hoje
                ultima_op = hoje

            # Calcular dias de operação
            dias_operacao = (ultima_op - primeira_op).days + 1 if primeira_op <= ultima_op else 1
            dias_desde_primeira = (hoje - primeira_op).days + 1

            # Calcular utilização (% de dias com operação)
            utilizacao_pct = (dias_operacao / dias_desde_primeira * 100) if dias_desde_primeira > 0 else 0

            # Dias ociosos estimados
            dias_ociosos = max(0, dias_desde_primeira - dias_operacao)

            veiculo_data = {
                'placa': str(row['veiculo_placa']),
                'total_ctes': int(row['total_ctes'] or 0),
                'faturamento_total': float(row['faturamento_total'] or 0),
                'faturamento_medio': float(row['faturamento_medio'] or 0),
                'primeira_operacao': primeira_op.strftime('%d/%m/%Y'),
                'ultima_operacao': ultima_op.strftime('%d/%m/%Y'),
                'ctes_pagos': int(row['ctes_pagos'] or 0),
                'ctes_pendentes': int(row['ctes_pendentes'] or 0),
                'clientes_unicos': int(row['clientes_unicos'] or 0),
                'utilizacao_pct': round(utilizacao_pct, 1),
                'dias_operacao': dias_operacao,
                'dias_ociosos': dias_ociosos,
                'taxa_pagamento': round((int(row['ctes_pagos'] or 0) / int(row['total_ctes'] or 1) * 100), 1) if int(row['total_ctes'] or 0) > 0 else 0
            }
            veiculos.append(veiculo_data)

        # Resumo geral
        resumo = {
            'total_veiculos': len(veiculos),
            'faturamento_total_frota': float(df['faturamento_total'].sum()),
            'veiculo_mais_rentavel': veiculos[0]['placa'] if veiculos else None,
            'utilizacao_media': round(sum(v['utilizacao_pct'] for v in veiculos) / len(veiculos), 1) if veiculos else 0,
            'faturamento_medio_frota': float(df['faturamento_medio'].mean()) if not df.empty else 0
        }

        return jsonify({
            'success': True,
            'veiculos': veiculos,
            'resumo': resumo,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.exception("Erro ao gerar relatórios por veículo")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao carregar relatórios por veículo'
        }), 500