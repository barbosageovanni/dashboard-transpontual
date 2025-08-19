from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from app.models.cte import CTE
from app import db
from datetime import datetime
import pandas as pd
import io
from sqlalchemy import func
import logging
from typing import Dict, List, Tuple, Optional
from werkzeug.utils import secure_filename

bp = Blueprint('baixas', __name__, url_prefix='/baixas')

# ============================================================================
# CONFIGURAÇÕES E CONSTANTES
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
        """
        Processa arquivo de baixas (CSV ou Excel) com detecção automática
        
        Returns:
            Tuple[bool, str, Optional[DataFrame]]: (sucesso, mensagem, dataframe)
        """
        try:
            # 1. Validação básica do arquivo
            if not arquivo or not arquivo.filename:
                return False, "Nenhum arquivo enviado", None
            
            filename = secure_filename(arquivo.filename).lower()
            extensao = '.' + filename.split('.')[-1] if '.' in filename else ''
            
            if extensao not in cls.EXTENSOES_PERMITIDAS:
                return False, f"Formato não suportado. Use: {', '.join(cls.EXTENSOES_PERMITIDAS)}", None
            
            # 2. Verificar tamanho
            arquivo.seek(0, 2)
            tamanho = arquivo.tell()
            arquivo.seek(0)
            
            if tamanho > cls.TAMANHO_MAX_ARQUIVO:
                return False, f"Arquivo muito grande. Máximo: {cls.TAMANHO_MAX_ARQUIVO // 1024 // 1024}MB", None
            
            # 3. Processar baseado na extensão
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
        """Processa arquivo CSV com detecção automática de encoding e separador"""
        try:
            # Ler conteúdo
            content = arquivo.read()
            arquivo.seek(0)
            
            # Detectar encoding
            content_str = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content_str = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content_str is None:
                return False, "Não foi possível decodificar o arquivo CSV", None
            
            # Detectar separador
            separadores = [';', ',', '\t', '|']
            df = None
            
            for sep in separadores:
                try:
                    df_teste = pd.read_csv(io.StringIO(content_str), sep=sep, nrows=5)
                    
                    # Verificar se conseguiu detectar colunas
                    if len(df_teste.columns) > 1:
                        # Ler arquivo completo
                        df = pd.read_csv(io.StringIO(content_str), sep=sep)
                        break
                except:
                    continue
            
            if df is None or df.empty:
                return False, "Não foi possível interpretar o formato CSV", None
            
            # Mapear e validar colunas
            sucesso, mensagem, df_processado = cls._mapear_validar_colunas(df)
            
            return sucesso, mensagem, df_processado
            
        except Exception as e:
            return False, f"Erro ao processar CSV: {str(e)}", None
    
    @classmethod
    def _processar_excel(cls, arquivo, extensao: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Processa arquivo Excel (.xlsx ou .xls)"""
        try:
            # Escolher engine baseado na extensão
            if extensao == '.xlsx':
                engine = 'openpyxl'
            else:  # .xls
                engine = 'xlrd'
            
            # Ler Excel
            df = pd.read_excel(arquivo, engine=engine)
            
            if df.empty:
                return False, "Planilha Excel está vazia", None
            
            # Mapear e validar colunas
            sucesso, mensagem, df_processado = cls._mapear_validar_colunas(df)
            
            return sucesso, mensagem, df_processado
            
        except Exception as e:
            return False, f"Erro ao processar Excel: {str(e)}", None
    
    @classmethod
    def _mapear_validar_colunas(cls, df: pd.DataFrame) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Mapeia e valida colunas do DataFrame"""
        try:
            # Limpar nomes das colunas
            df.columns = df.columns.str.strip().str.lower()
            
            # Mapear colunas
            mapeamento = {}
            for campo_modelo, variantes in cls.MAPEAMENTO_COLUNAS_BAIXAS.items():
                for variante in variantes:
                    if variante.lower() in df.columns:
                        mapeamento[variante.lower()] = campo_modelo
                        break
            
            # Renomear colunas
            df_mapeado = df.rename(columns=mapeamento)
            
            # Verificar colunas obrigatórias
            colunas_obrigatorias = ['numero_cte', 'data_baixa']
            faltando = [col for col in colunas_obrigatorias if col not in df_mapeado.columns]
            
            if faltando:
                # Tentar sugestões de colunas disponíveis
                colunas_disponiveis = list(df_mapeado.columns)
                sugestoes = []
                
                for falta in faltando:
                    for disponivel in colunas_disponiveis:
                        if falta.replace('_', '').lower() in disponivel.replace('_', '').lower():
                            sugestoes.append(f"{falta} → {disponivel}")
                
                mensagem_erro = f"Colunas obrigatórias ausentes: {', '.join(faltando)}"
                if sugestoes:
                    mensagem_erro += f". Sugestões: {'; '.join(sugestoes)}"
                
                return False, mensagem_erro, None
            
            # Limpar dados básicos
            df_limpo = df_mapeado.dropna(subset=['numero_cte'])
            
            if df_limpo.empty:
                return False, "Nenhuma linha válida encontrada (números CTE em branco)", None
            
            return True, "Arquivo processado com sucesso", df_limpo
            
        except Exception as e:
            return False, f"Erro na validação: {str(e)}", None

# ============================================================================
# ROTAS PRINCIPAIS
# ============================================================================

@bp.route('/')
@login_required
def index():
    """Página principal do sistema de baixas"""
    return render_template('baixas/index.html')

@bp.route('/api/estatisticas')
@login_required
def api_estatisticas():
    """API para estatísticas de baixas"""
    try:
        # Estatísticas básicas
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/buscar-cte/<int:numero_cte>')
@login_required
def api_buscar_cte(numero_cte):
    """API para buscar informações de um CTE"""
    try:
        cte = CTE.buscar_por_numero(numero_cte)
        if cte:
            return jsonify({
                'success': True,
                'cte': cte.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'CTE {numero_cte} não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/individual', methods=['POST'])
@login_required
def api_baixa_individual():
    """API para registrar baixa individual"""
    try:
        dados = request.get_json()
        numero_cte = dados.get('numero_cte')
        data_baixa = dados.get('data_baixa')
        observacao = dados.get('observacao', '')
        
        if not numero_cte or not data_baixa:
            return jsonify({
                'success': False,
                'message': 'Número do CTE e data da baixa são obrigatórios'
            }), 400
        
        # Buscar CTE
        cte = CTE.buscar_por_numero(numero_cte)
        if not cte:
            return jsonify({
                'success': False,
                'message': f'CTE {numero_cte} não encontrado'
            }), 404
        
        # Converter data
        data_baixa_obj = datetime.strptime(data_baixa, '%Y-%m-%d').date()
        
        # Registrar baixa
        sucesso, mensagem = cte.registrar_baixa(data_baixa_obj, observacao)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem
            })
        else:
            return jsonify({
                'success': False,
                'message': mensagem
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar baixa: {str(e)}'
        }), 500

# ============================================================================
# 🚀 API DE BAIXA EM LOTE - VERSÃO ATUALIZADA
# ============================================================================

@bp.route('/api/lote', methods=['POST'])
@login_required
def api_baixa_lote():
    """
    API para processamento de baixas em lote - VERSÃO ROBUSTA
    Suporta CSV e Excel com detecção automática
    """
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo enviado'
            }), 400
        
        # ✅ PROCESSAMENTO ROBUSTO com detecção automática
        sucesso, mensagem, df = ProcessadorArquivoBaixas.processar_arquivo(arquivo)
        
        if not sucesso:
            return jsonify({
                'sucesso': False,
                'erro': mensagem
            }), 400
        
        # Processar cada linha do DataFrame
        resultados = {
            'processadas': 0,
            'sucessos': 0,
            'erros': 0,
            'detalhes': []
        }
        
        for _, row in df.iterrows():
            try:
                # Extrair dados da linha
                numero_cte = row['numero_cte']
                data_baixa = row['data_baixa']
                observacao = row.get('observacao', '')
                
                # Validar e converter número CTE
                try:
                    numero_cte = int(float(numero_cte)) if pd.notna(numero_cte) else None
                except (ValueError, TypeError):
                    resultados['detalhes'].append({
                        'cte': str(numero_cte),
                        'sucesso': False,
                        'mensagem': 'Número CTE inválido'
                    })
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue
                
                if not numero_cte:
                    resultados['detalhes'].append({
                        'cte': 'N/A',
                        'sucesso': False,
                        'mensagem': 'Número CTE em branco'
                    })
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue
                
                # Validar e converter data
                data_baixa_obj = None
                if pd.notna(data_baixa):
                    try:
                        if isinstance(data_baixa, str):
                            # Tentar diferentes formatos de data
                            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
                            for formato in formatos:
                                try:
                                    data_baixa_obj = datetime.strptime(data_baixa.strip(), formato).date()
                                    break
                                except ValueError:
                                    continue
                        else:
                            # Se já é datetime/date
                            data_baixa_obj = data_baixa.date() if hasattr(data_baixa, 'date') else data_baixa
                    except:
                        pass
                
                if not data_baixa_obj:
                    resultados['detalhes'].append({
                        'cte': numero_cte,
                        'sucesso': False,
                        'mensagem': 'Data de baixa inválida ou em branco'
                    })
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue
                
                # Buscar CTE no banco
                cte = CTE.buscar_por_numero(numero_cte)
                if not cte:
                    resultados['detalhes'].append({
                        'cte': numero_cte,
                        'sucesso': False,
                        'mensagem': 'CTE não encontrado'
                    })
                    resultados['erros'] += 1
                    resultados['processadas'] += 1
                    continue
                
                # Registrar baixa
                sucesso_baixa, mensagem_baixa = cte.registrar_baixa(data_baixa_obj, observacao)
                
                resultados['detalhes'].append({
                    'cte': numero_cte,
                    'sucesso': sucesso_baixa,
                    'mensagem': mensagem_baixa
                })
                
                if sucesso_baixa:
                    resultados['sucessos'] += 1
                else:
                    resultados['erros'] += 1
                    
                resultados['processadas'] += 1
                
            except Exception as e:
                resultados['detalhes'].append({
                    'cte': row.get('numero_cte', 'N/A'),
                    'sucesso': False,
                    'mensagem': f'Erro: {str(e)}'
                })
                resultados['erros'] += 1
                resultados['processadas'] += 1
        
        # Log do resultado
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
        return jsonify({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

# ============================================================================
# ROTAS AUXILIARES
# ============================================================================

@bp.route('/api/template-baixas')
@login_required
def api_template_baixas():
    """API para download do template de baixas"""
    try:
        # Criar template CSV
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
    """API para validação prévia do arquivo"""
    try:
        arquivo = request.files.get('arquivo')
        if not arquivo:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'})
        
        # Processar arquivo
        sucesso, mensagem, df = ProcessadorArquivoBaixas.processar_arquivo(arquivo)
        
        if not sucesso:
            return jsonify({'sucesso': False, 'erro': mensagem})
        
        # Estatísticas do arquivo
        stats = {
            'linhas_totais': len(df),
            'colunas_encontradas': list(df.columns),
            'ctes_unicos': df['numero_cte'].nunique() if 'numero_cte' in df.columns else 0,
            'preview': df.head(3).to_dict('records')
        }
        
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'estatisticas': stats
        })
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)})

# ============================================================================
# LOGGING E AUDITORIA
# ============================================================================

def log_operacao_baixa(usuario_id: int, tipo: str, detalhes: Dict):
    """Log de operações de baixa para auditoria"""
    try:
        # Implementar log de auditoria se necessário
        logging.info(f"Baixa {tipo} - Usuário {usuario_id}: {detalhes}")
    except Exception as e:
        logging.error(f"Erro no log de auditoria: {str(e)}")