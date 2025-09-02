#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico Completo do Sistema CTEs
diagnostico_sistema.py - PARA IDENTIFICAR E CORRIGIR PROBLEMAS
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiagnosticoSistema:
    """Classe para diagnóstico completo do sistema CTEs"""
    
    def __init__(self):
        self.resultados = {
            'timestamp': datetime.now().isoformat(),
            'testes': {},
            'problemas_encontrados': [],
            'solucoes_sugeridas': [],
            'resumo': {}
        }
    
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Executa todos os testes de diagnóstico"""
        print("🔍 INICIANDO DIAGNÓSTICO COMPLETO DO SISTEMA CTEs")
        print("=" * 60)
        
        # Testes de infraestrutura
        self._testar_ambiente()
        self._testar_banco_dados()
        self._testar_modelo_cte()
        
        # Testes de dados
        self._testar_dados_existentes()
        self._testar_formatacao_datas()
        self._testar_serializacao()
        
        # Testes de API
        self._testar_rotas_api()
        
        # Gerar resumo
        self._gerar_resumo()
        
        return self.resultados
    
    def _testar_ambiente(self):
        """Testa configuração do ambiente"""
        print("🔧 Testando ambiente Flask...")
        
        try:
            # Tentar importar componentes básicos
            from flask import Flask
            from flask_sqlalchemy import SQLAlchemy
            from flask_login import LoginManager
            
            self.resultados['testes']['ambiente_flask'] = {
                'status': 'OK',
                'flask_disponivel': True,
                'sqlalchemy_disponivel': True,
                'login_manager_disponivel': True
            }
            print("✅ Ambiente Flask OK")
            
        except ImportError as e:
            self.resultados['testes']['ambiente_flask'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            self.resultados['problemas_encontrados'].append(
                f"Problema no ambiente Flask: {e}"
            )
            print(f"❌ Erro no ambiente Flask: {e}")
    
    def _testar_banco_dados(self):
        """Testa conexão com banco de dados"""
        print("🗄️  Testando banco de dados...")
        
        try:
            # Tentar importar e testar conexão
            from app import db
            from sqlalchemy import text
            
            # Teste de conexão básico
            result = db.session.execute(text("SELECT 1")).fetchone()
            
            if result:
                # Testar tabela dashboard_baker
                try:
                    count_result = db.session.execute(
                        text("SELECT COUNT(*) as total FROM dashboard_baker")
                    ).fetchone()
                    total_registros = count_result[0] if count_result else 0
                    
                    self.resultados['testes']['banco_dados'] = {
                        'status': 'OK',
                        'conexao': True,
                        'tabela_dashboard_baker': True,
                        'total_registros': total_registros
                    }
                    print(f"✅ Banco OK - {total_registros} registros encontrados")
                    
                except Exception as table_error:
                    self.resultados['testes']['banco_dados'] = {
                        'status': 'ERRO',
                        'conexao': True,
                        'tabela_dashboard_baker': False,
                        'erro_tabela': str(table_error)
                    }
                    self.resultados['problemas_encontrados'].append(
                        f"Tabela dashboard_baker não encontrada: {table_error}"
                    )
                    print(f"❌ Erro na tabela: {table_error}")
            
        except Exception as e:
            self.resultados['testes']['banco_dados'] = {
                'status': 'ERRO',
                'conexao': False,
                'erro': str(e)
            }
            self.resultados['problemas_encontrados'].append(
                f"Erro na conexão com banco: {e}"
            )
            print(f"❌ Erro no banco: {e}")
    
    def _testar_modelo_cte(self):
        """Testa modelo CTE"""
        print("📋 Testando modelo CTE...")
        
        try:
            from app.models.cte import CTE
            
            # Testar importação
            total_ctes = CTE.query.count()
            
            # Testar métodos do modelo
            if total_ctes > 0:
                primeiro_cte = CTE.query.first()
                
                # Testar serialização
                try:
                    dict_resultado = primeiro_cte.to_dict()
                    serializacao_ok = True
                    erro_serializacao = None
                except Exception as e:
                    serializacao_ok = False
                    erro_serializacao = str(e)
                
                # Testar propriedades
                try:
                    has_baixa = primeiro_cte.has_baixa
                    status_processo = primeiro_cte.status_processo
                    propriedades_ok = True
                except Exception as e:
                    propriedades_ok = False
                    erro_propriedades = str(e)
                
                self.resultados['testes']['modelo_cte'] = {
                    'status': 'OK' if serializacao_ok and propriedades_ok else 'PROBLEMA',
                    'modelo_importado': True,
                    'total_ctes': total_ctes,
                    'serializacao_ok': serializacao_ok,
                    'propriedades_ok': propriedades_ok,
                    'erro_serializacao': erro_serializacao,
                    'primeiro_cte_numero': getattr(primeiro_cte, 'numero_cte', None)
                }
                
                if not serializacao_ok:
                    self.resultados['problemas_encontrados'].append(
                        f"Problema na serialização do CTE: {erro_serializacao}"
                    )
                    self.resultados['solucoes_sugeridas'].append(
                        "Aplicar correções no método to_dict() do modelo CTE"
                    )
                
                print(f"✅ Modelo CTE OK - {total_ctes} CTEs no banco")
            else:
                self.resultados['testes']['modelo_cte'] = {
                    'status': 'AVISO',
                    'modelo_importado': True,
                    'total_ctes': 0,
                    'problema': 'Nenhum CTE encontrado no banco'
                }
                print("⚠️ Modelo CTE OK, mas nenhum registro encontrado")
                
        except Exception as e:
            self.resultados['testes']['modelo_cte'] = {
                'status': 'ERRO',
                'modelo_importado': False,
                'erro': str(e)
            }
            self.resultados['problemas_encontrados'].append(
                f"Erro no modelo CTE: {e}"
            )
            print(f"❌ Erro no modelo CTE: {e}")
    
    def _testar_dados_existentes(self):
        """Testa qualidade dos dados existentes"""
        print("📊 Testando qualidade dos dados...")
        
        try:
            from app.models.cte import CTE
            from sqlalchemy import func
            
            # Estatísticas básicas
            total = CTE.query.count()
            com_valor = CTE.query.filter(CTE.valor_total > 0).count()
            com_data_emissao = CTE.query.filter(CTE.data_emissao.isnot(None)).count()
            com_destinatario = CTE.query.filter(CTE.destinatario_nome.isnot(None)).count()
            
            # Dados problemáticos
            valores_zero = total - com_valor
            sem_data_emissao = total - com_data_emissao
            sem_destinatario = total - com_destinatario
            
            self.resultados['testes']['qualidade_dados'] = {
                'status': 'OK',
                'total_ctes': total,
                'com_valor': com_valor,
                'com_data_emissao': com_data_emissao,
                'com_destinatario': com_destinatario,
                'problemas': {
                    'valores_zero': valores_zero,
                    'sem_data_emissao': sem_data_emissao,
                    'sem_destinatario': sem_destinatario
                },
                'percentual_completos': round((min(com_valor, com_data_emissao, com_destinatario) / total * 100) if total > 0 else 0, 1)
            }
            
            if valores_zero > 0 or sem_data_emissao > 0:
                self.resultados['problemas_encontrados'].append(
                    f"Dados incompletos: {valores_zero} sem valor, {sem_data_emissao} sem data"
                )
            
            print(f"✅ Qualidade dos dados: {self.resultados['testes']['qualidade_dados']['percentual_completos']}% completos")
            
        except Exception as e:
            self.resultados['testes']['qualidade_dados'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            print(f"❌ Erro na análise de dados: {e}")
    
    def _testar_formatacao_datas(self):
        """Testa formatação de datas"""
        print("📅 Testando formatação de datas...")
        
        try:
            from app.models.cte import CTE
            
            # Buscar alguns CTEs com datas
            ctes_com_data = CTE.query.filter(CTE.data_emissao.isnot(None)).limit(5).all()
            
            datas_testadas = []
            problemas_data = []
            
            for cte in ctes_com_data:
                try:
                    # Testar conversão da data
                    data_str = cte.data_emissao.strftime('%Y-%m-%d') if cte.data_emissao else None
                    data_br = cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else None
                    
                    datas_testadas.append({
                        'cte': cte.numero_cte,
                        'data_original': str(cte.data_emissao),
                        'data_iso': data_str,
                        'data_br': data_br,
                        'ok': True
                    })
                    
                except Exception as e:
                    problemas_data.append({
                        'cte': getattr(cte, 'numero_cte', '?'),
                        'erro': str(e)
                    })
            
            self.resultados['testes']['formatacao_datas'] = {
                'status': 'OK' if not problemas_data else 'PROBLEMA',
                'datas_testadas': len(datas_testadas),
                'problemas_encontrados': len(problemas_data),
                'exemplos_ok': datas_testadas[:3],
                'problemas': problemas_data
            }
            
            if problemas_data:
                self.resultados['problemas_encontrados'].append(
                    f"Problemas na formatação de datas: {len(problemas_data)} casos"
                )
                self.resultados['solucoes_sugeridas'].append(
                    "Aplicar parser de datas melhorado (date_utils.py)"
                )
            
            print(f"✅ Formatação de datas: {len(datas_testadas)} OK, {len(problemas_data)} problemas")
            
        except Exception as e:
            self.resultados['testes']['formatacao_datas'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            print(f"❌ Erro no teste de datas: {e}")
    
    def _testar_serializacao(self):
        """Testa serialização de CTEs para JSON"""
        print("🔄 Testando serialização JSON...")
        
        try:
            from app.models.cte import CTE
            import json
            
            # Buscar alguns CTEs para testar
            ctes_teste = CTE.query.limit(10).all()
            
            sucessos = 0
            falhas = 0
            detalhes_falhas = []
            
            for cte in ctes_teste:
                try:
                    # Testar to_dict
                    dict_result = cte.to_dict()
                    
                    # Testar JSON serialization
                    json_str = json.dumps(dict_result)
                    
                    sucessos += 1
                    
                except Exception as e:
                    falhas += 1
                    detalhes_falhas.append({
                        'cte': getattr(cte, 'numero_cte', '?'),
                        'erro': str(e)
                    })
            
            self.resultados['testes']['serializacao'] = {
                'status': 'OK' if falhas == 0 else 'PROBLEMA',
                'ctes_testados': len(ctes_teste),
                'sucessos': sucessos,
                'falhas': falhas,
                'percentual_sucesso': round((sucessos / len(ctes_teste) * 100) if ctes_teste else 0, 1),
                'detalhes_falhas': detalhes_falhas[:5]  # Mostrar só os primeiros 5
            }
            
            if falhas > 0:
                self.resultados['problemas_encontrados'].append(
                    f"Falhas na serialização: {falhas}/{len(ctes_teste)} CTEs"
                )
                self.resultados['solucoes_sugeridas'].append(
                    "Aplicar modelo CTE corrigido com serialização robusta"
                )
            
            print(f"✅ Serialização: {sucessos}/{len(ctes_teste)} OK ({self.resultados['testes']['serializacao']['percentual_sucesso']}%)")
            
        except Exception as e:
            self.resultados['testes']['serializacao'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            print(f"❌ Erro no teste de serialização: {e}")
    
    def _testar_rotas_api(self):
        """Testa rotas da API"""
        print("🌐 Testando rotas da API...")
        
        try:
            from app.routes.ctes import bp as ctes_bp
            
            # Listar rotas do blueprint
            rotas_encontradas = []
            for rule in ctes_bp.url_map.iter_rules():
                if rule.endpoint.startswith('ctes.'):
                    rotas_encontradas.append({
                        'endpoint': rule.endpoint,
                        'rule': str(rule.rule),
                        'methods': list(rule.methods)
                    })
            
            # Verificar rotas importantes
            rotas_importantes = [
                'ctes.api_listar',
                'ctes.api_test_conexao',
                'ctes.api_buscar_cte'
            ]
            
            rotas_ok = []
            rotas_faltando = []
            
            endpoints_encontrados = [r['endpoint'] for r in rotas_encontradas]
            
            for rota in rotas_importantes:
                if rota in endpoints_encontrados:
                    rotas_ok.append(rota)
                else:
                    rotas_faltando.append(rota)
            
            self.resultados['testes']['rotas_api'] = {
                'status': 'OK' if not rotas_faltando else 'PROBLEMA',
                'total_rotas': len(rotas_encontradas),
                'rotas_importantes_ok': rotas_ok,
                'rotas_faltando': rotas_faltando,
                'todas_rotas': rotas_encontradas
            }
            
            if rotas_faltando:
                self.resultados['problemas_encontrados'].append(
                    f"Rotas importantes faltando: {', '.join(rotas_faltando)}"
                )
                self.resultados['solucoes_sugeridas'].append(
                    "Aplicar correções nas rotas da API (ctes.py)"
                )
            
            print(f"✅ Rotas API: {len(rotas_ok)}/{len(rotas_importantes)} importantes OK")
            
        except Exception as e:
            self.resultados['testes']['rotas_api'] = {
                'status': 'ERRO',
                'erro': str(e)
            }
            print(f"❌ Erro no teste de rotas: {e}")
    
    def _gerar_resumo(self):
        """Gera resumo do diagnóstico"""
        print("\n" + "=" * 60)
        print("📋 RESUMO DO DIAGNÓSTICO")
        print("=" * 60)
        
        testes_ok = 0
        testes_problema = 0
        testes_erro = 0
        
        for nome_teste, resultado in self.resultados['testes'].items():
            status = resultado.get('status', 'DESCONHECIDO')
            if status == 'OK':
                testes_ok += 1
                print(f"✅ {nome_teste.replace('_', ' ').title()}: OK")
            elif status == 'PROBLEMA' or status == 'AVISO':
                testes_problema += 1
                print(f"⚠️ {nome_teste.replace('_', ' ').title()}: PROBLEMA")
            else:
                testes_erro += 1
                print(f"❌ {nome_teste.replace('_', ' ').title()}: ERRO")
        
        self.resultados['resumo'] = {
            'testes_realizados': len(self.resultados['testes']),
            'testes_ok': testes_ok,
            'testes_problema': testes_problema,
            'testes_erro': testes_erro,
            'problemas_encontrados': len(self.resultados['problemas_encontrados']),
            'solucoes_sugeridas': len(self.resultados['solucoes_sugeridas'])
        }
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • {testes_ok} testes OK")
        print(f"   • {testes_problema} testes com problemas")  
        print(f"   • {testes_erro} testes com erro")
        print(f"   • {len(self.resultados['problemas_encontrados'])} problemas identificados")
        print(f"   • {len(self.resultados['solucoes_sugeridas'])} soluções sugeridas")
        
        if self.resultados['problemas_encontrados']:
            print(f"\n🚨 PROBLEMAS PRINCIPAIS:")
            for i, problema in enumerate(self.resultados['problemas_encontrados'][:5], 1):
                print(f"   {i}. {problema}")
        
        if self.resultados['solucoes_sugeridas']:
            print(f"\n💡 SOLUÇÕES RECOMENDADAS:")
            for i, solucao in enumerate(self.resultados['solucoes_sugeridas'][:5], 1):
                print(f"   {i}. {solucao}")
        
        print("\n" + "=" * 60)

def executar_diagnostico():
    """Função principal para executar o diagnóstico"""
    try:
        diagnostico = DiagnosticoSistema()
        resultados = diagnostico.executar_diagnostico_completo()
        
        # Salvar resultados em arquivo
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'diagnostico_ctes_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Relatório salvo em: {filename}")
        
        return resultados
        
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO no diagnóstico: {e}")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("🏥 DIAGNÓSTICO DO SISTEMA CTEs")
    print("Verificando problemas de carregamento da lista...")
    print()
    
    resultados = executar_diagnostico()
    
    if resultados and resultados['resumo']['testes_ok'] >= resultados['resumo']['testes_realizados'] // 2:
        print("\n🎉 DIAGNÓSTICO CONCLUÍDO COM SUCESSO")
        print("O sistema parece estar funcionando. Verifique os detalhes do relatório.")
    else:
        print("\n⚠️ PROBLEMAS IDENTIFICADOS NO SISTEMA")
        print("Aplicar as correções sugeridas nos artefatos fornecidos.")