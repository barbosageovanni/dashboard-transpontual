# app/services/importacao_service.py
import io
import time
from typing import Tuple, Optional, Dict, Any, List

import pandas as pd
from pandas import DataFrame
from werkzeug.datastructures import FileStorage

from app import db  # noqa: F401
from app.models.cte import CTE


class ImportacaoService:
    """
    Serviço de importação/validação para CTEs.

    -> Aceita CSV (delimitador ; ou ,) e Excel (.xlsx/.xls)
    -> Funções usadas pelas rotas em app/routes/ctes.py:
       - validar_csv_upload(arquivo) -> (bool, msg, df|None)
       - processar_dados_csv(df) -> (df_limpo, estatisticas)
       - identificar_ctes_novos(df_limpo) -> (df_novos, df_existentes, stats)
       - verificar_duplicatas_internas(df_limpo) -> dict
       - processar_importacao_completa(arquivo) -> dict
       - gerar_template_csv() -> str
    """

    COLUNAS_PADRAO = [
        "numero_cte",
        "destinatario_nome",
        "valor_total",
        "veiculo_placa",
        "data_emissao",
        "data_inclusao_fatura",
        "numero_fatura",
        "primeiro_envio",
        "data_rq_tmc",
        "data_atesto",
        "envio_final",
        "data_envio_processo",
        "data_baixa",
        "observacao",
    ]

    @staticmethod
    def _ler_arquivo_para_dataframe(arquivo: FileStorage) -> Tuple[bool, str, Optional[DataFrame]]:
        """Lê CSV ou Excel e devolve um DataFrame."""
        nome = (arquivo.filename or "").lower()
        try:
            dados = arquivo.read()
            arquivo.stream.seek(0)

            if nome.endswith(".xlsx") or nome.endswith(".xls"):
                df = pd.read_excel(io.BytesIO(dados))
                return True, "ok", df

            if nome.endswith(".csv"):
                buf = io.StringIO(dados.decode("utf-8", errors="ignore"))
                try:
                    df = pd.read_csv(buf, sep=";")
                except Exception:
                    buf.seek(0)
                    df = pd.read_csv(buf, sep=",")
                return True, "ok", df

            return False, "Extensão não suportada. Envie .csv ou .xlsx", None
        except Exception as e:
            return False, f"Falha ao ler arquivo: {e}", None

    @staticmethod
    def validar_csv_upload(arquivo: FileStorage) -> Tuple[bool, str, Optional[DataFrame]]:
        """
        Valida o upload e retorna (valido, mensagem, df).
        NUNCA retorna apenas bool — evita “cannot unpack non-iterable bool object”.
        """
        if not arquivo or not arquivo.filename:
            return False, "Nenhum arquivo enviado", None

        ok, msg, df = ImportacaoService._ler_arquivo_para_dataframe(arquivo)
        if not ok:
            return False, msg, None

        if df.empty:
            return False, "Arquivo sem registros", None

        # Normaliza as colunas
        df.columns = [str(c).strip().lower() for c in df.columns]

        colunas_encontradas = set(df.columns)
        colunas_obrig = {"numero_cte", "destinatario_nome", "valor_total"}
        faltando = colunas_obrig - colunas_encontradas
        if faltando:
            return (
                False,
                f"Colunas obrigatórias ausentes: {', '.join(sorted(faltando))}",
                None,
            )

        return True, "ok", df

    # --------- Limpeza e estatísticas ---------

    @staticmethod
    def _parse_data(valor) -> Optional[pd.Timestamp]:
        if pd.isna(valor) or valor in ("", None):
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return pd.to_datetime(str(valor), format=fmt, errors="raise")
            except Exception:
                pass
        try:
            return pd.to_datetime(valor, errors="coerce")
        except Exception:
            return None

    @staticmethod
    def processar_dados_csv(df: DataFrame) -> Tuple[DataFrame, Dict[str, Any]]:
        """Limpa e normaliza o DataFrame; retorna (df_limpo, estatísticas)."""
        original = len(df)

        # garante colunas padrão
        for col in ImportacaoService.COLUNAS_PADRAO:
            if col not in df.columns:
                df[col] = None

        def limpa_texto(v):
            if pd.isna(v) or v is None:
                return None
            s = str(v).strip()
            return s if s else None

        def to_float(v):
            if pd.isna(v) or v is None or v == "":
                return None
            try:
                if isinstance(v, str):
                    v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
                return float(v)
            except Exception:
                return None

        def to_int(v):
            if pd.isna(v) or v is None or v == "":
                return None
            try:
                return int(float(v))
            except Exception:
                return None

        df_norm = pd.DataFrame({
            "numero_cte": df["numero_cte"].map(to_int),
            "destinatario_nome": df["destinatario_nome"].map(limpa_texto),
            "valor_total": df["valor_total"].map(to_float),
            "veiculo_placa": df["veiculo_placa"].map(limpa_texto)
                if "veiculo_placa" in df.columns else None,
            "data_emissao": df["data_emissao"].map(ImportacaoService._parse_data)
                if "data_emissao" in df.columns else None,
            "data_inclusao_fatura": df["data_inclusao_fatura"].map(ImportacaoService._parse_data)
                if "data_inclusao_fatura" in df.columns else None,
            "numero_fatura": df["numero_fatura"].map(limpa_texto)
                if "numero_fatura" in df.columns else None,
            "primeiro_envio": df["primeiro_envio"].map(ImportacaoService._parse_data)
                if "primeiro_envio" in df.columns else None,
            "data_rq_tmc": df["data_rq_tmc"].map(ImportacaoService._parse_data)
                if "data_rq_tmc" in df.columns else None,
            "data_atesto": df["data_atesto"].map(ImportacaoService._parse_data)
                if "data_atesto" in df.columns else None,
            "envio_final": df["envio_final"].map(ImportacaoService._parse_data)
                if "envio_final" in df.columns else None,
            "data_envio_processo": df["data_envio_processo"].map(ImportacaoService._parse_data)
                if "data_envio_processo" in df.columns else None,
            "data_baixa": df["data_baixa"].map(ImportacaoService._parse_data)
                if "data_baixa" in df.columns else None,
            "observacao": df["observacao"].map(limpa_texto)
                if "observacao" in df.columns else None,
        })

        mask_validos = (
            df_norm["numero_cte"].notna()
            & df_norm["destinatario_nome"].notna()
            & df_norm["valor_total"].notna()
        )
        df_limpo = df_norm.loc[mask_validos].copy()

        estat = {
            "linhas_totais": original,
            "linhas_validas": int(mask_validos.sum()),
            "linhas_descartadas": int((~mask_validos).sum()),
        }
        return df_limpo, estat

    @staticmethod
    def identificar_ctes_novos(df_limpo: DataFrame) -> Tuple[DataFrame, DataFrame, Dict[str, Any]]:
        """Separa CTEs novos dos já existentes no banco."""
        numeros = [int(n) for n in df_limpo["numero_cte"].dropna().astype(int).tolist()]
        existentes = CTE.obter_ctes_existentes_bulk(numeros)
        is_existente = df_limpo["numero_cte"].isin(list(existentes))
        df_existentes = df_limpo.loc[is_existente].copy()
        df_novos = df_limpo.loc[~is_existente].copy()
        stats = {
            "total": len(df_limpo),
            "ctes_existentes": int(is_existente.sum()),
            "ctes_novos": int((~is_existente).sum()),
        }
        return df_novos, df_existentes, stats

    @staticmethod
    def verificar_duplicatas_internas(df_limpo: DataFrame) -> Dict[str, Any]:
        dup = (
            df_limpo.groupby("numero_cte")
            .size()
            .reset_index(name="quantidade")
            .query("quantidade > 1")
            .to_dict("records")
        )
        return {"duplicatas_internas": dup, "total_duplicatas": len(dup)}

    # -------- Importação completa --------

    @staticmethod
    def _linha_para_dict(row: pd.Series) -> Dict[str, Any]:
        def to_date(d):
            if pd.isna(d) or d is None:
                return None
            return d.date()

        return {
            "numero_cte": int(row.get("numero_cte")),
            "destinatario_nome": row.get("destinatario_nome"),
            "valor_total": float(row.get("valor_total")),
            "veiculo_placa": row.get("veiculo_placa"),
            "data_emissao": to_date(row.get("data_emissao")),
            "data_inclusao_fatura": to_date(row.get("data_inclusao_fatura")),
            "numero_fatura": row.get("numero_fatura"),
            "primeiro_envio": to_date(row.get("primeiro_envio")),
            "data_rq_tmc": to_date(row.get("data_rq_tmc")),
            "data_atesto": to_date(row.get("data_atesto")),
            "envio_final": to_date(row.get("envio_final")),
            "data_envio_processo": to_date(row.get("data_envio_processo")),
            "data_baixa": to_date(row.get("data_baixa")),
            "observacao": row.get("observacao"),
            "origem_dados": "Importação CSV/XLSX",
        }

    @staticmethod
    def processar_importacao_completa(arquivo: FileStorage) -> Dict[str, Any]:
        """
        Fluxo completo: valida, limpa, identifica novos e insere em lote.
        Retorna um dicionário com 'sucesso', 'estatisticas', 'detalhes' e tempos.
        """
        inicio = time.time()

        valido, msg, df = ImportacaoService.validar_csv_upload(arquivo)
        if not valido:
            return {"sucesso": False, "erro": msg}

        df_limpo, stats_proc = ImportacaoService.processar_dados_csv(df)
        if df_limpo.empty:
            return {"sucesso": False, "erro": "Nenhum registro válido após limpeza"}

        df_novos, df_existentes, stats_novos = ImportacaoService.identificar_ctes_novos(df_limpo)
        duplicatas = ImportacaoService.verificar_duplicatas_internas(df_limpo)

        lista_dados: List[Dict[str, Any]] = [ImportacaoService._linha_para_dict(r) for _, r in df_novos.iterrows()]

        resultado_lote = CTE.criar_ctes_lote(lista_dados)

        fim = time.time()

        estatisticas = {
            "processamento": stats_proc,
            "analise": stats_novos,
            "duplicatas": duplicatas,
            "insercao": {
                "processados": resultado_lote.get("processados", 0),
                "sucessos": resultado_lote.get("sucessos", 0),
                "erros": resultado_lote.get("erros", 0),
                "detalhes": resultado_lote.get("detalhes", []),
            },
            "existentes": len(df_existentes),
        }

        return {
            "sucesso": True,
            "estatisticas": estatisticas,
            "detalhes": resultado_lote.get("detalhes", []),
            "tempo_processamento": round(fim - inicio, 2),
        }

    # --------- Template ---------

    @staticmethod
    def gerar_template_csv() -> str:
        """Gera um CSV de exemplo com TODAS as colunas aceitas pelo sistema."""
        exemplo = {
            "numero_cte": [1001, 1002, 1003],
            "destinatario_nome": ["Cliente A", "Cliente B", "Cliente C"],
            "valor_total": [5500.00, 3200.50, 7800.00],
            "veiculo_placa": ["ABC1234", "XYZ5678", "DEF9012"],
            "data_emissao": ["01/01/2025", "02/01/2025", "03/01/2025"],
            "data_inclusao_fatura": ["02/01/2025", "03/01/2025", "04/01/2025"],
            "numero_fatura": ["NF001", "NF002", "NF003"],
            "primeiro_envio": ["04/01/2025", "", "06/01/2025"],
            "data_rq_tmc": ["05/01/2025", "", "07/01/2025"],
            "data_atesto": ["06/01/2025", "", "08/01/2025"],
            "envio_final": ["07/01/2025", "", "09/01/2025"],
            "data_envio_processo": ["03/01/2025", "04/01/2025", "05/01/2025"],
            "data_baixa": ["", "", "20/01/2025"],
            "observacao": ["Exemplo de atualização", "Pendente de baixa", "Concluído"],
        }
        df = pd.DataFrame(exemplo, columns=ImportacaoService.COLUNAS_PADRAO)
        return df.to_csv(index=False, sep=";", encoding="utf-8-sig")
