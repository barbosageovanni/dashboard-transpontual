# ============================================================================
# MIDDLEWARE DE CORREÇÃO - SISTEMA DE APIs
# Arquivo: app/utils/api_helpers.py (NOVO ARQUIVO)
# ============================================================================

from flask import jsonify, request, current_app
from flask_login import current_user
from functools import wraps
import logging
import traceback
from datetime import datetime

def api_response_handler(f):
    """
    Decorator para garantir que todas as APIs sempre retornem JSON válido
    Corrige o erro: "Unexpected token '<', "<!doctype "... is not valid JSON"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Log da requisição
            current_app.logger.info(f"API Request: {request.method} {request.path}")
            
            # Verificar autenticação para rotas API
            if not current_user.is_authenticated:
                return jsonify({
                    'success': False,
                    'error': 'Autenticação necessária',
                    'error_code': 'AUTH_REQUIRED',
                    'redirect': '/auth/login',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            # Executar função original
            result = f(*args, **kwargs)
            
            # Se não é uma Response do Flask, fazer JSON
            if not hasattr(result, 'status_code'):
                if isinstance(result, dict):
                    result = jsonify(result)
                elif isinstance(result, (list, tuple)):
                    result = jsonify({'data': result, 'success': True})
                else:
                    result = jsonify({'data': result, 'success': True})
            
            # Adicionar headers CORS se necessário
            result.headers['Content-Type'] = 'application/json; charset=utf-8'
            
            return result
            
        except Exception as e:
            # Log do erro completo
            error_id = f"API_ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            current_app.logger.error(f"{error_id}: {str(e)}")
            current_app.logger.error(f"{error_id}: {traceback.format_exc()}")
            
            # SEMPRE retornar JSON em caso de erro
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'INTERNAL_ERROR',
                'error_id': error_id,
                'route': request.endpoint,
                'method': request.method,
                'timestamp': datetime.now().isoformat()
            }), 500
    
    return decorated_function

def validate_json_request(required_fields=None):
    """
    Decorator para validar requisições JSON
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'Requisição deve ser JSON',
                        'error_code': 'INVALID_CONTENT_TYPE'
                    }), 400
                
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'Body JSON vazio ou inválido',
                        'error_code': 'EMPTY_JSON'
                    }), 400
                
                # Validar campos obrigatórios
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            'success': False,
                            'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}',
                            'error_code': 'MISSING_FIELDS',
                            'missing_fields': missing_fields
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================================
# CORREÇÃO PARA app/routes/ctes.py
# ============================================================================

# Adicionar estes imports no início do arquivo ctes.py:
from app.utils.api_helpers import api_response_handler, validate_json_request

# E aplicar os decorators nas rotas problemáticas:

@bp.route('/api/listar')
@login_required
@api_response_handler  # ← ADICIONAR ESTE DECORATOR
def api_listar():
    """API para listar CTEs com paginação e filtros - VERSÃO CORRIGIDA"""
    try:
        # Parâmetros de filtro
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Máximo 100
        filtro_texto = request.args.get('filtro_texto', '').strip()
        filtro_status_baixa = request.args.get('filtro_status_baixa', '')
        filtro_status_processo = request.args.get('filtro_status_processo', '')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Log dos filtros
        current_app.logger.info(f"Listando CTEs - Página: {page}, Filtros: {filtro_texto}")
        
        # Query base
        query = CTE.query
        
        # Aplicar filtros
        if filtro_texto:
            query = query.filter(
                or_(
                    CTE.numero_cte.like(f'%{filtro_texto}%'),
                    CTE.destinatario_nome.ilike(f'%{filtro_texto}%'),
                    CTE.veiculo_placa.ilike(f'%{filtro_texto}%')
                )
            )
        
        if filtro_status_baixa == 'com_baixa':
            query = query.filter(CTE.data_baixa.isnot(None))
        elif filtro_status_baixa == 'sem_baixa':
            query = query.filter(CTE.data_baixa.is_(None))
        
        # Ordenar por data de emissão (mais recente primeiro)
        query = query.order_by(CTE.data_emissao.desc().nullslast(), CTE.numero_cte.desc())
        
        # Paginação
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Converter CTEs para dicionário
        ctes = []
        for cte in pagination.items:
            cte_dict = cte.to_dict()
            # Garantir que valores monetários sejam float
            if cte_dict.get('valor_total'):
                cte_dict['valor_total'] = float(cte_dict['valor_total'])
            ctes.append(cte_dict)
        
        # Resposta padronizada
        response_data = {
            'success': True,
            'ctes': ctes,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'texto': filtro_texto,
                'status_baixa': filtro_status_baixa,
                'status_processo': filtro_status_processo
            },
            'timestamp': datetime.now().isoformat()
        }
        
        current_app.logger.info(f"Retornando {len(ctes)} CTEs de {pagination.total} total")
        return jsonify(response_data)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Parâmetro inválido: {str(e)}',
            'error_code': 'INVALID_PARAMETER'
        }), 400
    
    except Exception as e:
        # Este erro será capturado pelo decorator api_response_handler
        raise e


@bp.route('/api/inserir', methods=['POST'])
@login_required
@api_response_handler
@validate_json_request(['numero_cte', 'valor_total'])
def api_inserir():
    """API para inserir novo CTE - VERSÃO CORRIGIDA"""
    try:
        dados = request.get_json()
        
        # Log da operação
        current_app.logger.info(f"Inserindo CTE: {dados.get('numero_cte')}")
        
        # Validações específicas
        numero_cte = str(dados['numero_cte']).strip()
        if not numero_cte:
            return jsonify({
                'success': False,
                'error': 'Número do CTE não pode ser vazio',
                'error_code': 'EMPTY_CTE_NUMBER'
            }), 400
        
        valor_total = dados.get('valor_total')
        try:
            valor_total = float(valor_total)
            if valor_total <= 0:
                raise ValueError("Valor deve ser positivo")
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Valor total deve ser um número positivo',
                'error_code': 'INVALID_VALUE'
            }), 400
        
        # Verificar se CTE já existe
        cte_existente = CTE.query.filter_by(numero_cte=numero_cte).first()
        if cte_existente:
            return jsonify({
                'success': False,
                'error': f'CTE {numero_cte} já existe no sistema',
                'error_code': 'DUPLICATE_CTE'
            }), 400
        
        # Criar novo CTE
        novo_cte = CTE(
            numero_cte=numero_cte,
            destinatario_nome=dados.get('destinatario_nome', '').strip() or None,
            veiculo_placa=dados.get('veiculo_placa', '').strip() or None,
            valor_total=valor_total,
            data_emissao=datetime.strptime(dados['data_emissao'], '%Y-%m-%d').date() if dados.get('data_emissao') else None,
            observacao=dados.get('observacao', '').strip() or None
        )
        
        # Salvar no banco
        db.session.add(novo_cte)
        db.session.commit()
        
        current_app.logger.info(f"CTE {numero_cte} inserido com sucesso - ID: {novo_cte.id}")
        
        return jsonify({
            'success': True,
            'message': f'CTE {numero_cte} inserido com sucesso',
            'cte': novo_cte.to_dict(),
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Erro será capturado pelo decorator
        raise e


@bp.route('/api/buscar/<int:numero_cte>')
@login_required
@api_response_handler
def api_buscar(numero_cte):
    """API para buscar CTE específico - VERSÃO CORRIGIDA"""
    try:
        current_app.logger.info(f"Buscando CTE: {numero_cte}")
        
        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
        
        if not cte:
            return jsonify({
                'success': False,
                'error': f'CTE {numero_cte} não encontrado',
                'error_code': 'CTE_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'cte': cte.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Número do CTE deve ser um número inteiro',
            'error_code': 'INVALID_CTE_NUMBER'
        }), 400
    
    except Exception as e:
        # Erro será capturado pelo decorator
        raise e

# ============================================================================
# CORREÇÃO PARA app/__init__.py
# ============================================================================

# Adicionar este middleware global na função create_app():

@app.before_request
def handle_api_requests():
    """
    Middleware global para requisições de API
    Garante que APIs sempre retornem JSON
    """
    # Identificar se é uma requisição para API
    is_api_request = (
        request.path.startswith('/api/') or 
        '/api/' in request.path or
        request.path.endswith('/api')
    )
    
    if is_api_request:
        # Para APIs, não usar redirecionamento de login
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Autenticação necessária',
                'error_code': 'AUTH_REQUIRED',
                'redirect': '/auth/login',
                'requested_url': request.url
            }), 401

@app.errorhandler(404)
def not_found_error(error):
    """Tratar 404s em APIs"""
    if (request.path.startswith('/api/') or '/api/' in request.path):
        return jsonify({
            'success': False,
            'error': 'Endpoint não encontrado',
            'error_code': 'NOT_FOUND',
            'requested_url': request.url
        }), 404
    
    # Para outras rotas, comportamento normal
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Tratar 500s em APIs"""
    if (request.path.startswith('/api/') or '/api/' in request.path):
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'error_code': 'INTERNAL_ERROR',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    # Para outras rotas, comportamento normal
    return render_template('errors/500.html'), 500

# ============================================================================
# SCRIPT DE TESTE PARA VALIDAR CORREÇÕES
# ============================================================================

def testar_apis():
    """
    Função para testar se as APIs estão retornando JSON corretamente
    Executar no shell do Flask: flask shell -> testar_apis()
    """
    import requests
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTANDO APIs...")
    print("=" * 50)
    
    # Teste 1: Listar CTEs
    try:
        response = requests.get(f"{base_url}/ctes/api/listar")
        print(f"✅ GET /ctes/api/listar: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print("   ✅ Content-Type correto")
            data = response.json()
            print(f"   ✅ JSON válido: success={data.get('success')}")
        else:
            print(f"   ❌ Content-Type incorreto: {response.headers.get('content-type')}")
            print(f"   ❌ Response (100 chars): {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("=" * 50)
    print("🏁 Teste concluído")

# ============================================================================
# INSTRUÇÕES DE IMPLEMENTAÇÃO
# ============================================================================

"""
PARA IMPLEMENTAR ESTAS CORREÇÕES:

1. Criar arquivo: app/utils/api_helpers.py (código acima)

2. Atualizar app/routes/ctes.py:
   - Adicionar imports dos decorators
   - Aplicar @api_response_handler em todas as rotas /api/
   - Aplicar @validate_json_request nas rotas POST/PUT

3. Atualizar app/__init__.py:
   - Adicionar os errorhandlers globais
   - Adicionar o middleware handle_api_requests

4. Substituir app/static/js/ctes.js pelo arquivo corrigido

5. Testar com:
   - flask shell
   - >>> from app.routes.ctes import testar_apis
   - >>> testar_apis()

6. No navegador, executar no console:
   - debugSistema()

RESULTADO ESPERADO:
- Todas as requisições AJAX retornarão JSON válido
- Não haverá mais erro "Unexpected token '<', "<!doctype"
- Sistema processará CTEs em lote corretamente
- Mensagens de erro claras e consistentes
"""