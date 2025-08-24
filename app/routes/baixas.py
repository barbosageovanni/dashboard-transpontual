from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required
from app.models.cte import CTE
from app import db
from datetime import datetime, timedelta
import pandas as pd
import io
from sqlalchemy import func
import logging
from typing import Dict, List, Tuple, Optional
from werkzeug.utils import secure_filename
from io import BytesIO

bp = Blueprint('baixas', __name__, url_prefix='/baixas')

# ============================================================================
# PROCESSADOR DE ARQUIVOS (CSV + EXCEL)
# ============================================================================

class ProcessadorArquivoBaixas:
    """Classe especializada para processar arquivos de baixas (CSV + Excel)"""
    EXTENSOES_PERMITIDAS = {'.csv', '.xlsx', '.xls'}
    TAMANHO_MAX_ARQUIVO = 10 * 1024 * 1024  # 10MB

    # Mapeamento flexível de colunas para baixas
    MAPEAMENTO_COLUNAS_BAIXAS = {
        'numero_cte': [
            'numero_cte', 'num_cte', 'cte', 'numero', 'numero_conhecimento',
            'conhecimento', 'n_cte', 'nro_cte'
        ],
        'data_baixa': [
            'data_baixa', 'baixa', 'dt_baixa', 'data_pagamento', 'pagamento',
            'data_quitacao', 'quitacao', 'd_baixa', 'dt_pagamento'
        ],
        'observacao': [
            'observacao', 'obs', 'observacoes', 'comentario', 'comentarios',
            'nota', 'descricao', 'detalhe'
        ]
    }

    @classmethod
    def processar_arquivo(cls, arquivo) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Processa arquivo de baixas (CSV ou Excel) com detecção automática"""
        try:
            if not arquivo or not arquivo.filename:
                return False, "Nenhum arquivo enviado", None

            filename = secure_filename(arquivo.filename).lower()
            extensao = '.' + filename.split('.')[-1] if '.' in filename else ''

            if extensao not in cls.EXTENSOES_PERMITIDAS:
                return False, f"Formato não suportado. Use: {', '.join(cls.EXTENSOES_PERMITIDAS)}", None

            # tamanho
            arquivo.seek(0, 2)
            tamanho = arquivo.tell()
            arquivo.seek(0)
            if tamanho > cls.TAMANHO_MAX_ARQUIVO:
                return False, f"Arquivo muito grande. Máximo: {cls.TAMANHO_MAX_ARQUIVO // 1024 // 1024}MB", None

            if extensao == '.csv':
                return cls._processar_csv(arquivo)
            elif extensao in ['.xlsx', '.xls']:
                return cls._processar_excel(arquivo, extensao)
            else:
                return False, "Formato de arquivo não reconhecido", None

        except Exception as e:
            logging.error(f"Erro no processamento do arquivo: {str(e)}")
            return False, f"Erro ao processar arquivo: {str(e)}", None

    @classmethod
    def _processar_csv(cls, arquivo) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Processa CSV com detecção automática de encoding e separador"""
        try:
            content = arquivo.read()
            arquivo.seek(0)

            # tentar encodings comuns
            content_str = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content_str = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            if content_str is None:
                return False, "Não foi possível decodificar o arquivo CSV", None

            # tentar separadores comuns
            df = None
            for sep in [';', ',', '\t', '|']:
                try:
                    df_teste = pd.read_csv(io.StringIO(content_str), sep=sep, nrows=5)
                    if len(df_teste.columns) > 1:
                        df = pd.read_csv(io.StringIO(content_str), sep=sep)
                        break
                except Exception:
                    continue
            if df is None or df.empty:
                return False, "Não foi possível interpretar o formato CSV", None

            sucesso, mensagem, df_proc = cls._mapear_validar_colunas(df)
            return sucesso, mensagem, df_proc

        except Exception as e:
            return False, f"Erro ao processar CSV: {str(e)}", None

    @classmethod
    def _processar_excel(cls, arquivo, extensao: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Processa Excel (.xlsx ou .xls)"""
        try:
            engine = 'openpyxl' if extensao == '.xlsx' else 'xlrd'
            df = pd.read_excel(arquivo, engine=engine)
            if df.empty:
                return False, "Planilha Excel está vazia", None

            sucesso, mensagem, df_proc = cls._mapear_validar_colunas(df)
            return sucesso, mensagem, df_proc

        except Exception as e:
            return False, f"Erro ao processar Excel: {str(e)}", None

    @classmethod
    def _mapear_validar_colunas(cls, df: pd.DataFrame) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Mapeia e valida colunas do DataFrame"""
        try:
            df.columns = df.columns.str.strip().str.lower()

            mapeamento = {}
            for campo_modelo, variantes in cls.MAPEAMENTO_COLUNAS_BAIXAS.items():
                for variante in variantes:
                    if variante.lower() in df.columns:
                        mapeamento[variante.lower()] = campo_modelo
                        break

            df_mapeado = df.rename(columns=mapeamento)

            colunas_obrigatorias = ['numero_cte', 'data_baixa']
            faltando = [c for c in colunas_obrigatorias if c not in df_mapeado.columns]
            if faltando:
                colunas_disp = list(df_mapeado.columns)
                sugestoes = []
                for falta in faltando:
                    for disp in colunas_disp:
                        if falta.replace('_', '') in disp.replace('_', ''):
                            sugestoes.append(f"{falta} → {disp}")
                msg = f"Colunas obrigatórias ausentes: {', '.join(faltando)}"
                if sugestoes:
                    msg += f". Sugestões: {'; '.join(sugestoes)}"
                return False, msg, None

            df_limpo = df_mapeado.dropna(subset=['numero_cte'])
            if df_limpo.empty:
                return False, "Nenhuma linha válida encontrada (números CTE em branco)", None

            return True, "Arquivo processado com sucesso", df_limpo

        except Exception as e:
            return False, f"Erro na validação: {str(e)}", None

# ============================================================================
# HELPER LOCAL PARA REGISTRAR BAIXA (evita depender de método no modelo)
# ============================================================================

def _registrar_baixa_model(cte: CTE, data_baixa, observacao: str = "") -> Tuple[bool, str]:
    """
    Atualiza o CTE com a baixa diretamente no modelo.
    Retorna (sucesso, mensagem).
    """
    try:
        if cte.data_baixa:
            return False, "CTE já possui baixa"

        cte.data_baixa = data_baixa

        obs_atual = (cte.observacao or "").strip()
        if observacao:
            cte.observacao = (obs_atual + (" | " if obs_atual else "") + f"BAIXA: {observacao}").strip()

        # updated_at se existir no modelo
        if hasattr(cte, "updated_at"):
            cte.updated_at = datetime.utcnow()

        db.session.commit()
        return True, f"Baixa registrada para CTE {cte.numero_cte}"

    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao registrar baixa: {str(e)}"

# ============================================================================
# PÁGINAS
# ============================================================================

@bp.route('/')
@login_required
def index():
    return render_template('baixas/index.html')

# ============================================================================
# APIs
# ============================================================================

@bp.route('/api/estatisticas')
@login_required
def api_estatisticas():
    try:
        total_baixas = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
        valor_baixado = db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.isnot(None)).scalar() or 0
        baixas_pendentes = CTE.query.filter(CTE.data_baixa.is_(None)).count()
        valor_pendente = db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.is_(None)).scalar() or 0

        return jsonify({
            'success': True,
            'data': {
                'total_baixas': total_baixas,
                'valor_baixado': float(valor_baixado),
                'baixas_pendentes': baixas_pendentes,
                'valor_pendente': float(valor_pendente)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/buscar-cte/<int:numero_cte>')
@login_required
def api_buscar_cte(numero_cte):
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': f'CTE {numero_cte} não encontrado'}), 404
        return jsonify({'success': True, 'cte': cte.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/individual', methods=['POST'])
@login_required
def api_baixa_individual():
    """Registra baixa individual (sem depender de método no modelo)"""
    try:
        dados = request.get_json()
        numero_cte = dados.get('numero_cte')
        data_baixa = dados.get('data_baixa')
        observacao = dados.get('observacao', '')

        if not numero_cte or not data_baixa:
            return jsonify({'success': False, 'message': 'Número do CTE e data da baixa são obrigatórios'}), 400

        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({'success': False, 'message': f'CTE {numero_cte} não encontrado'}), 404

        data_baixa_obj = datetime.strptime(data_baixa, '%Y-%m-%d').date()
        sucesso, mensagem = _registrar_baixa_model(cte, data_baixa_obj, observacao)

        status = 200 if sucesso else 400
        return jsonify({'success': sucesso, 'message': mensagem}), status

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao registrar baixa: {str(e)}'}), 500

# ----------------------------------------------------------------------------

@bp.route('/api/lote', methods=['POST'])
@login_required
def api_baixa_lote():
    """
    Processa baixas em lote (CSV e Excel) com detecção automática
    """
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400

        # processa CSV/XLSX/XLS
        sucesso, mensagem, df = ProcessadorArquivoBaixas.processar_arquivo(arquivo)
        if not sucesso:
            return jsonify({'sucesso': False, 'erro': mensagem}), 400

        resultados = {'processadas': 0, 'sucessos': 0, 'erros': 0, 'detalhes': []}

        for _, row in df.iterrows():
            try:
                numero_cte = row['numero_cte']
                data_baixa = row['data_baixa']
                observacao = row.get('observacao', '')

                # número
                try:
                    numero_cte = int(float(numero_cte)) if pd.notna(numero_cte) else None
                except (ValueError, TypeError):
                    resultados['detalhes'].append({'cte': str(numero_cte), 'sucesso': False, 'mensagem': 'Número CTE inválido'})
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue
                if not numero_cte:
                    resultados['detalhes'].append({'cte': 'N/A', 'sucesso': False, 'mensagem': 'Número CTE em branco'})
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue

                # data
                data_baixa_obj = None
                if pd.notna(data_baixa):
                    try:
                        if isinstance(data_baixa, str):
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
                                try:
                                    data_baixa_obj = datetime.strptime(data_baixa.strip(), fmt).date()
                                    break
                                except ValueError:
                                    continue
                        else:
                            data_baixa_obj = data_baixa.date() if hasattr(data_baixa, 'date') else data_baixa
                    except Exception:
                        pass

                if not data_baixa_obj:
                    resultados['detalhes'].append({'cte': numero_cte, 'sucesso': False, 'mensagem': 'Data de baixa inválida ou em branco'})
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue

                cte = CTE.buscar_por_numero(numero_cte)
                if not cte:
                    resultados['detalhes'].append({'cte': numero_cte, 'sucesso': False, 'mensagem': 'CTE não encontrado'})
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue

                ok, msg = _registrar_baixa_model(cte, data_baixa_obj, observacao)

                resultados['detalhes'].append({'cte': numero_cte, 'sucesso': ok, 'mensagem': msg})
                resultados['sucessos' if ok else 'erros'] += 1
                resultados['processadas'] += 1

            except Exception as e:
                resultados['detalhes'].append({'cte': row.get('numero_cte', 'N/A'), 'sucesso': False, 'mensagem': f'Erro: {str(e)}'})
                resultados['erros'] += 1
                resultados['processadas'] += 1

        logging.info(f"Baixa em lote processada: {resultados['sucessos']} sucessos, {resultados['erros']} erros")

        return jsonify({
            'sucesso': True,
            'resultados': resultados,
            'arquivo_info': {
                'nome': secure_filename(arquivo.filename),
                'formato': 'Excel' if arquivo.filename.lower().endswith(('.xlsx', '.xls')) else 'CSV',
                'linhas_processadas': len(df)
            }
        })

    except Exception as e:
        logging.error(f"Erro crítico na baixa em lote: {str(e)}")
        return jsonify({'sucesso': False, 'erro': f'Erro interno: {str(e)}'}), 500

# ============================================================================
# OUTRAS ROTAS (template, validar, histórico, relatórios, exportar etc.)
# (mantidas como no seu arquivo original)
# ============================================================================

@bp.route('/api/template-baixas')
@login_required
def api_template_baixas():
    try:
        template_data = {
            'numero_cte': [12345, 12346, 12347],
            'data_baixa': ['01/01/2025', '02/01/2025', '03/01/2025'],
            'observacao': ['Baixa via boleto', 'Pagamento PIX', 'Transferência bancária']
        }
        df_template = pd.DataFrame(template_data)
        csv_content = df_template.to_csv(sep=';', index=False, encoding='utf-8-sig')
        from flask import make_response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = 'attachment; filename=template_baixas.csv'
        return response
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@bp.route('/api/validar-arquivo', methods=['POST'])
@login_required
def api_validar_arquivo():
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'})
        sucesso, mensagem, df = ProcessadorArquivoBaixas.processar_arquivo(arquivo)
        if not sucesso:
            return jsonify({'sucesso': False, 'erro': mensagem})
        stats = {
            'linhas_totais': len(df),
            'colunas_encontradas': list(df.columns),
            'ctes_unicos': df['numero_cte'].nunique() if 'numero_cte' in df.columns else 0,
            'preview': df.head(3).to_dict('records')
        }
        return jsonify({'sucesso': True, 'mensagem': mensagem, 'estatisticas': stats})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)})

@bp.route('/conciliacao')
@login_required
def conciliacao():
    try:
        stats = {
            'pendentes': CTE.query.filter(CTE.data_baixa.is_(None)).count(),
            'processadas': CTE.query.filter(CTE.data_baixa.isnot(None)).count(),
            'valor_pendente': float(db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.is_(None)).scalar() or 0),
            'valor_processado': float(db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.isnot(None)).scalar() or 0)
        }
        return render_template('baixas/conciliacao.html', stats=stats)
    except Exception as e:
        flash(f'Erro ao carregar página de conciliação: {str(e)}', 'error')
        return redirect(url_for('baixas.index'))

@bp.route('/historico')
@login_required
def historico():
    try:
        data_limite = datetime.now().date() - timedelta(days=30)
        historico_baixas = db.session.query(
            func.date(CTE.data_baixa).label('data'),
            func.count(CTE.id).label('quantidade'),
            func.sum(CTE.valor_total).label('valor_total')
        ).filter(
            CTE.data_baixa >= data_limite
        ).group_by(
            func.date(CTE.data_baixa)
        ).order_by(
            func.date(CTE.data_baixa).desc()
        ).all()
        return render_template('baixas/historico.html', historico=historico_baixas)
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}', 'error')
        return redirect(url_for('baixas.index'))

@bp.route('/relatorios')
@login_required
def relatorios():
    try:
        stats = {
            'total_ctes': CTE.query.count(),
            'com_baixa': CTE.query.filter(CTE.data_baixa.isnot(None)).count(),
            'sem_baixa': CTE.query.filter(CTE.data_baixa.is_(None)).count(),
            'valor_total': float(db.session.query(func.sum(CTE.valor_total)).scalar() or 0),
            'valor_baixado': float(db.session.query(func.sum(CTE.valor_total)).filter(CTE.data_baixa.isnot(None)).scalar() or 0)
        }
        return render_template('baixas/relatorios.html', stats=stats)
    except Exception as e:
        flash(f'Erro ao carregar relatórios: {str(e)}', 'error')
        return redirect(url_for('baixas.index'))

@bp.route('/importar')
@login_required
def importar():
    try:
        stats = {
            'ultima_importacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'total_importacoes': 0,
            'arquivos_processados': 0
        }
        return render_template('baixas/importar.html', stats=stats)
    except Exception as e:
        flash(f'Erro ao carregar página de importação: {str(e)}', 'error')
        return redirect(url_for('baixas.index'))

@bp.route('/api/exportar')
@login_required
def api_exportar():
    try:
        formato = request.args.get('formato', 'excel')
        query = CTE.query
        if request.args.get('apenas_baixadas') == 'true':
            query = query.filter(CTE.data_baixa.isnot(None))
        ctes = query.order_by(CTE.numero_cte.desc()).all()

        dados = []
        for cte in ctes:
            dados.append({
                'Número CTE': cte.numero_cte,
                'Cliente': cte.destinatario_nome or '',
                'Valor Total': float(cte.valor_total or 0),
                'Data Emissão': cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else '',
                'Data Baixa': cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else '',
                'Status': 'Pago' if cte.data_baixa else 'Pendente',
                'Observação': cte.observacao or ''
            })
        df = pd.DataFrame(dados)

        if formato == 'csv':
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig', sep=';')
            output.seek(0)
            filename = f'baixas_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Baixas', index=False)
            output.seek(0)
            filename = f'baixas_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            return send_file(output,
                             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             as_attachment=True,
                             download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
