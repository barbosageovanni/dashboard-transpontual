from app import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Tuple, Optional, Union
import pandas as pd
import logging
import re
import io

# =============================================================================
# Helpers internos (conversões seguras) - CORRIGIDOS
# =============================================================================

def _to_int_safe(value) -> Optional[int]:
    """Conversão segura para inteiro"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        if isinstance(value, str):
            v = value.strip()
            if not v:
                return None
            # trata "123.0"
            return int(float(v))
        return int(float(value))
    except (ValueError, TypeError):
        return None

def _to_float_safe(value) -> Optional[float]:
    """Conversão segura para float"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        if isinstance(value, str):
            v = value.strip()
            if not v:
                return None
            # remove R$, pontos e converte vírgula para ponto
            v = v.replace('R$', '').replace('.', '').replace(',', '.')
            return float(v)
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        return None
    except (ValueError, TypeError):
        return None

_DATE_RE_ISO = re.compile(r'^\d{4}-\d{2}-\d{2}$')
_DATE_RE_BR  = re.compile(r'^\d{2}/\d{2}/\d{4}$')

def _to_date_safe(value) -> Optional[date]:
    """Conversão segura para data"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            v = value.strip()
            if not v:
                return None
            # tenta formatos comuns
            if _DATE_RE_BR.match(v):
                return datetime.strptime(v, '%d/%m/%Y').date()
            if _DATE_RE_ISO.match(v):
                return datetime.strptime(v, '%Y-%m-%d').date()
            # fallback: deixa o pandas tentar
            return pd.to_datetime(v, errors='coerce').date()
        # números (Excel) — pandas já lê como Timestamp normalmente
        return pd.to_datetime(value, errors='coerce').date()
    except Exception:
        return None

def _to_str_safe(value) -> Optional[str]:
    """Conversão segura para string"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value).strip()
    return s if s else None

# Mapeia cabeçalhos de planilha -> nomes dos campos do modelo
HEADER_MAP = {
    # essenciais
    'numero cte': 'numero_cte',
    'número cte': 'numero_cte',
    'numero_cte': 'numero_cte',
    'num_cte': 'numero_cte',
    'cte': 'numero_cte',

    'destinatario nome': 'destinatario_nome',
    'destinatário nome': 'destinatario_nome',
    'destinatario_nome': 'destinatario_nome',
    'cliente': 'destinatario_nome',
    'nome_cliente': 'destinatario_nome',

    'valor total': 'valor_total',
    'valor_total': 'valor_total',
    'valor': 'valor_total',
    'total': 'valor_total',

    # demais campos
    'data emissão': 'data_emissao',
    'data emissao': 'data_emissao',
    'data_emissao': 'data_emissao',
    'emissao': 'data_emissao',

    'placa veículo': 'veiculo_placa',
    'veiculo placa': 'veiculo_placa',
    'veiculo_placa': 'veiculo_placa',
    'placa': 'veiculo_placa',

    'data inclusão fatura': 'data_inclusao_fatura',
    'data inclusao fatura': 'data_inclusao_fatura',
    'data_inclusao_fatura': 'data_inclusao_fatura',
    'inclusao_fatura': 'data_inclusao_fatura',

    'número fatura': 'numero_fatura',
    'numero fatura': 'numero_fatura',
    'numero_fatura': 'numero_fatura',
    'fatura': 'numero_fatura',

    'primeiro envio': 'primeiro_envio',
    'primeiro_envio': 'primeiro_envio',
    '1_envio': 'primeiro_envio',

    'envio final': 'envio_final',
    'envio_final': 'envio_final',
    'final': 'envio_final',

    'data atesto': 'data_atesto',
    'data_atesto': 'data_atesto',
    'atesto': 'data_atesto',

    'data baixa': 'data_baixa',
    'data_baixa': 'data_baixa',
    'baixa': 'data_baixa',

    'data envio processo': 'data_envio_processo',
    'data_envio_processo': 'data_envio_processo',
    'envio_processo': 'data_envio_processo',

    'data rq tmc': 'data_rq_tmc',
    'data_rq_tmc': 'data_rq_tmc',
    'rq_tmc': 'data_rq_tmc',

    'observação': 'observacao',
    'observacao': 'observacao',
    'obs': 'observacao',
}

def _normalize_headers(cols: List[str]) -> List[str]:
    """Normaliza cabeçalhos da planilha"""
    out = []
    for c in cols:
        k = (c or '').strip().lower()
        k = HEADER_MAP.get(k, k)  # aplica mapeamento se existir
        out.append(k)
    return out


# =============================================================================
# Modelo CTE - VERSÃO CORRIGIDA
# =============================================================================

class CTE(db.Model):
    """Modelo para CTEs - usa a tabela existente."""
    __tablename__ = 'dashboard_baker'

    id = db.Column(db.Integer, primary_key=True)
    numero_cte = db.Column(db.Integer, unique=True, nullable=False, index=True)

    # Dados principais
    destinatario_nome = db.Column(db.String(255))
    veiculo_placa = db.Column(db.String(20))
    valor_total = db.Column(db.Numeric(15, 2), nullable=False, default=0)

    # Datas principais
    data_emissao = db.Column(db.Date)
    data_baixa = db.Column(db.Date)

    # Faturamento / Processo
    numero_fatura = db.Column(db.String(100))
    data_inclusao_fatura = db.Column(db.Date)
    data_envio_processo = db.Column(db.Date)
    primeiro_envio = db.Column(db.Date)
    data_rq_tmc = db.Column(db.Date)
    data_atesto = db.Column(db.Date)
    envio_final = db.Column(db.Date)

    # Observações e metadados
    observacao = db.Column(db.Text)
    origem_dados = db.Column(db.String(50), default='Sistema')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def atualizar_seguro(self, dados: dict) -> tuple:
        """
        ✅ MÉTODO CORRIGIDO: Sempre retorna tupla (sucesso, mensagem)
        """
        try:
            from app import db
            
            if not dados:
                return False, "Nenhum dado fornecido"
            
            campos_atualizados = 0
            
            # Lista de campos que podem ser atualizados
            campos_permitidos = [
                'destinatario_nome', 'veiculo_placa', 'valor_total',
                'data_emissao', 'data_baixa', 'numero_fatura',
                'data_inclusao_fatura', 'data_envio_processo',
                'primeiro_envio', 'data_rq_tmc', 'data_atesto',
                'envio_final', 'observacao'
            ]
            
            # Atualizar campos válidos
            for campo, valor in dados.items():
                if campo in campos_permitidos and hasattr(self, campo):
                    try:
                        # Tratamento especial para datas
                        if 'data' in campo.lower() and isinstance(valor, str):
                            if valor.strip():  # Se não estiver vazio
                                from datetime import datetime
                                valor_data = datetime.strptime(valor.strip(), '%Y-%m-%d').date()
                                setattr(self, campo, valor_data)
                                campos_atualizados += 1
                        elif valor is not None and str(valor).strip():
                            setattr(self, campo, valor)
                            campos_atualizados += 1
                    except Exception:
                        continue  # Pular campos com erro
            
            if campos_atualizados > 0:
                self.updated_at = datetime.utcnow()
                db.session.commit()
                return True, f"CTE {self.numero_cte} atualizado ({campos_atualizados} campos)"
            else:
                return False, "Nenhum campo foi atualizado"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atualizar: {str(e)}"


    def __repr__(self) -> str:
        return f'<CTE {self.numero_cte}>'

    # -------------------------------------------------------------------------
    # Propriedades calculadas
    # -------------------------------------------------------------------------
    @property
    def has_baixa(self) -> bool:
        """Verifica se tem baixa"""
        return self.data_baixa is not None

    @property
    def processo_completo(self) -> bool:
        """Verifica se o processo está completo"""
        campos = [self.data_emissao, self.primeiro_envio, self.data_atesto, self.envio_final]
        return all(d is not None for d in campos)

    @property
    def status_processo(self) -> str:
        """Retorna status do processo"""
        if self.processo_completo:
            return 'Finalizado' if self.data_baixa else 'Completo'
        if self.envio_final:
            return 'Envio Final'
        if self.data_atesto:
            return 'Atestado'
        if self.primeiro_envio:
            return 'Enviado'
        if self.data_emissao:
            return 'Emitido'
        return 'Pendente'

    # -------------------------------------------------------------------------
    # MÉTODO FALTANTE - ADICIONADO PARA CORRIGIR ERRO
    # -------------------------------------------------------------------------
    @classmethod
    def validar_dados_importacao(cls, dados: Dict) -> Tuple[bool, List[str]]:
        """
        Validação específica para dados de importação
        🔧 MÉTODO FALTANTE ADICIONADO - CORRIGE O ERRO DOS LOGS
        """
        erros = []
        
        try:
            # Função helper para validação segura
            def validar_texto(valor, nome_campo, min_length=1):
                """Valida texto de forma segura"""
                if valor is None:
                    return None
                if not isinstance(valor, str):
                    valor = str(valor)
                valor_limpo = valor.strip()
                if len(valor_limpo) < min_length:
                    return None
                return valor_limpo
            
            # Validações obrigatórias
            if not dados.get('numero_cte'):
                erros.append("Número do CTE é obrigatório")
            elif not isinstance(dados['numero_cte'], (int, float)) or dados['numero_cte'] <= 0:
                erros.append("Número do CTE deve ser um número positivo")
            
            # Validação segura do destinatário
            destinatario_validado = validar_texto(dados.get('destinatario_nome'), 'destinatario_nome', 3)
            if not destinatario_validado:
                erros.append("Nome do destinatário é obrigatório e deve ter pelo menos 3 caracteres")
            
            # Validação segura do valor
            try:
                valor_total = dados.get('valor_total')
                if valor_total is None:
                    erros.append("Valor total é obrigatório")
                else:
                    valor_float = float(valor_total)
                    if valor_float < 0:
                        erros.append("Valor total não pode ser negativo")
                    elif valor_float > 1000000:  # Limite de 1 milhão
                        erros.append("Valor total muito alto (máximo: R$ 1.000.000,00)")
            except (ValueError, TypeError):
                erros.append("Valor total deve ser numérico")
            
            # Validações de formato - COM PROTEÇÃO
            veiculo_validado = validar_texto(dados.get('veiculo_placa'), 'veiculo_placa', 1)
            if dados.get('veiculo_placa') and not veiculo_validado:
                erros.append("Placa do veículo inválida")
            
            # Verificar se CTE já existe (opcional - depende do contexto)
            if dados.get('numero_cte'):
                existe = cls.query.filter_by(numero_cte=dados['numero_cte']).first()
                if existe:
                    erros.append(f"CTE {dados['numero_cte']} já existe no sistema")
            
            return len(erros) == 0, erros
            
        except Exception as e:
            erros.append(f"Erro na validação: {str(e)}")
            return False, erros

    # -------------------------------------------------------------------------
    # MÉTODOS DE TEMPLATE CSV - ADICIONADOS
    # -------------------------------------------------------------------------
    @classmethod
    def gerar_template_csv_atualizacao(cls) -> str:
        """
        Gera template CSV para atualização (todos os campos)
        🔧 MÉTODO FALTANTE ADICIONADO
        """
        # Headers para atualização (todos os campos)
        headers = [
            'numero_cte',
            'destinatario_nome', 
            'veiculo_placa',
            'valor_total',
            'data_emissao',
            'numero_fatura',
            'data_baixa',
            'observacao',
            'data_inclusao_fatura',
            'data_envio_processo',
            'primeiro_envio',
            'data_rq_tmc',
            'data_atesto',
            'envio_final'
        ]
        
        # Linha de exemplo
        exemplo = [
            '123456',
            'EMPRESA EXEMPLO LTDA',
            'ABC1234',
            '1500.50',
            '2025-01-15',
            'FAT001',
            '2025-02-15',
            'Observação exemplo',
            '2025-01-16',
            '2025-01-17',
            '2025-01-18',
            '2025-01-19',
            '2025-01-20',
            '2025-01-21'
        ]
        
        # Montar CSV com separador ';'
        output = io.StringIO()
        output.write(';'.join(headers) + '\n')
        output.write(';'.join(exemplo) + '\n')
        
        content = output.getvalue()
        output.close()
        
        return content

    @classmethod
    def processar_csv_atualizacao(cls, csv_path: str, modo='alterar') -> Dict:
        """
        Processa CSV para atualização/upsert de CTEs
        🔧 MÉTODO FALTANTE ADICIONADO
        """
        resultado = {
            'sucesso': True,
            'atualizados': 0,
            'inseridos': 0,
            'erros': 0,
            'detalhes': [],
            'erro': None
        }
        
        try:
            # Ler CSV
            try:
                df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')
            except Exception:
                df = pd.read_csv(csv_path, sep=',', encoding='utf-8-sig')
            
            # Normalizar headers
            df.columns = _normalize_headers(list(df.columns))
            
            for index, row in df.iterrows():
                try:
                    numero_cte = _to_int_safe(row.get('numero_cte'))
                    if not numero_cte or numero_cte <= 0:
                        resultado['erros'] += 1
                        resultado['detalhes'].append(f"Linha {index + 2}: Número CTE inválido")
                        continue
                    
                    # Buscar CTE existente
                    cte_existente = cls.query.filter_by(numero_cte=numero_cte).first()
                    
                    # Preparar dados usando o método _from_row existente
                    dados = cls._from_row(row)
                    if not dados:
                        resultado['erros'] += 1
                        resultado['detalhes'].append(f"Linha {index + 2}: Dados inválidos")
                        continue
                    
                    if cte_existente and modo in ['alterar', 'upsert']:
                        # Atualizar existente
                        ok, msg = cte_existente.alterar(dados)
                        if ok:
                            resultado['atualizados'] += 1
                            resultado['detalhes'].append(f"CTE {numero_cte} atualizado")
                        else:
                            resultado['erros'] += 1
                            resultado['detalhes'].append(f"CTE {numero_cte}: {msg}")
                        
                    elif not cte_existente and modo in ['inserir', 'upsert']:
                        # Inserir novo
                        ok, obj_or_msg = cls.criar_cte_otimizado(dados)
                        if ok:
                            resultado['inseridos'] += 1
                            resultado['detalhes'].append(f"CTE {numero_cte} inserido")
                        else:
                            resultado['erros'] += 1
                            resultado['detalhes'].append(f"CTE {numero_cte}: {obj_or_msg}")
                        
                    else:
                        resultado['erros'] += 1
                        if cte_existente:
                            resultado['detalhes'].append(f"CTE {numero_cte} já existe (modo: {modo})")
                        else:
                            resultado['detalhes'].append(f"CTE {numero_cte} não encontrado (modo: {modo})")
                    
                except Exception as e:
                    resultado['erros'] += 1
                    resultado['detalhes'].append(f"Linha {index + 2}: Erro - {str(e)}")
            
            # Commit das alterações
            if resultado['atualizados'] > 0 or resultado['inseridos'] > 0:
                db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            resultado['sucesso'] = False
            resultado['erro'] = str(e)
            logging.exception("Erro no processamento CSV de atualização")
        
        return resultado

    # -------------------------------------------------------------------------
    # Serialização
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict:
        """Conversão para dicionário com tratamento de erro"""
        try:
            return {
                'id': self.id,
                'numero_cte': self.numero_cte,
                'destinatario_nome': self.destinatario_nome or '',
                'veiculo_placa': self.veiculo_placa or '',
                'valor_total': float(self.valor_total) if self.valor_total is not None else 0.0,
                'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
                'data_baixa': self.data_baixa.isoformat() if self.data_baixa else None,
                'numero_fatura': self.numero_fatura or '',
                'data_inclusao_fatura': self.data_inclusao_fatura.isoformat() if self.data_inclusao_fatura else None,
                'data_envio_processo': self.data_envio_processo.isoformat() if self.data_envio_processo else None,
                'primeiro_envio': self.primeiro_envio.isoformat() if self.primeiro_envio else None,
                'data_rq_tmc': self.data_rq_tmc.isoformat() if self.data_rq_tmc else None,
                'data_atesto': self.data_atesto.isoformat() if self.data_atesto else None,
                'envio_final': self.envio_final.isoformat() if self.envio_final else None,
                'observacao': self.observacao or '',
                'has_baixa': self.has_baixa,
                'processo_completo': self.processo_completo,
                'status_processo': self.status_processo,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'origem_dados': self.origem_dados or 'Sistema'
            }
        except Exception as e:
            logging.exception("Erro em to_dict")
            return {
                'numero_cte': self.numero_cte,
                'erro': str(e),
            }

    def to_dict_importacao(self) -> Dict:
        """Conversão otimizada para importação/exportação"""
        try:
            fmt = '%Y-%m-%d'
            fd = lambda d: d.strftime(fmt) if d else None
            return {
                'numero_cte': self.numero_cte,
                'destinatario_nome': self.destinatario_nome,
                'veiculo_placa': self.veiculo_placa,
                'valor_total': float(self.valor_total) if self.valor_total is not None else 0.0,
                'data_emissao': fd(self.data_emissao),
                'numero_fatura': self.numero_fatura,
                'data_baixa': fd(self.data_baixa),
                'observacao': self.observacao,
                'data_inclusao_fatura': fd(self.data_inclusao_fatura),
                'data_envio_processo': fd(self.data_envio_processo),
                'primeiro_envio': fd(self.primeiro_envio),
                'data_rq_tmc': fd(self.data_rq_tmc),
                'data_atesto': fd(self.data_atesto),
                'envio_final': fd(self.envio_final),
                'origem_dados': self.origem_dados,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
            }
        except Exception as e:
            logging.exception("Erro ao converter CTE para dict de importação")
            return {'numero_cte': self.numero_cte, 'erro': str(e)}

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @classmethod
    def buscar_por_numero(cls, numero_cte: int) -> Optional['CTE']:
        """Busca CTE por número"""
        try:
            return cls.query.filter_by(numero_cte=numero_cte).first()
        except Exception as e:
            logging.error(f"Erro ao buscar CTE {numero_cte}: {e}")
            return None

    @classmethod
    def criar_cte(cls, dados: Dict) -> Tuple[bool, Union[str, 'CTE']]:
        """Cria novo CTE com validação"""
        try:
            # Normalizar payload
            payload = cls._normalize_payload(dados)
            if payload.get('numero_cte') is None:
                return False, "Número do CTE é obrigatório"

            # Verificar duplicata
            if cls.buscar_por_numero(payload['numero_cte']):
                return False, f"CTE {payload['numero_cte']} já existe"

            # Validar dados
            valido, erros = cls.validar_dados_importacao(payload)
            if not valido:
                return False, "; ".join(erros)

            cte = cls(**payload)
            db.session.add(cte)
            db.session.commit()
            return True, cte
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Erro ao criar CTE: {e}")
            return False, str(e)

    def alterar(self, dados: Dict) -> Tuple[bool, str]:
        """Alterar SOMENTE os campos presentes em `dados`."""
        try:
            payload = self._normalize_payload(dados)
            for k, v in payload.items():
                if hasattr(self, k) and k not in ['id', 'numero_cte']:
                    setattr(self, k, v)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True, "CTE atualizado com sucesso"
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Erro ao alterar CTE {self.numero_cte}: {e}")
            return False, str(e)

    @classmethod
    def alterar_cte(cls, numero_cte: int, dados: Dict) -> Tuple[bool, str]:
        """Altera CTE por número"""
        inst = cls.buscar_por_numero(numero_cte)
        if not inst:
            return False, f"CTE {numero_cte} não encontrado"
        return inst.alterar(dados)

    def registrar_baixa(self, data_baixa: date, observacao: str = "") -> Tuple[bool, str]:
        """Registra baixa do CTE"""
        try:
            if self.data_baixa:
                return False, "CTE já possui baixa"
            self.data_baixa = data_baixa
            if observacao:
                self.observacao = f"{self.observacao or ''} | BAIXA: {observacao}"
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True, f"Baixa registrada para CTE {self.numero_cte}"
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Erro ao registrar baixa CTE {self.numero_cte}: {e}")
            return False, str(e)

    # -------------------------------------------------------------------------
    # Importação / Atualização em lote
    # -------------------------------------------------------------------------
    @classmethod
    def obter_ctes_existentes_bulk(cls, numeros_cte: List[int]) -> set:
        """Obtém CTEs existentes em lote"""
        if not numeros_cte:
            return set()
        try:
            result = db.session.query(cls.numero_cte).filter(cls.numero_cte.in_(numeros_cte)).all()
            return set(r[0] for r in result)
        except Exception as e:
            logging.error(f"Erro ao obter CTEs existentes: {e}")
            return set()

    @classmethod
    def criar_cte_otimizado(cls, dados: Dict) -> Tuple[bool, Union[str, 'CTE']]:
        """Versão otimizada do método criar_cte para importação em lote"""
        try:
            payload = cls._normalize_payload(dados)
            ncte = payload.get('numero_cte')
            if not ncte:
                return False, "Número do CTE inválido"

            if not _to_str_safe(payload.get('destinatario_nome')):
                return False, "Nome do destinatário é obrigatório"

            v = payload.get('valor_total')
            if v is None or float(v) < 0:
                return False, "Valor total inválido"

            if cls.buscar_por_numero(ncte):
                return False, f"CTE {ncte} já existe"

            cte = cls(**payload)
            db.session.add(cte)
            db.session.flush()
            return True, cte
        except IntegrityError as e:
            db.session.rollback()
            if 'numero_cte' in str(e):
                return False, f"CTE {dados.get('numero_cte')} já existe"
            return False, f"Erro de integridade: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Erro ao criar CTE otimizado: {e}")
            return False, f"Erro ao criar CTE: {str(e)}"

    @classmethod
    def aplicar_alteracoes_lote(cls, lista_dados: List[Dict], modo: str = 'alterar', batch_size: int = 500) -> Dict:
        """
        Aplica alterações em lote.
        modo:
          - 'alterar' -> só atualiza existentes
          - 'inserir' -> só insere novos
          - 'upsert'  -> atualiza se existir, senão cria
        """
        res = {
            'processados': 0,
            'atualizados': 0,
            'inseridos': 0,
            'erros': 0,
            'detalhes': [],
            'tempo_inicio': datetime.now()
        }

        try:
            numeros = [_to_int_safe(d.get('numero_cte')) for d in lista_dados]
            numeros = [n for n in numeros if n]
            existentes = cls.obter_ctes_existentes_bulk(numeros)

            for i in range(0, len(lista_dados), batch_size):
                batch = lista_dados[i:i+batch_size]
                try:
                    for dados in batch:
                        res['processados'] += 1
                        ndados = cls._normalize_payload(dados)
                        ncte = ndados.get('numero_cte')
                        if not ncte:
                            res['erros'] += 1
                            res['detalhes'].append({'cte': None, 'sucesso': False, 'mensagem': 'Número CTE ausente'})
                            continue

                        existe = ncte in existentes

                        if modo == 'alterar':
                            if not existe:
                                res['detalhes'].append({'cte': ncte, 'sucesso': False, 'mensagem': 'CTE não existe (ignorado)'})
                                continue
                            ok, msg = cls.alterar_cte(ncte, ndados)
                            if ok:
                                res['atualizados'] += 1
                            else:
                                res['erros'] += 1
                            res['detalhes'].append({'cte': ncte, 'sucesso': ok, 'mensagem': msg})

                        elif modo == 'inserir':
                            if existe:
                                res['detalhes'].append({'cte': ncte, 'sucesso': False, 'mensagem': 'CTE já existe (ignorado)'})
                                continue
                            ok, obj_or_msg = cls.criar_cte_otimizado(ndados)
                            if ok:
                                res['inseridos'] += 1
                                res['detalhes'].append({'cte': ncte, 'sucesso': True, 'mensagem': 'Inserido'})
                            else:
                                res['erros'] += 1
                                res['detalhes'].append({'cte': ncte, 'sucesso': False, 'mensagem': obj_or_msg})

                        else:  # upsert
                            if existe:
                                ok, msg = cls.alterar_cte(ncte, ndados)
                                if ok:
                                    res['atualizados'] += 1
                                else:
                                    res['erros'] += 1
                                res['detalhes'].append({'cte': ncte, 'sucesso': ok, 'mensagem': msg})
                            else:
                                ok, obj_or_msg = cls.criar_cte_otimizado(ndados)
                                if ok:
                                    res['inseridos'] += 1
                                    res['detalhes'].append({'cte': ncte, 'sucesso': True, 'mensagem': 'Inserido'})
                                else:
                                    res['erros'] += 1
                                    res['detalhes'].append({'cte': ncte, 'sucesso': False, 'mensagem': obj_or_msg})

                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logging.exception(f"Erro no lote: {e}")
                    for dados in batch:
                        res['erros'] += 1
                        res['detalhes'].append({'cte': dados.get('numero_cte'), 'sucesso': False, 'mensagem': f'Erro no lote: {e}'})

            res['tempo_fim'] = datetime.now()
            res['duracao'] = (res['tempo_fim'] - res['tempo_inicio']).total_seconds()
            return res
        except Exception as e:
            logging.exception("Erro em aplicar_alteracoes_lote")
            res['erro_geral'] = str(e)
            return res

    # -------------------------------------------------------------------------
    # CSV — Importação e Atualização
    # -------------------------------------------------------------------------
    @classmethod
    def processar_csv_importacao(cls, arquivo_path: str) -> Dict:
        """Importa APENAS novos CTEs a partir de CSV"""
        try:
            try:
                df = pd.read_csv(arquivo_path, sep=';', encoding='utf-8-sig')
            except Exception:
                df = pd.read_csv(arquivo_path, sep=',', encoding='utf-8-sig')

            df.columns = _normalize_headers(list(df.columns))
            dados = []
            for _, row in df.iterrows():
                d = cls._from_row(row)
                if d:
                    dados.append(d)
            return cls.criar_ctes_lote(dados)
        except Exception as e:
            logging.exception(f"Erro no processamento CSV de importação: {e}")
            return {'erro_geral': str(e), 'processados': 0, 'sucessos': 0, 'erros': 0}

    # -------------------------------------------------------------------------
    # Fluxos já existentes — preservados
    # -------------------------------------------------------------------------
    @classmethod
    def criar_ctes_lote(cls, lista_dados: List[Dict], batch_size: int = 500) -> Dict:
        """Cria CTEs em lote (apenas novos)"""
        res = {
            'processados': 0,
            'sucessos': 0,
            'erros': 0,
            'ctes_existentes': 0,
            'detalhes': [],
            'tempo_inicio': datetime.now()
        }
        try:
            numeros = [d['numero_cte'] for d in lista_dados if d.get('numero_cte')]
            existentes = cls.obter_ctes_existentes_bulk(numeros)
            res['ctes_existentes'] = len(existentes)

            novos = [d for d in lista_dados if d.get('numero_cte') not in existentes]

            for i in range(0, len(novos), batch_size):
                batch = novos[i:i+batch_size]
                try:
                    for dados in batch:
                        res['processados'] += 1
                        ok, obj_or_msg = cls.criar_cte_otimizado(dados)
                        if ok:
                            res['sucessos'] += 1
                            res['detalhes'].append({'cte': dados['numero_cte'], 'sucesso': True, 'mensagem': 'CTE criado'})
                        else:
                            res['erros'] += 1
                            res['detalhes'].append({'cte': dados.get('numero_cte'), 'sucesso': False, 'mensagem': str(obj_or_msg)})
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logging.exception(f"Erro no lote: {e}")
                    for d in batch:
                        res['erros'] += 1
                        res['detalhes'].append({'cte': d.get('numero_cte'), 'sucesso': False, 'mensagem': f'Erro no lote: {e}'})

            for numero_cte in existentes:
                res['detalhes'].append({'cte': numero_cte, 'sucesso': False, 'mensagem': 'CTE já existe no banco'})

            res['tempo_fim'] = datetime.now()
            res['duracao'] = (res['tempo_fim'] - res['tempo_inicio']).total_seconds()
            return res
        except Exception as e:
            logging.exception("Erro em criar_ctes_lote")
            res['erro_geral'] = str(e)
            return res

    # -------------------------------------------------------------------------
    # Normalização de linha/payload
    # -------------------------------------------------------------------------
    @classmethod
    def _from_row(cls, row) -> Optional[Dict]:
        """Converte uma linha do DataFrame em payload normalizado."""
        try:
            num = _to_int_safe(row.get('numero_cte'))
            if not num:
                return None

            destino = _to_str_safe(row.get('destinatario_nome'))
            if not destino or len(destino) < 1:
                return None

            valor = _to_float_safe(row.get('valor_total'))
            if valor is None:
                return None

            data = {
                'numero_cte': num,
                'destinatario_nome': destino,
                'veiculo_placa': _to_str_safe(row.get('veiculo_placa')),
                'valor_total': valor,

                'data_emissao': _to_date_safe(row.get('data_emissao')),
                'numero_fatura': _to_str_safe(row.get('numero_fatura')),
                'data_baixa': _to_date_safe(row.get('data_baixa')),
                'observacao': _to_str_safe(row.get('observacao')),

                'data_inclusao_fatura': _to_date_safe(row.get('data_inclusao_fatura')),
                'data_envio_processo': _to_date_safe(row.get('data_envio_processo')),
                'primeiro_envio': _to_date_safe(row.get('primeiro_envio')),
                'data_rq_tmc': _to_date_safe(row.get('data_rq_tmc')),
                'data_atesto': _to_date_safe(row.get('data_atesto')),
                'envio_final': _to_date_safe(row.get('envio_final')),

                'origem_dados': _to_str_safe(row.get('origem_dados')) or 'Planilha',
            }
            return data
        except Exception as e:
            logging.error(f"Erro ao processar linha: {e}")
            return None


    def atualizar(self, dados: dict) -> bool:
        """
        Atualiza os dados do CTE
        
        Args:
            dados (dict): Dicionário com os novos dados
            
        Returns:
            bool: True se atualização foi bem-sucedida
        """
        try:
            # Campos que podem ser atualizados
            campos_permitidos = [
                'destinatario_nome', 'veiculo_placa', 'valor_total',
                'data_emissao', 'data_baixa', 'numero_fatura',
                'data_inclusao_fatura', 'data_envio_processo',
                'primeiro_envio', 'data_rq_tmc', 'data_atesto',
                'envio_final', 'observacao'
            ]
            
            # Atualizar apenas campos permitidos
            for campo, valor in dados.items():
                if campo in campos_permitidos and hasattr(self, campo):
                    setattr(self, campo, valor)
            
            # Atualizar timestamp
            self.updated_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar CTE {self.numero_cte}: {e}")
            return False
    
    @classmethod
    def atualizar_lote(cls, dados_lote: list) -> dict:
        """
        Atualiza múltiplos CTEs em lote
        
        Args:
            dados_lote (list): Lista de dicionários com dados para atualização
            
        Returns:
            dict: Resultado da operação em lote
        """
        from app import db
        
        resultado = {
            'sucessos': 0,
            'erros': 0,
            'detalhes': []
        }
        
        try:
            for item in dados_lote:
                numero_cte = item.get('numero_cte')
                if not numero_cte:
                    resultado['erros'] += 1
                    resultado['detalhes'].append(f"CTE sem número: {item}")
                    continue
                
                cte = cls.query.filter_by(numero_cte=numero_cte).first()
                if not cte:
                    resultado['erros'] += 1
                    resultado['detalhes'].append(f"CTE {numero_cte} não encontrado")
                    continue
                
                if cte.atualizar(item):
                    resultado['sucessos'] += 1
                else:
                    resultado['erros'] += 1
                    resultado['detalhes'].append(f"Erro ao atualizar CTE {numero_cte}")
            
            # Commit das alterações
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            resultado['erro_geral'] = str(e)
        
        return resultado
    @classmethod
    def _normalize_payload(cls, dados: Dict) -> Dict:
        """Normaliza dicionário (tipos corretos) antes de inserir/alterar."""
        payload = {}

        if 'numero_cte' in dados:
            payload['numero_cte'] = _to_int_safe(dados.get('numero_cte'))

        if 'destinatario_nome' in dados:
            payload['destinatario_nome'] = _to_str_safe(dados.get('destinatario_nome'))

        if 'veiculo_placa' in dados:
            payload['veiculo_placa'] = _to_str_safe(dados.get('veiculo_placa'))

        if 'valor_total' in dados:
            v = _to_float_safe(dados.get('valor_total'))
            payload['valor_total'] = v if v is not None else None

        # datas
        for campo in (
            'data_emissao', 'data_baixa', 'data_inclusao_fatura', 'data_envio_processo',
            'primeiro_envio', 'data_rq_tmc', 'data_atesto', 'envio_final'
        ):
            if campo in dados:
                payload[campo] = _to_date_safe(dados.get(campo))

        if 'numero_fatura' in dados:
            payload['numero_fatura'] = _to_str_safe(dados.get('numero_fatura'))

        if 'observacao' in dados:
            payload['observacao'] = _to_str_safe(dados.get('observacao'))

        if 'origem_dados' in dados:
            payload['origem_dados'] = _to_str_safe(dados.get('origem_dados'))

        return payload


# =============================================================================
# Funções auxiliares pós-importação (opcionais)
# =============================================================================

def otimizar_banco_para_importacao() -> bool:
    """Otimiza configurações do banco para importação"""
    try:
        db.session.execute(text("SET work_mem = '256MB'"))
        db.session.execute(text("SET autovacuum = off"))
        db.session.execute(text("SET checkpoint_completion_target = 0.9"))
        db.session.commit()
        return True
    except Exception as e:
        logging.error(f"Erro ao otimizar banco: {e}")
        return False

def restaurar_configuracao_banco() -> bool:
    """Restaura configurações padrão do banco"""
    try:
        db.session.execute(text("SET work_mem = DEFAULT"))
        db.session.execute(text("SET autovacuum = DEFAULT"))
        db.session.execute(text("SET checkpoint_completion_target = DEFAULT"))
        db.session.execute(text("VACUUM ANALYZE dashboard_baker"))
        db.session.commit()
        return True
    except Exception as e:
        logging.error(f"Erro ao restaurar configurações: {e}")
        return False

def validar_integridade_pos_importacao() -> Dict:
    """Valida integridade dos dados após importação"""
    try:
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total_registros,
                COUNT(CASE WHEN numero_cte IS NULL THEN 1 END) as ctes_sem_numero,
                COUNT(CASE WHEN destinatario_nome IS NULL OR destinatario_nome = '' THEN 1 END) as ctes_sem_destinatario,
                COUNT(CASE WHEN valor_total < 0 THEN 1 END) as valores_negativos,
                COUNT(CASE WHEN valor_total > 1000000 THEN 1 END) as valores_altos,
                COUNT(DISTINCT numero_cte) as ctes_unicos,
                MIN(numero_cte) as menor_cte,
                MAX(numero_cte) as maior_cte,
                SUM(valor_total) as valor_total
            FROM dashboard_baker
        """)).fetchone()

        duplicatas = db.session.execute(text("""
            SELECT numero_cte, COUNT(*) as quantidade 
            FROM dashboard_baker 
            GROUP BY numero_cte 
            HAVING COUNT(*) > 1
        """)).fetchall()

        return {
            'validacao_ok': (result[1] == 0 and result[2] == 0 and result[3] == 0 and len(duplicatas) == 0),
            'total_registros': result[0],
            'ctes_sem_numero': result[1],
            'ctes_sem_destinatario': result[2],
            'valores_negativos': result[3],
            'valores_altos': result[4],
            'ctes_unicos': result[5],
            'faixa_numeros': f"{result[6]} a {result[7]}" if result[6] and result[7] else "N/A",
            'valor_total': float(result[8] or 0),
            'duplicatas': len(duplicatas),
            'detalhes_duplicatas': [{'numero_cte': d[0], 'quantidade': d[1]} for d in duplicatas]
        }
    except Exception as e:
        logging.error(f"Erro na validação de integridade: {e}")
        return {'erro': str(e)}

# -----------------------------------------------------------------------------
# Templates CSV - FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------

def gerar_template_csv_importacao() -> str:
    """Template para importação (novos)."""
    template_data = {
        'numero_cte': [12345, 12346, 12347],
        'destinatario_nome': ['Cliente Exemplo Ltda', 'Empresa ABC S/A', 'Transportadora XYZ'],
        'valor_total': [1500.50, 2750.00, 850.75],
        'data_emissao': ['01/01/2025', '02/01/2025', '03/01/2025'],
        'veiculo_placa': ['ABC1234', 'XYZ5678', 'DEF9012'],
        'numero_fatura': ['NF001', 'NF002', ''],
        'data_baixa': ['', '', '15/01/2025'],
        'observacao': ['Primeira importação', 'Dados migrados', 'Cliente prioritário'],
        'data_inclusao_fatura': ['02/01/2025', '03/01/2025', '04/01/2025'],
        'data_envio_processo': ['03/01/2025', '04/01/2025', '05/01/2025'],
        'primeiro_envio': ['04/01/2025', '05/01/2025', '06/01/2025'],
        'data_rq_tmc': ['05/01/2025', '06/01/2025', '07/01/2025'],
        'data_atesto': ['06/01/2025', '', '08/01/2025'],
        'envio_final': ['07/01/2025', '', '09/01/2025']
    }
    df = pd.DataFrame(template_data)
    return df.to_csv(sep=';', index=False, encoding='utf-8-sig')

def gerar_template_csv_atualizacao() -> str:
    """
    Template para ATUALIZAÇÃO — inclui **todos** os campos
    """
    return CTE.gerar_template_csv_atualizacao()