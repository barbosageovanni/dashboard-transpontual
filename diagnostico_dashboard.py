#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico e Correção - Dashboard Financeiro
Salvar como: diagnostico_dashboard.py na raiz do projeto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.cte import CTE
from sqlalchemy import text, inspect
from datetime import datetime, timedelta
import logging

def diagnosticar_completo():
    """Diagnóstico completo do sistema para identificar problemas"""
    
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🔍 DIAGNÓSTICO COMPLETO - DASHBOARD FINANCEIRO")
        print("="*60)
        
        # 1. Verificar conexão com banco
        print("\n1️⃣ VERIFICANDO CONEXÃO COM BANCO DE DADOS...")
        try:
            db.session.execute(text('SELECT 1'))
            print("✅ Conexão com banco OK")
        except Exception as e:
            print(f"❌ ERRO na conexão: {e}")
            return False
        
        # 2. Verificar estrutura da tabela CTEs
        print("\n2️⃣ VERIFICANDO ESTRUTURA DA TABELA CTEs...")
        verificar_estrutura_tabela()
        
        # 3. Verificar dados existentes
        print("\n3️⃣ ANALISANDO DADOS EXISTENTES...")
        stats_dados = analisar_dados_existentes()
        
        # 4. Testar APIs
        print("\n4️⃣ TESTANDO APIs...")
        testar_apis()
        
        # 5. Verificar campos necessários para novas métricas
        print("\n5️⃣ VERIFICANDO CAMPOS PARA NOVAS MÉTRICAS...")
        verificar_campos_metricas()
        
        # 6. Gerar relatório final
        print("\n6️⃣ RELATÓRIO FINAL:")
        gerar_relatorio_final(stats_dados)
        
        return True

def verificar_estrutura_tabela():
    """Verifica se a tabela CTEs tem todos os campos necessários"""
    try:
        inspector = inspect(db.engine)
        columns = inspector.get_columns('ctes')
        
        campos_encontrados = [col['name'] for col in columns]
        print(f"✅ Tabela 'ctes' encontrada com {len(campos_encontrados)} campos")
        
        # Campos obrigatórios básicos
        campos_basicos = [
            'numero_cte', 'destinatario_nome', 'valor_total', 'data_emissao'
        ]
        
        # Campos para novas métricas
        campos_novos = [
            'envio_final', 'data_inclusao_fatura', 'data_rq_tmc', 'data_atesto'
        ]
        
        print("\n📋 Campos básicos:")
        for campo in campos_basicos:
            if campo in campos_encontrados:
                print(f"  ✅ {campo}")
            else:
                print(f"  ❌ {campo} - AUSENTE!")
        
        print("\n📋 Campos para novas métricas:")
        for campo in campos_novos:
            if campo in campos_encontrados:
                print(f"  ✅ {campo}")
            else:
                print(f"  ⚠️  {campo} - AUSENTE (precisa ser criado)")
        
        return campos_encontrados
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return []

def analisar_dados_existentes():
    """Analisa os dados existentes na tabela CTEs"""
    try:
        stats = {}
        
        # Total de registros
        total_ctes = CTE.query.count()
        stats['total_ctes'] = total_ctes
        print(f"📊 Total de CTEs: {total_ctes}")
        
        if total_ctes == 0:
            print("❌ PROBLEMA CRÍTICO: Nenhum CTE no banco!")
            return stats
        
        # CTEs com dados válidos
        ctes_com_valor = CTE.query.filter(
            CTE.valor_total.isnot(None), 
            CTE.valor_total > 0
        ).count()
        stats['ctes_com_valor'] = ctes_com_valor
        
        ctes_com_data = CTE.query.filter(CTE.data_emissao.isnot(None)).count()
        stats['ctes_com_data'] = ctes_com_data
        
        ctes_com_cliente = CTE.query.filter(
            CTE.destinatario_nome.isnot(None),
            CTE.destinatario_nome != ''
        ).count()
        stats['ctes_com_cliente'] = ctes_com_cliente
        
        print(f"💰 CTEs com valor válido: {ctes_com_valor} ({ctes_com_valor/total_ctes*100:.1f}%)")
        print(f"📅 CTEs com data emissão: {ctes_com_data} ({ctes_com_data/total_ctes*100:.1f}%)")
        print(f"👤 CTEs com cliente: {ctes_com_cliente} ({ctes_com_cliente/total_ctes*100:.1f}%)")
        
        # Período dos dados
        data_mais_antiga = db.session.query(db.func.min(CTE.data_emissao)).scalar()
        data_mais_recente = db.session.query(db.func.max(CTE.data_emissao)).scalar()
        
        if data_mais_antiga and data_mais_recente:
            stats['data_mais_antiga'] = data_mais_antiga
            stats['data_mais_recente'] = data_mais_recente
            print(f"📅 Período dos dados: {data_mais_antiga} até {data_mais_recente}")
        
        # CTEs nos últimos 180 dias
        data_limite = datetime.now().date() - timedelta(days=180)
        ctes_periodo = CTE.query.filter(CTE.data_emissao >= data_limite).count()
        stats['ctes_ultimos_180_dias'] = ctes_periodo
        
        print(f"📈 CTEs últimos 180 dias: {ctes_periodo}")
        
        if ctes_periodo == 0:
            print("❌ PROBLEMA: Nenhum CTE nos últimos 180 dias!")
            print("   Possível causa: Dados muito antigos ou filtro de data incorreto")
        
        # Estatísticas de valores
        resultado_valores = db.session.query(
            db.func.sum(CTE.valor_total).label('total'),
            db.func.avg(CTE.valor_total).label('media'),
            db.func.min(CTE.valor_total).label('minimo'),
            db.func.max(CTE.valor_total).label('maximo')
        ).filter(CTE.valor_total.isnot(None)).first()
        
        if resultado_valores:
            print(f"💵 Receita total: R$ {resultado_valores.total or 0:,.2f}")
            print(f"💵 Ticket médio: R$ {resultado_valores.media or 0:,.2f}")
            print(f"💵 Valor mínimo: R$ {resultado_valores.minimo or 0:,.2f}")
            print(f"💵 Valor máximo: R$ {resultado_valores.maximo or 0:,.2f}")
            
            stats.update({
                'receita_total': float(resultado_valores.total or 0),
                'ticket_medio': float(resultado_valores.media or 0),
                'valor_minimo': float(resultado_valores.minimo or 0),
                'valor_maximo': float(resultado_valores.maximo or 0)
            })
        
        return stats
        
    except Exception as e:
        print(f"❌ Erro na análise de dados: {e}")
        return {}

def verificar_campos_metricas():
    """Verifica se os campos necessários para as novas métricas existem"""
    try:
        # Tentar acessar campos das novas métricas
        campos_verificar = [
            ('envio_final', 'Receita Faturada'),
            ('data_inclusao_fatura', 'Receita com Faturas'),
            ('data_rq_tmc', 'Variação RQ/TMC → 1º Envio'),
            ('data_atesto', 'Variação 1º Envio → Atesto')
        ]
        
        campos_existem = []
        
        for campo, descricao in campos_verificar:
            try:
                # Tentar contar registros com este campo preenchido
                query = text(f"SELECT COUNT(*) FROM ctes WHERE {campo} IS NOT NULL")
                resultado = db.session.execute(query).scalar()
                
                print(f"✅ {campo} - {resultado} registros preenchidos ({descricao})")
                campos_existem.append((campo, resultado))
                
            except Exception as e:
                print(f"❌ {campo} - Campo não existe ({descricao})")
                print(f"   SQL para criar: ALTER TABLE ctes ADD COLUMN {campo} DATE;")
        
        if not campos_existem:
            print("\n⚠️  NENHUM campo das novas métricas encontrado!")
            print("   As métricas 'Receita Faturada' e 'Receita com Faturas' não funcionarão")
            print("   Soluções:")
            print("   1. Criar os campos na tabela")
            print("   2. Usar campos existentes como proxy (data_baixa, primeiro_envio)")
        
        return campos_existem
        
    except Exception as e:
        print(f"❌ Erro ao verificar campos: {e}")
        return []

def testar_apis():
    """Testa se as APIs estão funcionando"""
    try:
        from app.services.analise_financeira_service import AnaliseFinanceiraService
        
        print("📡 Testando AnaliseFinanceiraService...")
        
        # Testar análise completa
        resultado = AnaliseFinanceiraService.gerar_analise_completa(filtro_dias=30)
        
        if resultado:
            print("✅ AnaliseFinanceiraService.gerar_analise_completa() - OK")
            
            # Verificar estrutura do resultado
            campos_esperados = [
                'receita_mensal', 'ticket_medio', 'tempo_medio_cobranca',
                'concentracao_clientes', 'stress_test_receita', 'graficos'
            ]
            
            for campo in campos_esperados:
                if campo in resultado:
                    print(f"  ✅ {campo}")
                else:
                    print(f"  ❌ {campo} - AUSENTE")
        else:
            print("❌ AnaliseFinanceiraService retornou dados vazios")
        
    except ImportError:
        print("❌ AnaliseFinanceiraService não encontrado")
    except Exception as e:
        print(f"❌ Erro ao testar APIs: {e}")

def gerar_relatorio_final(stats):
    """Gera relatório final com recomendações"""
    
    print("\n" + "="*60)
    print("📋 RELATÓRIO FINAL E RECOMENDAÇÕES")
    print("="*60)
    
    problemas_encontrados = []
    
    # Verificar problemas críticos
    if stats.get('total_ctes', 0) == 0:
        problemas_encontrados.append("❌ CRÍTICO: Nenhum CTE no banco de dados")
    
    if stats.get('ctes_ultimos_180_dias', 0) == 0:
        problemas_encontrados.append("❌ CRÍTICO: Nenhum CTE nos últimos 180 dias")
    
    if stats.get('receita_total', 0) == 0:
        problemas_encontrados.append("❌ CRÍTICO: Receita total zerada")
    
    if stats.get('ctes_com_valor', 0) == 0:
        problemas_encontrados.append("❌ CRÍTICO: Nenhum CTE com valor válido")
    
    # Exibir problemas
    if problemas_encontrados:
        print("\n🚨 PROBLEMAS CRÍTICOS ENCONTRADOS:")
        for problema in problemas_encontrados:
            print(f"  {problema}")
    else:
        print("\n✅ Nenhum problema crítico encontrado nos dados básicos")
    
    # Recomendações específicas
    print("\n💡 RECOMENDAÇÕES DE CORREÇÃO:")
    
    print("\n1️⃣ IMPLEMENTAR APIS AUSENTES:")
    print("   - Adicionar /api/receita-faturada")
    print("   - Adicionar /api/receita-com-faturas") 
    print("   - Adicionar /api/clientes")
    print("   - Usar o código do artifact 'Backend Corrigido'")
    
    print("\n2️⃣ CORRIGIR VALIDAÇÃO DA API PRINCIPAL:")
    print("   - Remover validação restritiva de filtro_dias")
    print("   - Permitir períodos flexíveis")
    
    print("\n3️⃣ VERIFICAR CAMPOS DA TABELA:")
    print("   - Se envio_final não existe: ALTER TABLE ctes ADD COLUMN envio_final DATE;")
    print("   - Se data_inclusao_fatura não existe: ALTER TABLE ctes ADD COLUMN data_inclusao_fatura DATE;")
    print("   - Ou usar campos existentes como proxy")
    
    print("\n4️⃣ PRÓXIMOS PASSOS:")
    print("   1. Implementar correções do backend")
    print("   2. Adicionar campos faltantes na tabela")
    print("   3. Reiniciar servidor: python iniciar.py")
    print("   4. Testar no navegador")
    print("   5. Verificar console do navegador (F12)")

def criar_campos_ausentes():
    """Cria os campos ausentes na tabela CTEs"""
    print("\n🔧 CRIANDO CAMPOS AUSENTES...")
    
    campos_criar = [
        'envio_final',
        'data_inclusao_fatura', 
        'data_rq_tmc',
        'data_atesto'
    ]
    
    for campo in campos_criar:
        try:
            # Verificar se campo existe
            query_check = text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ctes' AND column_name = '{campo}'
            """)
            
            resultado = db.session.execute(query_check).fetchone()
            
            if not resultado:
                # Campo não existe, criar
                query_create = text(f"ALTER TABLE ctes ADD COLUMN {campo} DATE")
                db.session.execute(query_create)
                db.session.commit()
                print(f"✅ Campo {campo} criado com sucesso")
            else:
                print(f"✅ Campo {campo} já existe")
                
        except Exception as e:
            print(f"❌ Erro ao criar campo {campo}: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("Iniciando diagnóstico completo...")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--criar-campos':
        # Modo de criação de campos
        app = create_app()
        with app.app_context():
            criar_campos_ausentes()
    else:
        # Modo diagnóstico normal
        diagnosticar_completo()
    
    print("\nDiagnóstico concluído!")
    print("Para criar campos ausentes, execute: python diagnostico_dashboard.py --criar-campos")