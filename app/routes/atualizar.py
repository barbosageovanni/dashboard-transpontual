#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Rota de Atualização - Fix para 'cannot unpack'
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services.atualizacao_service import AtualizacaoService
import pandas as pd
import io

bp = Blueprint('atualizar', __name__, url_prefix='/atualizar')

@bp.route('/lote', methods=['POST'])
@login_required
def atualizar_lote():
    """Fix para erro cannot unpack"""
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Sem arquivo'}), 400
        
        # Processar CSV simples
        content = arquivo.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content))
        dados = df.to_dict('records')
        
        # Usar serviço que sempre retorna dict
        resultado = AtualizacaoService.atualizar_cte_lote(dados)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
