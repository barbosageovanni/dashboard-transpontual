from app import db
from datetime import datetime
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from decimal import Decimal
import logging

class CTE(db.Model):
    """Modelo para CTEs - Usando tabela existente"""
    __tablename__ = 'dashboard_baker'  # Nome da tabela existente

    id = db.Column(db.Integer, primary_key=True)
    numero_cte = db.Column(db.Integer, unique=True, nullable=False, index=True)
    
    # Dados principais
    destinatario_nome = db.Column(db.String(255))
    veiculo_placa = db.Column(db.String(20))
    valor_total = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    
    # Datas principais
    data_emissao = db.Column(db.Date)
    data_baixa = db.Column(db.Date)
    
    # Informações de faturamento
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

    def __repr__(self):
        return f'<CTE {self.numero_cte}>'

    @property
    def has_baixa(self):
        """Verifica se tem baixa"""
        return self.data_baixa is not None

    @property
    def processo_completo(self):
        """Verifica se o processo está completo - VERSÃO CORRIGIDA"""
        # Verificar se todas as datas principais estão preenchidas
        datas_obrigatorias = [
            self.data_emissao,
            self.primeiro_envio, 
            self.data_atesto,
            self.envio_final
        ]
        
        # Debug: imprimir para identificar o problema
        print(f"🔍 Debug CTE {self.numero_cte}:")
        print(f"  - Data Emissão: {self.data_emissao}")
        print(f"  - Primeiro Envio: {self.primeiro_envio}")
        print(f"  - Data Atesto: {self.data_atesto}")
        print(f"  - Envio Final: {self.envio_final}")
        
        # Verificar se TODAS as datas estão preenchidas E não são None
        completo = all(data is not None for data in datas_obrigatorias)
        
        print(f"  - Processo Completo: {completo}")
        
        return completo

    @property
    def status_processo(self):
        """Status do processo - VERSÃO CORRIGIDA COM MAIS DETALHES"""
        if self.processo_completo:
            if self.data_baixa:
                return 'Finalizado'  # Completo + Baixado
            else:
                return 'Completo'    # Completo mas sem baixa
        elif self.envio_final:
            return 'Envio Final'
        elif self.data_atesto:
            return 'Atestado'
        elif self.primeiro_envio:
            return 'Enviado'
        elif self.data_emissao:
            return 'Emitido'
        else:
            return 'Pendente'

    def to_dict(self):
        """Converte para dicionário - VERSÃO COM DEBUG"""
        try:
            # Calcular processo completo com debug
            processo_completo = self.processo_completo
            
            return {
                'id': self.id,
                'numero_cte': self.numero_cte,
                'destinatario_nome': self.destinatario_nome or '',
                'veiculo_placa': self.veiculo_placa or '',
                'valor_total': float(self.valor_total) if self.valor_total else 0.0,
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
                'processo_completo': processo_completo,
                'status_processo': self.status_processo,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                # Debug info
                'debug_datas': {
                    'data_emissao': self.data_emissao is not None,
                    'primeiro_envio': self.primeiro_envio is not None,
                    'data_atesto': self.data_atesto is not None,
                    'envio_final': self.envio_final is not None
                }
            }
        except Exception as e:
            print(f"Erro em to_dict para CTE {self.numero_cte}: {e}")
            return {
                'numero_cte': self.numero_cte,
                'destinatario_nome': str(self.destinatario_nome or ''),
                'valor_total': 0.0,
                'data_emissao': None,
                'has_baixa': False,
                'processo_completo': False,
                'status_processo': 'Erro'
            }

    @classmethod
    def criar_cte(cls, dados):
        """Cria um novo CTE"""
        try:
            # Processar datas que vêm como string
            dados_processados = dados.copy()
            
            # Campos de data para conversão
            campos_data = [
                'data_emissao', 'data_baixa', 'data_inclusao_fatura',
                'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                'data_atesto', 'envio_final'
            ]
            
            for campo in campos_data:
                if campo in dados_processados and dados_processados[campo]:
                    try:
                        if isinstance(dados_processados[campo], str):
                            dados_processados[campo] = datetime.strptime(dados_processados[campo], '%Y-%m-%d').date()
                    except ValueError:
                        dados_processados[campo] = None
            
            cte = cls(**dados_processados)
            db.session.add(cte)
            db.session.commit()
            return True, cte
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @classmethod
    def buscar_por_numero(cls, numero_cte):
        """Busca CTE por número"""
        return cls.query.filter_by(numero_cte=numero_cte).first()

    def atualizar(self, dados):
        """Atualiza dados do CTE"""
        try:
            # Processar datas que vêm como string
            dados_processados = dados.copy()
            
            # Campos de data para conversão
            campos_data = [
                'data_emissao', 'data_baixa', 'data_inclusao_fatura',
                'data_envio_processo', 'primeiro_envio', 'data_rq_tmc',
                'data_atesto', 'envio_final'
            ]
            
            for campo in campos_data:
                if campo in dados_processados and dados_processados[campo]:
                    try:
                        if isinstance(dados_processados[campo], str):
                            dados_processados[campo] = datetime.strptime(dados_processados[campo], '%Y-%m-%d').date()
                    except ValueError:
                        dados_processados[campo] = None
            
            for chave, valor in dados_processados.items():
                if hasattr(self, chave):
                    setattr(self, chave, valor)
            
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True, "CTE atualizado com sucesso"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def registrar_baixa(self, data_baixa, observacao=""):
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
            return False, str(e)

    # ============================================================================
    # MÉTODOS PARA IMPORTAÇÃO EM LOTE
    # ============================================================================

    @classmethod
    def obter_ctes_existentes_bulk(cls, numeros_cte: List[int]) -> set:
        """
        Obtém CTEs existentes em lote para verificação rápida
        
        Args:
            numeros_cte: Lista de números de CTE para verificar
            
        Returns:
            set: Conjunto de números de CTE que já existem
        """
        try:
            if not numeros_cte:
                return set()
            
            # Query otimizada com IN
            result = db.session.query(cls.numero_cte).filter(
                cls.numero_cte.in_(numeros_cte)
            ).all()
            
            return set(row[0] for row in result)
            
        except Exception as e:
            logging.error(f"Erro ao obter CTEs existentes: {str(e)}")
            return set()

    @classmethod
    def criar_cte_otimizado(cls, dados: Dict) -> Tuple[bool, Union[str, 'CTE']]:
        """
        Versão otimizada do método criar_cte para importação em lote
        🔧 CORRIGIDO: Tratamento seguro de valores None
        """
        try:
            # Validações básicas otimizadas - CORRIGIDAS
            if not dados.get('numero_cte') or dados['numero_cte'] <= 0:
                return False, "Número do CTE inválido"
            
            # 🔧 CORREÇÃO: Tratamento seguro do destinatário
            destinatario_nome = dados.get('destinatario_nome')
            if not destinatario_nome or not str(destinatario_nome).strip():
                return False, "Nome do destinatário é obrigatório"
            
            # 🔧 CORREÇÃO: Validação segura do valor
            valor_total = dados.get('valor_total')
            if not isinstance(valor_total, (int, float, Decimal)) or valor_total < 0:
                return False, "Valor total inválido"
            
            # Verificar duplicata (otimizado)
            existe = cls.query.filter_by(numero_cte=dados['numero_cte']).first()
            if existe:
                return False, f"CTE {dados['numero_cte']} já existe"
            
            # 🔧 FUNÇÃO HELPER PARA LIMPEZA SEGURA
            def limpar_texto(valor):
                """Limpa texto de forma segura"""
                if valor is None:
                    return None
                texto = str(valor).strip()
                return texto if texto else None
            
            # Criar instância com valores limpos
            cte = cls(
                numero_cte=dados['numero_cte'],
                destinatario_nome=str(destinatario_nome).strip(),
                veiculo_placa=limpar_texto(dados.get('veiculo_placa')),
                valor_total=float(valor_total),
                data_emissao=dados.get('data_emissao'),
                numero_fatura=limpar_texto(dados.get('numero_fatura')),
                data_baixa=dados.get('data_baixa'),
                observacao=limpar_texto(dados.get('observacao')),
                data_inclusao_fatura=dados.get('data_inclusao_fatura'),
                data_envio_processo=dados.get('data_envio_processo'),
                primeiro_envio=dados.get('primeiro_envio'),
                data_rq_tmc=dados.get('data_rq_tmc'),
                data_atesto=dados.get('data_atesto'),
                envio_final=dados.get('envio_final'),
                origem_dados=dados.get('origem_dados', 'Sistema')
            )
            
            # Salvar
            db.session.add(cte)
            db.session.flush()  # Para pegar o ID sem commit
            
            return True, cte
            
        except IntegrityError as e:
            db.session.rollback()
            if 'numero_cte' in str(e):
                return False, f"CTE {dados['numero_cte']} já existe no banco"
            return False, f"Erro de integridade: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao criar CTE: {str(e)}"

    @classmethod
    def criar_ctes_lote(cls, lista_dados: List[Dict], batch_size: int = 500) -> Dict:
        """
        Cria múltiplos CTEs em lotes otimizados
        
        Args:
            lista_dados: Lista de dicionários com dados dos CTEs
            batch_size: Tamanho do lote para commit
            
        Returns:
            Dict: Resultado da operação com estatísticas
        """
        resultado = {
            'processados': 0,
            'sucessos': 0,
            'erros': 0,
            'ctes_existentes': 0,
            'detalhes': [],
            'tempo_inicio': datetime.now()
        }
        
        try:
            total_ctes = len(lista_dados)
            
            # Primeiro, identificar CTEs que já existem
            numeros_cte = [dados['numero_cte'] for dados in lista_dados]
            ctes_existentes = cls.obter_ctes_existentes_bulk(numeros_cte)
            resultado['ctes_existentes'] = len(ctes_existentes)
            
            # Filtrar apenas CTEs novos
            lista_novos = [dados for dados in lista_dados if dados['numero_cte'] not in ctes_existentes]
            
            # Processar em lotes
            for i in range(0, len(lista_novos), batch_size):
                batch = lista_novos[i:i+batch_size]
                
                try:
                    # Processar lote
                    for dados in batch:
                        resultado['processados'] += 1
                        
                        sucesso, cte_ou_erro = cls.criar_cte_otimizado(dados)
                        
                        if sucesso:
                            resultado['sucessos'] += 1
                            resultado['detalhes'].append({
                                'cte': dados['numero_cte'],
                                'sucesso': True,
                                'mensagem': 'CTE criado com sucesso'
                            })
                        else:
                            resultado['erros'] += 1
                            resultado['detalhes'].append({
                                'cte': dados.get('numero_cte', 'N/A'),
                                'sucesso': False,
                                'mensagem': str(cte_ou_erro)
                            })
                    
                    # Commit do lote
                    db.session.commit()
                    
                except Exception as e:
                    # Rollback do lote em caso de erro
                    db.session.rollback()
                    
                    # Marcar todos do lote como erro
                    for dados in batch:
                        if not any(d['cte'] == dados.get('numero_cte') for d in resultado['detalhes']):
                            resultado['erros'] += 1
                            resultado['detalhes'].append({
                                'cte': dados.get('numero_cte', 'N/A'),
                                'sucesso': False,
                                'mensagem': f'Erro no lote: {str(e)}'
                            })
            
            # Adicionar CTEs existentes aos detalhes
            for numero_cte in ctes_existentes:
                resultado['detalhes'].append({
                    'cte': numero_cte,
                    'sucesso': False,
                    'mensagem': 'CTE já existe no banco'
                })
            
            resultado['tempo_fim'] = datetime.now()
            resultado['duracao'] = (resultado['tempo_fim'] - resultado['tempo_inicio']).total_seconds()
            
            return resultado
            
        except Exception as e:
            resultado['erro_geral'] = str(e)
            logging.error(f"Erro geral na criação em lote: {str(e)}")
            return resultado

    @classmethod
    def validar_dados_importacao(cls, dados: Dict) -> Tuple[bool, List[str]]:
        """
        Validação específica para dados de importação
        🔧 CORRIGIDA: Tratamento seguro de valores None
        """
        erros = []
        
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
        
        # 🔧 CORREÇÃO: Validação segura do destinatário
        destinatario_validado = validar_texto(dados.get('destinatario_nome'), 'destinatario_nome', 3)
        if not destinatario_validado:
            erros.append("Nome do destinatário é obrigatório e deve ter pelo menos 3 caracteres")
        
        # 🔧 CORREÇÃO: Validação segura do valor
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
        veiculo_validado = validar_texto(dados.get('veiculo_placa'), 'veiculo_placa')
        if veiculo_validado and (len(veiculo_validado) < 7 or len(veiculo_validado) > 8):
            erros.append("Placa do veículo deve ter 7 ou 8 caracteres")
        
        fatura_validada = validar_texto(dados.get('numero_fatura'), 'numero_fatura')
        if fatura_validada and len(fatura_validada) > 50:
            erros.append("Número da fatura muito longo (máximo: 50 caracteres)")
        
        # Validações de datas (mantidas como estavam - já seguras)
        if dados.get('data_emissao') and isinstance(dados['data_emissao'], date):
            if dados['data_emissao'] > date.today():
                erros.append("Data de emissão não pode ser futura")
        
        if dados.get('data_baixa') and isinstance(dados['data_baixa'], date):
            if dados['data_baixa'] > date.today():
                erros.append("Data de baixa não pode ser futura")
        
        # Validação de coerência entre datas
        if (dados.get('data_emissao') and dados.get('data_baixa') and 
            isinstance(dados['data_emissao'], date) and isinstance(dados['data_baixa'], date)):
            if dados['data_baixa'] < dados['data_emissao']:
                erros.append("Data de baixa não pode ser anterior à data de emissão")
        
        return len(erros) == 0, erros

    @classmethod
    def processar_csv_importacao(cls, arquivo_path: str) -> Dict:
        """
        Processa arquivo CSV para importação completa
        
        Args:
            arquivo_path: Caminho para o arquivo CSV
            
        Returns:
            Dict: Resultado completo da importação
        """
        resultado = {
            'sucesso': False,
            'arquivo_processado': arquivo_path,
            'linhas_processadas': 0,
            'ctes_inseridos': 0,
            'ctes_existentes': 0,
            'erros': 0,
            'detalhes': [],
            'tempo_processamento': 0
        }
        
        inicio = datetime.now()
        
        try:
            # Ler CSV
            df = pd.read_csv(arquivo_path, sep=';', encoding='utf-8-sig')
            resultado['linhas_processadas'] = len(df)
            
            # Processar dados
            dados_processados = []
            for idx, row in df.iterrows():
                try:
                    dados = cls._processar_linha_csv(row)
                    if dados:
                        dados_processados.append(dados)
                except Exception as e:
                    resultado['erros'] += 1
                    resultado['detalhes'].append({
                        'linha': idx + 1,
                        'erro': str(e)
                    })
            
            # Importar em lote
            if dados_processados:
                resultado_lote = cls.criar_ctes_lote(dados_processados)
                resultado.update({
                    'ctes_inseridos': resultado_lote['sucessos'],
                    'ctes_existentes': resultado_lote['ctes_existentes'],
                    'erros': resultado['erros'] + resultado_lote['erros'],
                    'detalhes': resultado['detalhes'] + resultado_lote['detalhes']
                })
            
            resultado['tempo_processamento'] = (datetime.now() - inicio).total_seconds()
            resultado['sucesso'] = True
            
        except Exception as e:
            resultado['erro_geral'] = str(e)
            logging.error(f"Erro no processamento CSV: {str(e)}")
        
        return resultado

    @classmethod
    def _processar_linha_csv(cls, row) -> Optional[Dict]:
        """
        Processa uma linha do CSV - VERSÃO CORRIGIDA
        """
        try:
            # Função helper para conversão segura
            def converter_numero_cte(valor):
                """Converte número CTE de forma segura"""
                if pd.isna(valor) or valor is None:
                    return None
                try:
                    # Limpar e converter
                    if isinstance(valor, str):
                        valor = valor.strip()
                        if not valor:
                            return None
                    numero = int(float(valor))
                    return numero if numero > 0 else None
                except (ValueError, TypeError):
                    return None
            
            def converter_valor(valor):
                """Converte valor monetário de forma segura"""
                if pd.isna(valor) or valor is None:
                    return None
                try:
                    if isinstance(valor, str):
                        # Limpar formatação brasileira
                        valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        if not valor:
                            return None
                    valor_float = float(valor)
                    return valor_float if valor_float >= 0 else None
                except (ValueError, TypeError):
                    return None
            
            def converter_texto(valor):
                """Converte texto de forma segura"""
                if pd.isna(valor) or valor is None:
                    return None
                texto = str(valor).strip()
                return texto if texto else None
            
            # Campos obrigatórios com conversão segura
            numero_cte = converter_numero_cte(row.get('numero_cte'))
            if not numero_cte:
                return None
            
            destinatario_nome = converter_texto(row.get('destinatario_nome'))
            if not destinatario_nome or len(destinatario_nome) < 3:
                return None
            
            valor_total = converter_valor(row.get('valor_total'))
            if valor_total is None:
                return None
            
            # Processar datas (mantém função existente)
            def processar_data(valor):
                if pd.isna(valor) or not valor:
                    return None
                try:
                    return pd.to_datetime(valor, format='%d/%m/%Y').date()
                except:
                    try:
                        return pd.to_datetime(valor).date()
                    except:
                        return None
            
            # Montar dados finais
            dados = {
                'numero_cte': numero_cte,
                'destinatario_nome': destinatario_nome,
                'veiculo_placa': converter_texto(row.get('veiculo_placa')),
                'valor_total': valor_total,
                'data_emissao': processar_data(row.get('data_emissao')),
                'numero_fatura': converter_texto(row.get('numero_fatura')),
                'data_baixa': processar_data(row.get('data_baixa')),
                'observacao': converter_texto(row.get('observacao')),
                'data_inclusao_fatura': processar_data(row.get('data_inclusao_fatura')),
                'data_envio_processo': processar_data(row.get('data_envio_processo')),
                'primeiro_envio': processar_data(row.get('primeiro_envio')),
                'data_rq_tmc': processar_data(row.get('data_rq_tmc')),
                'data_atesto': processar_data(row.get('data_atesto')),
                'envio_final': processar_data(row.get('envio_final')),
                'origem_dados': 'Importação CSV'
            }
            
            # Validar dados antes de retornar
            valido, erros = cls.validar_dados_importacao(dados)
            if not valido:
                logging.warning(f"CTE {numero_cte} inválido: {erros}")
                return None
            
            return dados
            
        except Exception as e:
            logging.error(f"Erro ao processar linha CSV: {str(e)}")
            return None

    def to_dict_importacao(self) -> Dict:
        """
        Converte CTE para dicionário otimizado para importação/exportação
        
        Returns:
            Dict: Dados do CTE em formato de dicionário
        """
        try:
            return {
                'numero_cte': self.numero_cte,
                'destinatario_nome': self.destinatario_nome,
                'veiculo_placa': self.veiculo_placa,
                'valor_total': float(self.valor_total) if self.valor_total else 0.0,
                'data_emissao': self.data_emissao.strftime('%Y-%m-%d') if self.data_emissao else None,
                'numero_fatura': self.numero_fatura,
                'data_baixa': self.data_baixa.strftime('%Y-%m-%d') if self.data_baixa else None,
                'observacao': self.observacao,
                'data_inclusao_fatura': self.data_inclusao_fatura.strftime('%Y-%m-%d') if self.data_inclusao_fatura else None,
                'data_envio_processo': self.data_envio_processo.strftime('%Y-%m-%d') if self.data_envio_processo else None,
                'primeiro_envio': self.primeiro_envio.strftime('%Y-%m-%d') if self.primeiro_envio else None,
                'data_rq_tmc': self.data_rq_tmc.strftime('%Y-%m-%d') if self.data_rq_tmc else None,
                'data_atesto': self.data_atesto.strftime('%Y-%m-%d') if self.data_atesto else None,
                'envio_final': self.envio_final.strftime('%Y-%m-%d') if self.envio_final else None,
                'origem_dados': self.origem_dados,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
            }
        except Exception as e:
            logging.error(f"Erro ao converter CTE {self.numero_cte} para dict: {str(e)}")
            return {
                'numero_cte': self.numero_cte,
                'erro': str(e)
            }


# ============================================================================
# FUNÇÕES AUXILIARES FORA DA CLASSE
# ============================================================================

def otimizar_banco_para_importacao():
    """
    Aplica otimizações no banco para importação em lote
    Execute antes de importações grandes
    """
    try:
        # Aumentar work_mem temporariamente (PostgreSQL)
        db.session.execute(text("SET work_mem = '256MB'"))
        
        # Desabilitar autovacuum durante importação
        db.session.execute(text("SET autovacuum = off"))
        
        # Aumentar checkpoint_segments
        db.session.execute(text("SET checkpoint_completion_target = 0.9"))
        
        db.session.commit()
        return True
        
    except Exception as e:
        logging.error(f"Erro ao otimizar banco: {str(e)}")
        return False

def restaurar_configuracao_banco():
    """
    Restaura configurações padrão do banco após importação
    Execute após importações grandes
    """
    try:
        # Restaurar configurações padrão
        db.session.execute(text("SET work_mem = DEFAULT"))
        db.session.execute(text("SET autovacuum = DEFAULT"))
        db.session.execute(text("SET checkpoint_completion_target = DEFAULT"))
        
        # Executar vacuum para limpeza
        db.session.execute(text("VACUUM ANALYZE dashboard_baker"))
        
        db.session.commit()
        return True
        
    except Exception as e:
        logging.error(f"Erro ao restaurar configurações: {str(e)}")
        return False

def validar_integridade_pos_importacao() -> Dict:
    """
    Valida integridade dos dados após importação
    
    Returns:
        Dict: Resultado da validação
    """
    try:
        # Verificações de integridade
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
        
        # Verificar duplicatas
        duplicatas = db.session.execute(text("""
            SELECT numero_cte, COUNT(*) as quantidade 
            FROM dashboard_baker 
            GROUP BY numero_cte 
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        return {
            'validacao_ok': (result[1] == 0 and result[2] == 0 and result[3] == 0 and 
                            len(duplicatas) == 0),
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
        logging.error(f"Erro na validação de integridade: {str(e)}")
        return {'erro': str(e)}

def gerar_template_csv_importacao() -> str:
    """
    Gera template CSV para importação
    
    Returns:
        str: Conteúdo do CSV template
    """
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

# ============================================================================
# EXEMPLO DE USO
# ============================================================================

def exemplo_importacao_lote():
    """
    Exemplo de como usar o sistema de importação em lote
    """
    try:
        # 1. Otimizar banco
        otimizar_banco_para_importacao()
        
        # 2. Dados de exemplo
        dados_exemplo = [
            {
                'numero_cte': 50001,
                'destinatario_nome': 'Cliente Teste 1',
                'valor_total': 1500.00,
                'data_emissao': date(2025, 1, 15),
                'origem_dados': 'Importação Teste'
            },
            {
                'numero_cte': 50002,
                'destinatario_nome': 'Cliente Teste 2',
                'valor_total': 2750.50,
                'data_emissao': date(2025, 1, 16),
                'origem_dados': 'Importação Teste'
            }
        ]
        
        # 3. Importar
        resultado = CTE.criar_ctes_lote(dados_exemplo)
        
        print(f"✅ Importação concluída:")
        print(f"  - Processados: {resultado['processados']}")
        print(f"  - Sucessos: {resultado['sucessos']}")
        print(f"  - Erros: {resultado['erros']}")
        print(f"  - Duração: {resultado['duracao']:.2f}s")
        
        # 4. Validar integridade
        validacao = validar_integridade_pos_importacao()
        print(f"  - Validação OK: {validacao['validacao_ok']}")
        
        # 5. Restaurar configurações
        restaurar_configuracao_banco()
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro na importação: {str(e)}")
        restaurar_configuracao_banco()
        return None