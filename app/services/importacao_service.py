#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Importação de CTEs em Lote - Dashboard Baker Flask
app/services/importacao_service.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Union
import io
import os
from werkzeug.utils import secure_filename
from flask import current_app

from app.models.cte import CTE
from app import db
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, InvalidOperation

class ImportacaoService:
    """Serviço especializado para importação de CTEs em lote"""
    
    # Configurações de importação
    EXTENSOES_PERMITIDAS = {'.csv', '.xlsx', '.xls'}
    TAMANHO_MAX_ARQUIVO = 50 * 1024 * 1024  # 50MB
    BATCH_SIZE = 500  # CTEs por lote
    
    # Mapeamento de colunas CSV para campos do modelo
    MAPEAMENTO_COLUNAS = {
        # Variações possíveis de nomes de colunas
        'numero_cte': ['numero_cte', 'num_cte', 'cte', 'numero'],
        'destinatario_nome': ['destinatario_nome', 'cliente', 'destinatario', 'nome_cliente'],
        'veiculo_placa': ['veiculo_placa', 'placa', 'veiculo', 'placa_veiculo'],
        'valor_total': ['valor_total', 'valor', 'total', 'valor_cte'],
        'data_emissao': ['data_emissao', 'emissao', 'data_cte', 'dt_emissao'],
        'numero_fatura': ['numero_fatura', 'fatura', 'num_fatura', 'nf'],
        'data_baixa': ['data_baixa', 'baixa', 'dt_baixa', 'data_pagamento'],
        'observacao': ['observacao', 'obs', 'observacoes', 'comentario'],
        'data_inclusao_fatura': ['data_inclusao_fatura', 'inclusao_fatura', 'dt_inclusao'],
        'data_envio_processo': ['data_envio_processo', 'envio_processo', 'dt_envio'],
        'primeiro_envio': ['primeiro_envio', '1_envio', 'primeiro', 'dt_primeiro_envio'],
        'data_rq_tmc': ['data_rq_tmc', 'rq_tmc', 'dt_rq_tmc', 'rq'],
        'data_atesto': ['data_atesto', 'atesto', 'dt_atesto', 'data_aprovacao'],
        'envio_final': ['envio_final', 'final', 'dt_envio_final', 'conclusao']
    }

    @classmethod
    def processar_importacao_completa(cls, arquivo) -> Dict:
        """
        Processa importação completa de CTEs
        Método principal similar ao sistema de baixas
        """
        resultado = {
            'sucesso': False,
            'erro': None,
            'estatisticas': {},
            'detalhes': [],
            'arquivo_processado': None,
            'tempo_processamento': None
        }
        
        inicio_processamento = datetime.now()
        
        try:
            # 1. Validar arquivo
            valido, mensagem, df_raw = cls.validar_csv_upload(arquivo)
            if not valido:
                resultado['erro'] = mensagem
                return resultado
            
            # 2. Processar dados
            df_limpo, stats_processamento = cls.processar_dados_csv(df_raw)
            if df_limpo.empty:
                resultado['erro'] = 'Nenhum registro válido encontrado no arquivo'
                return resultado
            
            # 3. Identificar CTEs novos vs existentes
            df_novos, df_existentes, stats_analise = cls.identificar_ctes_novos(df_limpo)
            
            # 4. Inserir CTEs novos em lote
            if not df_novos.empty:
                stats_insercao = cls.inserir_ctes_lote(df_novos)
            else:
                stats_insercao = {
                    'processados': 0,
                    'sucessos': 0,
                    'erros': 0,
                    'detalhes': []
                }
            
            # 5. Consolidar estatísticas
            resultado.update({
                'sucesso': True,
                'estatisticas': {
                    'arquivo': {
                        'nome': secure_filename(arquivo.filename),
                        'tamanho': len(arquivo.read()),
                        'linhas_totais': len(df_raw)
                    },
                    'processamento': stats_processamento,
                    'analise': stats_analise,
                    'insercao': stats_insercao
                },
                'detalhes': {
                    'ctes_novos': df_novos.to_dict('records') if not df_novos.empty else [],
                    'ctes_existentes': df_existentes.to_dict('records') if not df_existentes.empty else [],
                    'erros_insercao': stats_insercao.get('detalhes', [])
                },
                'tempo_processamento': (datetime.now() - inicio_processamento).total_seconds()
            })
            
            # Reset arquivo para próxima leitura
            arquivo.seek(0)
            
        except Exception as e:
            current_app.logger.error(f"Erro na importação: {str(e)}")
            resultado['erro'] = f"Erro interno: {str(e)}"
        
        return resultado

    @classmethod
    def validar_csv_upload(cls, arquivo) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Valida arquivo CSV enviado"""
        try:
            # Validar extensão
            if not arquivo.filename.lower().endswith('.csv'):
                return False, "Apenas arquivos CSV são permitidos", None
            
            # Validar tamanho (aproximado)
            arquivo.seek(0, 2)  # Ir para o final
            tamanho = arquivo.tell()
            arquivo.seek(0)  # Voltar ao início
            
            if tamanho > cls.TAMANHO_MAX_ARQUIVO:
                return False, f"Arquivo muito grande. Máximo: {cls.TAMANHO_MAX_ARQUIVO // 1024 // 1024}MB", None
            
            # Tentar ler o CSV
            try:
                # Detectar encoding
                content = arquivo.read()
                arquivo.seek(0)
                
                # Tentar diferentes encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        content_str = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    return False, "Não foi possível decodificar o arquivo. Verifique o encoding.", None
                
                # Ler CSV
                df = pd.read_csv(io.StringIO(content_str), sep=';')
                
                # Validar se tem dados
                if df.empty:
                    return False, "Arquivo CSV está vazio", None
                
                # Validar se tem pelo menos as colunas obrigatórias
                colunas_obrigatorias = ['numero_cte', 'destinatario_nome', 'valor_total']
                colunas_encontradas = cls._mapear_colunas(df.columns.tolist())
                
                faltando = []
                for col in colunas_obrigatorias:
                    if col not in colunas_encontradas:
                        faltando.append(col)
                
                if faltando:
                    return False, f"Colunas obrigatórias ausentes: {', '.join(faltando)}", None
                
                return True, "Arquivo válido", df
                
            except pd.errors.EmptyDataError:
                return False, "Arquivo CSV está vazio", None
            except pd.errors.ParserError as e:
                return False, f"Erro ao ler CSV: {str(e)}", None
                
        except Exception as e:
            return False, f"Erro na validação: {str(e)}", None

    @classmethod
    def processar_dados_csv(cls, df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Processa e limpa dados do CSV"""
        stats = {
            'linhas_originais': len(df_raw),
            'linhas_validas': 0,
            'linhas_descartadas': 0,
            'colunas_mapeadas': {},
            'erros_encontrados': []
        }
        
        try:
            # 1. Mapear colunas
            df = df_raw.copy()
            mapeamento = cls._mapear_colunas(df.columns.tolist())
            df = df.rename(columns=mapeamento)
            stats['colunas_mapeadas'] = mapeamento
            
            # 2. Limpar dados básicos
            df = df.dropna(subset=['numero_cte'], how='all')  # Remover linhas sem CTE
            
            # 3. Processar cada linha
            linhas_validas = []
            
            for idx, row in df.iterrows():
                try:
                    linha_processada = cls._processar_linha(row)
                    if linha_processada:
                        linhas_validas.append(linha_processada)
                        stats['linhas_validas'] += 1
                    else:
                        stats['linhas_descartadas'] += 1
                        stats['erros_encontrados'].append(f"Linha {idx + 1}: dados inválidos")
                except Exception as e:
                    stats['linhas_descartadas'] += 1
                    stats['erros_encontrados'].append(f"Linha {idx + 1}: {str(e)}")
            
            # 4. Criar DataFrame final
            if linhas_validas:
                df_final = pd.DataFrame(linhas_validas)
            else:
                df_final = pd.DataFrame()
            
            return df_final, stats
            
        except Exception as e:
            stats['erros_encontrados'].append(f"Erro geral: {str(e)}")
            return pd.DataFrame(), stats

    @classmethod
    def identificar_ctes_novos(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
        """Identifica CTEs novos vs existentes"""
        stats = {
            'total_analisados': len(df),
            'ctes_novos': 0,
            'ctes_existentes': 0,
            'numeros_duplicados': []
        }
        
        try:
            if df.empty:
                return df, df, stats
            
            # Obter CTEs existentes no banco
            numeros_cte = df['numero_cte'].tolist()
            ctes_existentes_db = set(CTE.obter_ctes_existentes_bulk(numeros_cte))
            
            # Separar novos vs existentes
            df_novos = df[~df['numero_cte'].isin(ctes_existentes_db)].copy()
            df_existentes = df[df['numero_cte'].isin(ctes_existentes_db)].copy()
            
            # Verificar duplicatas internas no próprio arquivo
            duplicatas_internas = df['numero_cte'].duplicated(keep='first')
            if duplicatas_internas.any():
                nums_duplicados = df[duplicatas_internas]['numero_cte'].tolist()
                stats['numeros_duplicados'] = nums_duplicados
                # Remover duplicatas do df_novos
                df_novos = df_novos.drop_duplicates(subset=['numero_cte'], keep='first')
            
            stats.update({
                'ctes_novos': len(df_novos),
                'ctes_existentes': len(df_existentes)
            })
            
            return df_novos, df_existentes, stats
            
        except Exception as e:
            current_app.logger.error(f"Erro ao identificar CTEs: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), stats

    @classmethod
    def inserir_ctes_lote(cls, df: pd.DataFrame) -> Dict:
        """Insere CTEs em lote no banco de dados"""
        stats = {
            'processados': 0,
            'sucessos': 0,
            'erros': 0,
            'detalhes': [],
            'tempo_inicio': datetime.now()
        }
        
        if df.empty:
            return stats
        
        try:
            # Converter DataFrame para lista de dicionários
            lista_ctes = df.to_dict('records')
            
            # Usar método otimizado da classe CTE
            resultado = CTE.criar_ctes_lote(lista_ctes, batch_size=cls.BATCH_SIZE)
            
            # Consolidar estatísticas
            stats.update({
                'processados': resultado.get('processados', 0),
                'sucessos': resultado.get('sucessos', 0),
                'erros': resultado.get('erros', 0),
                'detalhes': resultado.get('detalhes', [])[:100],  # Limitar a 100 detalhes
                'tempo_fim': datetime.now(),
                'duracao': resultado.get('duracao', 0)
            })
            
        except Exception as e:
            current_app.logger.error(f"Erro na inserção em lote: {str(e)}")
            stats['erro_geral'] = str(e)
        
        return stats

    @classmethod
    def _mapear_colunas(cls, colunas_csv: List[str]) -> Dict[str, str]:
        """Mapeia colunas do CSV para campos do modelo"""
        mapeamento = {}
        
        for coluna_csv in colunas_csv:
            coluna_limpa = coluna_csv.strip().lower()
            
            # Buscar correspondência no mapeamento
            for campo_modelo, variacoes in cls.MAPEAMENTO_COLUNAS.items():
                if coluna_limpa in [v.lower() for v in variacoes]:
                    mapeamento[coluna_csv] = campo_modelo
                    break
        
        return mapeamento

    @classmethod
    def _processar_linha(cls, row: pd.Series) -> Optional[Dict]:
        """Processa uma linha individual do CSV"""
        try:
            # Dados obrigatórios
            numero_cte = cls._processar_numero_cte(row.get('numero_cte'))
            if not numero_cte:
                return None
            
            destinatario_nome = cls._processar_texto(row.get('destinatario_nome'))
            if not destinatario_nome:
                return None
            
            valor_total = cls._processar_valor(row.get('valor_total'))
            if valor_total is None or valor_total < 0:
                return None
            
            # Dados opcionais
            dados = {
                'numero_cte': numero_cte,
                'destinatario_nome': destinatario_nome,
                'valor_total': valor_total,
                'veiculo_placa': cls._processar_texto(row.get('veiculo_placa')),
                'data_emissao': cls._processar_data(row.get('data_emissao')),
                'numero_fatura': cls._processar_texto(row.get('numero_fatura')),
                'data_baixa': cls._processar_data(row.get('data_baixa')),
                'observacao': cls._processar_texto(row.get('observacao')),
                'data_inclusao_fatura': cls._processar_data(row.get('data_inclusao_fatura')),
                'data_envio_processo': cls._processar_data(row.get('data_envio_processo')),
                'primeiro_envio': cls._processar_data(row.get('primeiro_envio')),
                'data_rq_tmc': cls._processar_data(row.get('data_rq_tmc')),
                'data_atesto': cls._processar_data(row.get('data_atesto')),
                'envio_final': cls._processar_data(row.get('envio_final')),
                'origem_dados': 'Importação CSV'
            }
            
            # Validar dados
            valido, erros = CTE.validar_dados_importacao(dados)
            if not valido:
                current_app.logger.warning(f"CTE {numero_cte} inválido: {erros}")
                return None
            
            return dados
            
        except Exception as e:
            current_app.logger.error(f"Erro ao processar linha: {str(e)}")
            return None

    @classmethod
    def _processar_numero_cte(cls, valor) -> Optional[int]:
        """Processa número do CTE"""
        if pd.isna(valor):
            return None
        
        try:
            # Converter para int, removendo decimais se necessário
            numero = int(float(str(valor).strip()))
            return numero if numero > 0 else None
        except (ValueError, TypeError):
            return None

    @classmethod
    def _processar_valor(cls, valor) -> Optional[float]:
        """Processa valores monetários"""
        if pd.isna(valor):
            return None
        
        try:
            # Limpar formatação brasileira
            if isinstance(valor, str):
                valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            
            valor_float = float(valor)
            return valor_float if valor_float >= 0 else None
        except (ValueError, TypeError):
            return None

    @classmethod
    def _processar_data(cls, valor) -> Optional[date]:
        """Processa datas em vários formatos"""
        if pd.isna(valor):
            return None
        
        if isinstance(valor, date):
            return valor
        
        if isinstance(valor, datetime):
            return valor.date()
        
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return None
            
            # Tentar vários formatos
            formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y']
            
            for formato in formatos:
                try:
                    return datetime.strptime(valor, formato).date()
                except ValueError:
                    continue
        
        return None

    @classmethod
    def _processar_texto(cls, valor) -> Optional[str]:
        """Processa campos de texto"""
        if pd.isna(valor):
            return None
        
        texto = str(valor).strip()
        return texto if texto else None

    @classmethod
    def gerar_template_csv(cls) -> str:
        """Gera template CSV para download"""
        colunas = [
            'numero_cte', 'destinatario_nome', 'valor_total', 'data_emissao',
            'veiculo_placa', 'numero_fatura', 'data_baixa', 'observacao',
            'data_inclusao_fatura', 'data_envio_processo', 'primeiro_envio',
            'data_rq_tmc', 'data_atesto', 'envio_final'
        ]
        
        # Dados de exemplo
        exemplo = {
            'numero_cte': [12345, 12346],
            'destinatario_nome': ['Cliente Exemplo Ltda', 'Empresa ABC S/A'],
            'valor_total': [1500.50, 2750.00],
            'data_emissao': ['01/01/2025', '02/01/2025'],
            'veiculo_placa': ['ABC1234', 'XYZ5678'],
            'numero_fatura': ['NF001', 'NF002'],
            'data_baixa': ['', ''],
            'observacao': ['Primeira importação', 'Dados migrados'],
            'data_inclusao_fatura': ['02/01/2025', '03/01/2025'],
            'data_envio_processo': ['03/01/2025', '04/01/2025'],
            'primeiro_envio': ['04/01/2025', '05/01/2025'],
            'data_rq_tmc': ['05/01/2025', '06/01/2025'],
            'data_atesto': ['06/01/2025', ''],
            'envio_final': ['07/01/2025', '']
        }
        
        df = pd.DataFrame(exemplo)
        return df.to_csv(sep=';', index=False, encoding='utf-8-sig')

    @classmethod
    def obter_estatisticas_importacao(cls) -> Dict:
        """Obtém estatísticas para o dashboard"""
        try:
            # Estatísticas gerais
            stats = CTE.estatisticas_importacao()
            
            # Estatísticas específicas de importação (últimos 30 dias)
            data_limite = datetime.now().date() - pd.Timedelta(days=30)
            
            ctes_importados = CTE.query.filter(
                CTE.created_at >= data_limite,
                CTE.origem_dados.like('%CSV%')
            ).count()
            
            stats['importacoes_recentes'] = ctes_importados
            
            return stats
            
        except Exception as e:
            return {'erro': str(e)}

    @classmethod
    def verificar_duplicatas_internas(cls, df: pd.DataFrame) -> Dict:
        """Verifica duplicatas dentro do próprio arquivo"""
        if df.empty:
            return {'tem_duplicatas': False, 'quantidade': 0, 'numeros': []}
        
        duplicatas = df['numero_cte'].duplicated(keep=False)
        
        if duplicatas.any():
            numeros_duplicados = df[duplicatas]['numero_cte'].unique().tolist()
            return {
                'tem_duplicatas': True,
                'quantidade': len(numeros_duplicados),
                'numeros': numeros_duplicados
            }
        
        return {'tem_duplicatas': False, 'quantidade': 0, 'numeros': []}