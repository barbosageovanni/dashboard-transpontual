# app/routes/ctes.py
from __future__ import annotations

import os
import re
import unicodedata
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional

import pandas as pd
from flask import (
    Blueprint, render_template, jsonify, request, redirect,
    url_for, flash, send_file, make_response, current_app
)
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func

from app import db
from app.models.cte import CTE
from app.services.importacao_service import ImportacaoService

bp = Blueprint("ctes", __name__, url_prefix="/ctes")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _extensao(nome: str) -> str:
    return os.path.splitext(nome or "")[1].lower()

def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s

def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    # normaliza nomes
    df = df.rename(columns={c: _slug(str(c)) for c in df.columns})

    mapeamento = {
        "numero_cte": {
            "numero_cte", "n_cte", "cte", "numero", "numerocte", "numero_ct_e"
        },
        "destinatario_nome": {
            "destinatario_nome", "cliente", "razao_social", "nome_destinatario"
        },
        "valor_total": {"valor_total", "valor", "valor_cte", "v_total"},
        "veiculo_placa": {"veiculo_placa", "placa", "placa_veiculo"},
        "data_emissao": {"data_emissao", "emissao", "dt_emissao"},
        "data_inclusao_fatura": {"data_inclusao_fatura", "dt_inc_fatura"},
        "numero_fatura": {"numero_fatura", "fatura", "n_fatura"},
        "primeiro_envio": {"primeiro_envio", "dt_primeiro_envio"},
        "envio_final": {"envio_final", "dt_envio_final"},
        "data_atesto": {"data_atesto", "dt_atesto"},
        "data_baixa": {"data_baixa", "baixa", "dt_baixa"},
        "status_processo": {"status_processo", "status"},
        "observacao": {"observacao", "obs", "observacoes"},
        "data_envio_processo": {"data_envio_processo", "dt_envio_proc"},
        "data_rq_tmc": {"data_rq_tmc", "dt_rq_tmc"},
    }

    for destino, aliases in mapeamento.items():
        for col in list(df.columns):
            if col in aliases and destino not in df.columns:
                df = df.rename(columns={col: destino})

    return df

def _parse_data(valor) -> Optional[datetime.date]:
    if pd.isna(valor) or valor in ("", None):
        return None
    # tenta dd/mm/yyyy; yyyy-mm-dd; fallback pandas
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(valor).strip(), fmt).date()
        except Exception:
            pass
    try:
        return pd.to_datetime(valor).date()
    except Exception:
        return None

def _parse_float(valor) -> Optional[float]:
    if pd.isna(valor) or valor in ("", None):
        return None
    try:
        v = str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(v)
    except Exception:
        try:
            return float(valor)
        except Exception:
            return None

# Campos permitidos para update
CAMPOS_ATUALIZAVEIS = {
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
    "observacao",
    "data_envio_processo",
    "data_rq_tmc",
}

# -----------------------------------------------------------------------------
# Páginas básicas
# -----------------------------------------------------------------------------
@bp.route("/")
@bp.route("/listar")
@login_required
def listar():
    return render_template("ctes/index.html")

# Alias para o menu "Atualizar Lote"
@bp.route("/atualizar-lote")
@login_required
def atualizar_lote():
    # Reaproveita a página de importação em lote (UI genérica)
    stats = ImportacaoService.obter_estatisticas_importacao()
    return render_template("ctes/importar_lote.html", stats=stats)

# -----------------------------------------------------------------------------
# API - Listagem/filtros
# -----------------------------------------------------------------------------
@bp.route("/api/listar")
@login_required
def api_listar():
    try:
        search = request.args.get("search", "").strip()
        status_baixa = request.args.get("status_baixa", "")
        status_processo = request.args.get("status_processo", "")
        data_inicio = request.args.get("data_inicio", "")
        data_fim = request.args.get("data_fim", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        query = CTE.query

        if search:
            try:
                if search.isdigit():
                    query = query.filter(CTE.numero_cte == int(search))
                else:
                    p = f"%{search}%"
                    query = query.filter(
                        or_(
                            CTE.destinatario_nome.ilike(p),
                            CTE.numero_fatura.ilike(p),
                            CTE.veiculo_placa.ilike(p),
                            CTE.observacao.ilike(p),
                        )
                    )
            except Exception as e:
                current_app.logger.warning(f"Filtro search inválido: {e}")

        if status_baixa == "com_baixa":
            query = query.filter(CTE.data_baixa.isnot(None))
        elif status_baixa == "sem_baixa":
            query = query.filter(CTE.data_baixa.is_(None))

        if status_processo == "completo":
            query = query.filter(
                and_(
                    CTE.data_emissao.isnot(None),
                    CTE.primeiro_envio.isnot(None),
                    CTE.data_atesto.isnot(None),
                    CTE.envio_final.isnot(None),
                )
            )
        elif status_processo == "incompleto":
            query = query.filter(
                or_(
                    CTE.data_emissao.is_(None),
                    CTE.primeiro_envio.is_(None),
                    CTE.data_atesto.is_(None),
                    CTE.envio_final.is_(None),
                )
            )

        if data_inicio:
            di = _parse_data(data_inicio)
            if di:
                query = query.filter(CTE.data_emissao >= di)
        if data_fim:
            df_ = _parse_data(data_fim)
            if df_:
                query = query.filter(CTE.data_emissao <= df_)

        pagination = query.order_by(CTE.numero_cte.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        ctes = []
        for cte in pagination.items:
            try:
                ctes.append(cte.to_dict())
            except Exception as e:
                current_app.logger.warning(f"to_dict falhou para {cte.numero_cte}: {e}")
                ctes.append(
                    {
                        "numero_cte": cte.numero_cte,
                        "destinatario_nome": cte.destinatario_nome or "",
                        "valor_total": float(cte.valor_total or 0),
                        "data_emissao": cte.data_emissao.isoformat()
                        if cte.data_emissao
                        else None,
                        "has_baixa": cte.data_baixa is not None,
                        "processo_completo": False,
                        "status_processo": "Erro",
                    }
                )

        return jsonify(
            {
                "success": True,
                "ctes": ctes,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# CRUD básico (compatibilidade frontend)
# -----------------------------------------------------------------------------
@bp.route("/api/inserir", methods=["POST"])
@login_required
def api_inserir():
    try:
        dados = request.get_json() or {}
        if not dados.get("numero_cte"):
            return jsonify({"success": False, "message": "Número do CTE é obrigatório"}), 400
        if not dados.get("valor_total"):
            return jsonify({"success": False, "message": "Valor total é obrigatório"}), 400

        if CTE.buscar_por_numero(int(dados["numero_cte"])):
            return jsonify({"success": False, "message": "CTE já existe"}), 400

        ok, res = CTE.criar_cte(dados)
        if ok:
            return jsonify({"success": True, "message": "CTE inserido", "cte": res.to_dict()})
        return jsonify({"success": False, "message": res}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route("/api/buscar/<int:numero_cte>")
@login_required
def api_buscar(numero_cte: int):
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({"success": False, "message": "CTE não encontrado"}), 404
        return jsonify({"success": True, "cte": cte.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route("/api/atualizar/<int:numero_cte>", methods=["PUT"])
@login_required
def api_atualizar(numero_cte: int):
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({"success": False, "message": "CTE não encontrado"}), 404
        dados = request.get_json() or {}
        ok, msg = cte.atualizar(dados)
        if ok:
            return jsonify({"success": True, "message": msg, "cte": cte.to_dict()})
        return jsonify({"success": False, "message": msg}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route("/api/excluir/<int:numero_cte>", methods=["DELETE"])
@login_required
def api_excluir(numero_cte: int):
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({"success": False, "message": "CTE não encontrado"}), 404
        db.session.delete(cte)
        db.session.commit()
        return jsonify({"success": True, "message": f"CTE {numero_cte} excluído"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------------------------------------------------------
# Templates de atualização (CSV e XLSX) com TODOS os campos
# -----------------------------------------------------------------------------
@bp.route("/template-atualizacao")
@login_required
def template_atualizacao_csv():
    headers = [
        "numero_cte", "destinatario_nome", "valor_total", "veiculo_placa",
        "data_emissao", "data_inclusao_fatura", "numero_fatura",
        "primeiro_envio", "envio_final", "data_atesto", "data_baixa",
        "status_processo", "observacao", "data_envio_processo", "data_rq_tmc"
    ]
    amostras = [
        ["1001","Cliente A","5500.00","ABC1234","01/01/2025","02/01/2025","NF001",
         "03/01/2025","04/01/2025","05/01/2025","15/01/2025","Completo","Exemplo","03/01/2025","06/01/2025"],
        ["1002","Cliente B","3200.50","XYZ5678","02/01/2025","","NF002",
         "","","","","Pendente","Pendente de baixa","",""],
    ]
    linhas = [",".join(headers)]
    for r in amostras:
        linhas.append(",".join(str(x) for x in r))
    resp = make_response("\n".join(linhas) + "\n")
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = 'attachment; filename="template_atualizacao_ctes.csv"'
    return resp

@bp.route("/template-atualizacao.xlsx")
@login_required
def template_atualizacao_xlsx():
    try:
        from openpyxl import Workbook
    except Exception as e:
        return make_response(f"openpyxl não disponível ({e}). Use /ctes/template-atualizacao.", 500)
    headers = [
        "numero_cte", "destinatario_nome", "valor_total", "veiculo_placa",
        "data_emissao", "data_inclusao_fatura", "numero_fatura",
        "primeiro_envio", "envio_final", "data_atesto", "data_baixa",
        "status_processo", "observacao", "data_envio_processo", "data_rq_tmc"
    ]
    amostras = [
        [1001,"Cliente A",5500.00,"ABC1234","01/01/2025","02/01/2025","NF001",
         "03/01/2025","04/01/2025","05/01/2025","15/01/2025","Completo","Exemplo","03/01/2025","06/01/2025"],
        [1002,"Cliente B",3200.50,"XYZ5678","02/01/2025","","NF002","","","","","","Pendente de baixa","",""],
    ]
    wb = Workbook(); ws = wb.active; ws.title = "Atualização CTEs"
    ws.append(headers)
    for r in amostras: ws.append(r)
    buf = BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(
        buf, as_attachment=True,
        download_name="template_atualizacao_ctes.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# -----------------------------------------------------------------------------
# Download de dados (com TODAS as colunas)
# -----------------------------------------------------------------------------
@bp.route("/api/download/excel")
@login_required
def download_excel():
    try:
        query = CTE.query.order_by(CTE.numero_cte.desc()).all()
        dados = []
        for cte in query:
            dados.append({
                "Número CTE": cte.numero_cte,
                "Cliente": cte.destinatario_nome or "",
                "Valor Total": float(cte.valor_total or 0),
                "Data Emissão": cte.data_emissao.strftime("%d/%m/%Y") if cte.data_emissao else "",
                "Placa Veículo": cte.veiculo_placa or "",
                "Data Inclusão Fatura": getattr(cte, "data_inclusao_fatura", None).strftime("%d/%m/%Y") if getattr(cte, "data_inclusao_fatura", None) else "",
                "Número Fatura": cte.numero_fatura or "",
                "Primeiro Envio": cte.primeiro_envio.strftime("%d/%m/%Y") if cte.primeiro_envio else "",
                "Envio Final": cte.envio_final.strftime("%d/%m/%Y") if cte.envio_final else "",
                "Data Atesto": cte.data_atesto.strftime("%d/%m/%Y") if cte.data_atesto else "",
                "Data Baixa": cte.data_baixa.strftime("%d/%m/%Y") if cte.data_baixa else "",
                "Status Baixa": "Pago" if cte.data_baixa else "Pendente",
                "Status Processo": getattr(cte, "status_processo", ""),
                "Observação": cte.observacao or "",
            })
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="CTEs", index=False)
        output.seek(0)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"ctes_export_{ts}.xlsx",
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/api/download/csv")
@login_required
def download_csv():
    try:
        ctes = CTE.query.order_by(CTE.numero_cte.desc()).all()
        dados = []
        for cte in ctes:
            dados.append({
                "numero_cte": cte.numero_cte,
                "destinatario_nome": cte.destinatario_nome or "",
                "valor_total": float(cte.valor_total or 0),
                "data_emissao": cte.data_emissao.strftime("%d/%m/%Y") if cte.data_emissao else "",
                "veiculo_placa": cte.veiculo_placa or "",
                "data_inclusao_fatura": getattr(cte, "data_inclusao_fatura", None).strftime("%d/%m/%Y") if getattr(cte, "data_inclusao_fatura", None) else "",
                "numero_fatura": cte.numero_fatura or "",
                "primeiro_envio": cte.primeiro_envio.strftime("%d/%m/%Y") if cte.primeiro_envio else "",
                "envio_final": cte.envio_final.strftime("%d/%m/%Y") if cte.envio_final else "",
                "data_atesto": cte.data_atesto.strftime("%d/%m/%Y") if cte.data_atesto else "",
                "data_baixa": cte.data_baixa.strftime("%d/%m/%Y") if cte.data_baixa else "",
                "status_processo": getattr(cte, "status_processo", ""),
                "observacao": cte.observacao or "",
            })
        df = pd.DataFrame(dados)
        buf = BytesIO(); df.to_csv(buf, index=False, encoding="utf-8-sig"); buf.seek(0)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(buf, mimetype="text/csv", as_attachment=True, download_name=f"ctes_export_{ts}.csv")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/api/download/pdf")
@login_required
def download_pdf():
    return redirect(url_for("ctes.download_excel"))

# -----------------------------------------------------------------------------
# Auditoria e correção rápida de status
# -----------------------------------------------------------------------------
@bp.route("/api/auditoria")
@login_required
def api_auditoria():
    try:
        problemas, ctes = [], CTE.query.all()
        for cte in ctes:
            datas = [
                ("data_emissao", cte.data_emissao),
                ("primeiro_envio", cte.primeiro_envio),
                ("data_atesto", cte.data_atesto),
                ("envio_final", cte.envio_final),
                ("data_baixa", cte.data_baixa),
            ]
            vazias = [n for n, d in datas if d is None]
            if cte.processo_completo and len(vazias) > 1:
                prob = f"Marcado completo mas faltam: {', '.join(vazias)}"
            elif not cte.processo_completo and len(vazias) <= 1:
                prob = f"Pode estar completo - falta: {', '.join(vazias) if vazias else 'nenhuma'}"
            else:
                prob = None
            if prob:
                problemas.append({
                    "numero_cte": cte.numero_cte,
                    "cliente": cte.destinatario_nome,
                    "status_atual": cte.status_processo,
                    "processo_completo": cte.processo_completo,
                    "problema": prob,
                })
        return jsonify({"success": True, "problemas_encontrados": len(problemas), "problemas": problemas[:50]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/api/corrigir-status")
@login_required
def api_corrigir_status():
    try:
        ctes = CTE.query.all()
        for cte in ctes:
            cte.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True, "message": f"Status recalculado para {len(ctes)} CTEs"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# Importação (usando ImportacaoService existente)
# -----------------------------------------------------------------------------
@bp.route("/importar", methods=["GET", "POST"])
@login_required
def importar_ctes():
    if request.method == "GET":
        stats = ImportacaoService.obter_estatisticas_importacao()
        return render_template("ctes/importar.html", stats=stats)
    try:
        if "arquivo_csv" not in request.files:
            flash("Nenhum arquivo selecionado", "error")
            return redirect(url_for("ctes.importar_ctes"))
        arquivo = request.files["arquivo_csv"]
        if not arquivo.filename:
            flash("Nenhum arquivo selecionado", "error")
            return redirect(url_for("ctes.importar_ctes"))
        if not arquivo.filename.lower().endswith(".csv"):
            flash("Apenas CSV é permitido", "error")
            return redirect(url_for("ctes.importar_ctes"))
        resultado = ImportacaoService.processar_importacao_completa(arquivo)
        if resultado.get("sucesso"):
            stats = resultado["estatisticas"]; ins = stats["insercao"]
            flash(
                f"Importação concluída! Processados: {ins['processados']} | Inseridos: {ins['sucessos']} | "
                f"Erros: {ins['erros']} | Já existentes: {stats['processamento']['ctes_existentes']}",
                "success",
            )
            return render_template("ctes/importar_resultado.html", resultado=resultado, detalhes=resultado["detalhes"])
        flash(f"Erro na importação: {resultado.get('erro')}", "error")
        return redirect(url_for("ctes.importar_ctes"))
    except Exception as e:
        current_app.logger.exception("Erro na importação de CTEs")
        flash(f"Erro interno: {str(e)}", "error")
        return redirect(url_for("ctes.importar_ctes"))

@bp.route("/template-csv")
@login_required
def download_template():
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        resp = make_response(csv_content)
        resp.headers["Content-Type"] = "text/csv"
        resp.headers["Content-Disposition"] = "attachment; filename=template_ctes.csv"
        return resp
    except Exception as e:
        current_app.logger.exception("Erro ao gerar template CSV")
        flash("Erro ao gerar template CSV", "error")
        return redirect(url_for("ctes.importar_ctes"))

@bp.route("/historico-importacoes")
@login_required
def historico_importacoes():
    try:
        data_limite = datetime.now().date() - timedelta(days=30)
        importacoes = (
            db.session.query(
                func.date(CTE.created_at).label("data"),
                func.count(CTE.id).label("quantidade"),
                func.sum(CTE.valor_total).label("valor_total"),
                CTE.origem_dados,
            )
            .filter(CTE.created_at >= data_limite, CTE.origem_dados.like("%CSV%"))
            .group_by(func.date(CTE.created_at), CTE.origem_dados)
            .order_by(func.date(CTE.created_at).desc())
            .all()
        )
        return render_template("ctes/historico_importacoes.html", importacoes=importacoes)
    except Exception as e:
        current_app.logger.exception("Erro ao buscar histórico")
        flash("Erro ao carregar histórico de importações", "error")
        return redirect(url_for("ctes.listar"))

# -----------------------------------------------------------------------------
# Validação de arquivo (CSV/Excel) — aceita GET e POST + alias /api/validar-csv
# -----------------------------------------------------------------------------
@bp.route("/validar-csv", methods=["GET", "POST"])
@login_required
def validar_csv():
    if request.method == "GET":
        # health-check que o front faz antes do upload
        return jsonify({"ok": True})

    try:
        arquivo = request.files.get("arquivo_csv") or request.files.get("arquivo")
        if not arquivo or not arquivo.filename:
            return jsonify({"sucesso": False, "erro": "Nenhum arquivo enviado"}), 400

        ext = _extensao(arquivo.filename)
        arquivo.stream.seek(0)

        if ext == ".csv":
            try:
                arquivo.stream.seek(0)
                df = pd.read_csv(arquivo, sep=None, engine="python")  # auto-detect
            except Exception as e:
                return jsonify({"sucesso": False, "erro": f"Erro ao ler CSV: {e}"}), 400
        elif ext in (".xlsx", ".xls"):
            try:
                df = pd.read_excel(arquivo)
            except Exception as e:
                return jsonify({"sucesso": False, "erro": f"Erro ao ler Excel: {e}"}), 400
        else:
            return jsonify({"sucesso": False, "erro": "Apenas CSV ou Excel (.xlsx/.xls) são permitidos"}), 400

        df = _normalizar_colunas(df)
        if df is None or df.empty:
            return jsonify({"sucesso": False, "erro": "Nenhum registro válido no arquivo"}), 400

        # Reaproveita pipeline existente
        df_limpo, stats_proc = ImportacaoService.processar_dados_csv(df)
        if df_limpo.empty:
            return jsonify({"sucesso": False, "erro": "Nenhum registro válido no arquivo"}), 400

        df_novos, df_existentes, stats_novos = ImportacaoService.identificar_ctes_novos(df_limpo)
        duplicatas = ImportacaoService.verificar_duplicatas_internas(df_limpo)
        preview = df_novos.head(5).to_dict("records") if not df_novos.empty else []

        return jsonify({
            "sucesso": True,
            "estatisticas": {
                "arquivo": {
                    "nome": arquivo.filename,
                    "linhas_totais": int(len(df)),
                    "linhas_validas": int(stats_proc.get("linhas_validas", 0)),
                    "linhas_descartadas": int(stats_proc.get("linhas_descartadas", 0)),
                },
                "analise": stats_novos,
                "duplicatas": duplicatas,
                "preview": preview,
            }
        })
    except Exception as e:
        current_app.logger.exception("Erro na validação")
        return jsonify({"sucesso": False, "erro": str(e)}), 500

@bp.route("/api/validar-csv", methods=["GET", "POST"])
@login_required
def api_validar_csv():
    return validar_csv()

# -----------------------------------------------------------------------------
# Atualização em lote (ALTERAR) — aceita CSV/Excel com todos os campos
# -----------------------------------------------------------------------------
def _processar_arquivo_atualizacao(arquivo_storage, modo: str = "alterar") -> Dict[str, Any]:
    """
    modo:
      - 'alterar'  : atualiza apenas CTEs existentes (default)
      - 'inserir'  : cria se não existir, senão atualiza
    """
    ext = _extensao(arquivo_storage.filename)
    arquivo_storage.stream.seek(0)
    if ext == ".csv":
        df = pd.read_csv(arquivo_storage, sep=None, engine="python")
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(arquivo_storage)
    else:
        raise ValueError("Extensão não suportada. Envie CSV ou Excel.")

    df = _normalizar_colunas(df)
    if df.empty:
        return {"sucesso": False, "erro": "Arquivo sem registros."}

    processados = 0
    alterados = 0
    inseridos = 0
    erros = 0
    detalhes: List[Dict[str, Any]] = []

    BATCH = 300
    linhas = df.to_dict("records")

    for i, row in enumerate(linhas, start=1):
        try:
            numero_cte = row.get("numero_cte")
            if pd.isna(numero_cte) or numero_cte in (None, ""):
                raise ValueError("numero_cte vazio")
            try:
                numero_cte = int(float(str(numero_cte).strip()))
            except Exception:
                raise ValueError("numero_cte inválido")

            cte = CTE.buscar_por_numero(numero_cte)

            if not cte and modo == "alterar":
                detalhes.append({"linha": i, "cte": numero_cte, "sucesso": False, "mensagem": "CTE não existe"})
                erros += 1
                continue

            dados_update: Dict[str, Any] = {}
            for campo in CAMPOS_ATUALIZAVEIS:
                if campo not in row:
                    continue
                val = row.get(campo)
                if campo.startswith("data_"):
                    val = _parse_data(val)
                elif campo == "valor_total":
                    v = _parse_float(val)
                    if v is not None:
                        val = v
                    else:
                        val = None
                else:
                    if pd.isna(val):
                        val = None
                    else:
                        val = str(val).strip() if isinstance(val, str) else val
                dados_update[campo] = val

            if cte:
                ok, msg = cte.atualizar(dados_update)
                if ok:
                    alterados += 1
                    detalhes.append({"linha": i, "cte": numero_cte, "sucesso": True, "mensagem": "Atualizado"})
                else:
                    erros += 1
                    detalhes.append({"linha": i, "cte": numero_cte, "sucesso": False, "mensagem": msg})
            else:
                # modo inserir
                payload = {"numero_cte": numero_cte, **{k: v for k, v in dados_update.items() if v is not None}}
                ok, res = CTE.criar_cte(payload)
                if ok:
                    inseridos += 1
                    detalhes.append({"linha": i, "cte": numero_cte, "sucesso": True, "mensagem": "Inserido"})
                else:
                    erros += 1
                    detalhes.append({"linha": i, "cte": numero_cte, "sucesso": False, "mensagem": str(res)})

            processados += 1
            if processados % BATCH == 0:
                db.session.commit()

        except Exception as e:
            current_app.logger.warning(f"Erro linha {i}: {e}")
            erros += 1
            detalhes.append({"linha": i, "cte": row.get("numero_cte"), "sucesso": False, "mensagem": str(e)})

    db.session.commit()

    return {
        "sucesso": True,
        "estatisticas": {
            "processados": processados,
            "alterados": alterados,
            "inseridos": inseridos,
            "erros": erros,
        },
        "detalhes": detalhes[:200],  # limita para resposta
    }

@bp.route("/api/atualizar-lote", methods=["POST"])
@login_required
def api_atualizar_lote():
    """
    Atualiza CTEs a partir de CSV/Excel.
    Aceita campo 'arquivo' (ou 'arquivo_csv') e param opcional ?modo=alterar|inserir
    """
    try:
        arquivo = request.files.get("arquivo") or request.files.get("arquivo_csv")
        if not arquivo or not arquivo.filename:
            return jsonify({"sucesso": False, "erro": "Nenhum arquivo enviado"}), 400

        modo = request.args.get("modo", "alterar").lower().strip()
        if modo not in {"alterar", "inserir"}:
            modo = "alterar"

        resultado = _processar_arquivo_atualizacao(arquivo, modo=modo)
        http = 200 if resultado.get("sucesso") else 400
        return jsonify(resultado), http
    except Exception as e:
        current_app.logger.exception("Erro na atualização em lote")
        return jsonify({"sucesso": False, "erro": str(e)}), 500

# -----------------------------------------------------------------------------
# Importação em lote via serviço existente (mantida)
# -----------------------------------------------------------------------------
@bp.route("/api/importar/lote", methods=["POST"])
@login_required
def api_importar_lote():
    try:
        arquivo = request.files.get("arquivo")
        if not arquivo:
            return jsonify({"sucesso": False, "erro": "Nenhum arquivo enviado"}), 400
        if not (_extensao(arquivo.filename) in (".csv", ".xlsx", ".xls")):
            return jsonify({"sucesso": False, "erro": "Apenas CSV/XLSX são permitidos"}), 400

        # Se for Excel, você pode opcionalmente converter para df e chamar os métodos do serviço
        # Para manter compatibilidade, delegamos direto:
        resultado = ImportacaoService.processar_importacao_completa(arquivo)
        if resultado.get("sucesso"):
            ins = resultado["estatisticas"]["insercao"]
            fmt = {
                "processados": ins["processados"],
                "sucessos": ins["sucessos"],
                "erros": ins["erros"],
                "ctes_existentes": resultado["estatisticas"]["analise"]["ctes_existentes"],
                "detalhes": ins.get("detalhes", [])[:50],
                "tempo_processamento": resultado.get("tempo_processamento", 0),
            }
            return jsonify({"sucesso": True, "resultados": fmt, "estatisticas_completas": resultado["estatisticas"]})
        return jsonify({"sucesso": False, "erro": resultado.get("erro")}), 500
    except Exception as e:
        current_app.logger.exception("Erro na importação em lote")
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500

@bp.route("/api/template-csv")
@login_required
def api_template_csv():
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        resp = make_response(csv_content)
        resp.headers["Content-Type"] = "text/csv; charset=utf-8"
        resp.headers["Content-Disposition"] = "attachment; filename=template_importacao_ctes.csv"
        return resp
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@bp.route("/api/estatisticas-importacao")
@login_required
def api_estatisticas_importacao():
    try:
        stats = ImportacaoService.obter_estatisticas_importacao()
        return jsonify({"sucesso": True, "estatisticas": stats})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)})

# -----------------------------------------------------------------------------
# Página de importação em lote (UI)
# -----------------------------------------------------------------------------
@bp.route("/importar-lote")
@login_required
def importar_lote():
    stats = ImportacaoService.obter_estatisticas_importacao()
    return render_template("ctes/importar_lote.html", stats=stats)

@bp.route('/api/salvar-cte-seguro', methods=['POST'])
@login_required
def api_salvar_cte_seguro():
    """
    ✅ ROTA CORRIGIDA: Salvar CTE sem erro 'cannot unpack'
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Nenhum dado fornecido'
            }), 400
        
        # Validações básicas
        if not dados.get('numero_cte'):
            return jsonify({
                'success': False,
                'message': 'Número do CTE é obrigatório'
            }), 400
        
        # Verificar se CTE já existe
        cte_existente = CTE.query.filter_by(numero_cte=dados['numero_cte']).first()
        
        if cte_existente:
            # Atualizar CTE existente
            sucesso, mensagem = cte_existente.atualizar_seguro(dados)
        else:
            # Criar novo CTE
            novo_cte = CTE(
                numero_cte=dados['numero_cte'],
                destinatario_nome=dados.get('destinatario_nome', ''),
                veiculo_placa=dados.get('veiculo_placa'),
                valor_total=dados.get('valor_total', 0),
                observacao=dados.get('observacao')
            )
            
            # Processar datas se fornecidas
            campos_data = ['data_emissao', 'data_envio_processo', 'primeiro_envio', 'data_rq_tmc', 'data_atesto', 'envio_final']
            for campo in campos_data:
                if dados.get(campo):
                    try:
                        from datetime import datetime
                        valor_data = datetime.strptime(dados[campo], '%Y-%m-%d').date()
                        setattr(novo_cte, campo, valor_data)
                    except:
                        pass  # Ignorar datas inválidas
            
            sucesso, mensagem = novo_cte.salvar_seguro()
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem
            })
        else:
            return jsonify({
                'success': False,
                'message': mensagem
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Erro na API salvar CTE: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@bp.route('/api/atualizar-cte-seguro/<int:numero_cte>', methods=['PUT'])
@login_required
def api_atualizar_cte_seguro(numero_cte):
    """
    ✅ ROTA CORRIGIDA: Atualizar CTE sem erro 'cannot unpack'
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Nenhum dado fornecido'
            }), 400
        
        # Buscar CTE
        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
        if not cte:
            return jsonify({
                'success': False,
                'message': 'CTE não encontrado'
            }), 404
        
        # ✅ USAR MÉTODO SEGURO QUE SEMPRE RETORNA TUPLA
        sucesso, mensagem = cte.atualizar_seguro(dados)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem,
                'cte': cte.to_dict() if hasattr(cte, 'to_dict') else {'numero_cte': cte.numero_cte}
            })
        else:
            return jsonify({
                'success': False,
                'message': mensagem
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Erro na API atualizar CTE: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
