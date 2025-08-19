from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.cte import CTE

bp = Blueprint('api', __name__)

@bp.route('/ctes', methods=['GET'])
@login_required
def listar_ctes():
    """Lista CTEs com paginação"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    ctes = CTE.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'ctes': [
            {
                'numero_cte': cte.numero_cte,
                'destinatario_nome': cte.destinatario_nome,
                'valor_total': float(cte.valor_total) if cte.valor_total else 0,
                'data_emissao': cte.data_emissao.isoformat() if cte.data_emissao else None,
                'has_baixa': cte.has_baixa
            }
            for cte in ctes.items
        ],
        'pagination': {
            'page': page,
            'pages': ctes.pages,
            'total': ctes.total
        }
    })
