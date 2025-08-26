#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE DIAGNÓSTICO COMPLETO - Dashboard Baker
Execute este script para identificar problemas na conexão e dados
"""

import os
import sys
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def diagnostico_completo():
    """Executa diagnóstico completo do sistema"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DASHBOARD BAKER - INICIANDO")
    print("=" * 60)
    
    # 1. Verificar configurações
    print("\n1️⃣ VERIFICANDO CONFIGURAÇÕES...")
    verificar_configuracoes()
    
    # 2. Testar conexão com banco
    print("\n2️⃣ TESTANDO CONEXÃO COM BANCO...")
    testar_conexao_banco()
    
    # 3. Verificar estrutura da tabela
    print("\n3️⃣ VERIFICANDO ESTRUTURA DA TABELA...")
    verificar_estrutura_tabela()
    
    # 4. Verificar dados na tabela
    print("\n4️⃣ VERIFICANDO DADOS NA TABELA...")
    verificar_dados_tabela()
    
    # 5. Testar modelo CTE
    print("\n5️⃣ TESTANDO MODELO CTE...")
    testar_modelo_cte()
    
    # 6. Testar consulta pandas
    print("\n6️⃣ TESTANDO CONSULTA PANDAS...")
    testar_consulta_pandas()
    
    # 7. Diagnóstico da API
    print("\n7️⃣ TESTANDO API DO DASHBOARD...")
    testar_api_dashboard()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)

def verificar_configuracoes():
    """Verifica se as configurações estão corretas"""
    try:
        configs = {
            'DB_HOST': os.getenv('DB_HOST'),
            'DB_PORT': os.getenv('DB_PORT'),
            'DB_NAME': os.getenv('DB_NAME'),
            'DB_USER': os.getenv('DB_USER'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD'),
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'FLASK_ENV': os.getenv('FLASK_ENV')
        }
        
        print("Configurações encontradas:")
        for key, value in configs.items():
            if 'PASSWORD' in key or 'SECRET' in key:
                status = "✅ Definida" if value else "❌ Não definida"
                print(f"  {key}: {status}")
            else:
                print(f"  {key}: {value or '❌ Não definida'}")
        
        # Verificar se todas as configs obrigatórias estão definidas
        obrigatorias = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        faltando = [k for k in obrigatorias if not configs[k]]
        
        if faltando:
            print(f"❌ ERRO: Configurações obrigatórias faltando: {', '.join(faltando)}")
            return False
        else:
            print("✅ Todas as configurações obrigatórias estão definidas")
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao verificar configurações: {e}")
        return False

def testar_conexao_banco():
    """Testa conexão básica com o banco"""
    try:
        # Importar dentro da função para evitar erros de inicialização
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            # Testar conexão executando query simples
            result = db.engine.execute("SELECT 1 as test")
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Conexão com banco estabelecida com sucesso")
                
                # Mostrar informações do banco
                db_info = db.engine.execute("""
                    SELECT 
                        version() as version,
                        current_database() as database,
                        current_user as user
                """).fetchone()
                
                print(f"  Base: {db_info[1]}")
                print(f"  Usuário: {db_info[2]}")
                print(f"  Versão: {db_info[0][:50]}...")
                
                return True
            else:
                print("❌ ERRO: Query de teste falhou")
                return False
                
    except Exception as e:
        print(f"❌ ERRO de conexão com banco: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        
        # Dicas específicas para erros comuns
        if "could not connect" in str(e):
            print("   💡 Dica: Verifique host, porta e credenciais")
        elif "authentication failed" in str(e):
            print("   💡 Dica: Verifique usuário e senha")
        elif "database" in str(e) and "does not exist" in str(e):
            print("   💡 Dica: Verifique se o nome do banco está correto")
            
        return False

def verificar_estrutura_tabela():
    """Verifica se a tabela dashboard_baker existe e sua estrutura"""
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            # Verificar se tabela existe
            result = db.engine.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'dashboard_baker'
                )
            """).fetchone()
            
            if not result[0]:
                print("❌ ERRO: Tabela 'dashboard_baker' não existe")
                
                # Listar tabelas disponíveis
                tables = db.engine.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """).fetchall()
                
                print("   Tabelas disponíveis:")
                for table in tables[:10]:  # Mostrar apenas 10 primeiras
                    print(f"     - {table[0]}")
                if len(tables) > 10:
                    print(f"     ... e mais {len(tables) - 10} tabelas")
                    
                return False
            
            print("✅ Tabela 'dashboard_baker' existe")
            
            # Verificar estrutura da tabela
            colunas = db.engine.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'dashboard_baker'
                ORDER BY ordinal_position
            """).fetchall()
            
            print("  Estrutura da tabela:")
            for col in colunas:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"    {col[0]}: {col[1]} {nullable}")
            
            # Verificar colunas essenciais
            colunas_essenciais = [
                'numero_cte', 'destinatario_nome', 'valor_total', 
                'data_emissao', 'data_baixa'
            ]
            
            colunas_existentes = [col[0] for col in colunas]
            faltando = [col for col in colunas_essenciais if col not in colunas_existentes]
            
            if faltando:
                print(f"⚠️ AVISO: Colunas essenciais faltando: {', '.join(faltando)}")
            else:
                print("✅ Todas as colunas essenciais estão presentes")
                
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao verificar estrutura da tabela: {e}")
        return False

def verificar_dados_tabela():
    """Verifica se há dados na tabela"""
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            # Contar registros
            total = db.engine.execute("SELECT COUNT(*) FROM dashboard_baker").fetchone()[0]
            
            if total == 0:
                print("❌ ERRO: Tabela 'dashboard_baker' está vazia (0 registros)")
                return False
            
            print(f"✅ Tabela contém {total} registros")
            
            # Estatísticas básicas
            stats = db.engine.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT numero_cte) as ctes_unicos,
                    COUNT(DISTINCT destinatario_nome) as clientes_unicos,
                    COUNT(data_baixa) as com_baixa,
                    COUNT(*) - COUNT(data_baixa) as sem_baixa,
                    COALESCE(SUM(valor_total), 0) as valor_total
                FROM dashboard_baker
            """).fetchone()
            
            print("  Estatísticas:")
            print(f"    Total registros: {stats[0]}")
            print(f"    CTEs únicos: {stats[1]}")
            print(f"    Clientes únicos: {stats[2]}")
            print(f"    Com baixa: {stats[3]}")
            print(f"    Sem baixa: {stats[4]}")
            print(f"    Valor total: R$ {float(stats[5]):,.2f}")
            
            # Mostrar alguns exemplos
            exemplos = db.engine.execute("""
                SELECT numero_cte, destinatario_nome, valor_total, data_emissao, data_baixa
                FROM dashboard_baker 
                ORDER BY numero_cte DESC 
                LIMIT 3
            """).fetchall()
            
            print("  Exemplos de registros:")
            for ex in exemplos:
                baixa_status = "✅ Pago" if ex[4] else "⏳ Pendente"
                print(f"    CTE {ex[0]}: {ex[1]} - R$ {float(ex[2]):,.2f} - {baixa_status}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao verificar dados da tabela: {e}")
        return False

def testar_modelo_cte():
    """Testa se o modelo CTE do SQLAlchemy funciona"""
    try:
        from app import create_app
        from app.models.cte import CTE
        
        app = create_app()
        
        with app.app_context():
            # Testar query básica
            total = CTE.query.count()
            print(f"✅ Modelo CTE funciona - Total: {total} registros")
            
            # Testar um registro específico
            primeiro = CTE.query.first()
            if primeiro:
                print(f"  Primeiro registro: CTE {primeiro.numero_cte}")
                print(f"    Destinatário: {primeiro.destinatario_nome}")
                print(f"    Valor: R$ {float(primeiro.valor_total):,.2f}")
                print(f"    Has Baixa: {primeiro.has_baixa}")
                print(f"    Processo Completo: {primeiro.processo_completo}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERRO no modelo CTE: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_consulta_pandas():
    """Testa se a consulta pandas funciona"""
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            # Testar a query SQL que está falhando
            sql_query = """
                SELECT numero_cte, destinatario_nome, veiculo_placa, valor_total,
                       data_emissao, numero_fatura, data_baixa, observacao,
                       data_inclusao_fatura, data_envio_processo, primeiro_envio,
                       data_rq_tmc, data_atesto, envio_final, origem_dados
                FROM dashboard_baker 
                ORDER BY numero_cte DESC
                LIMIT 100
            """
            
            df = pd.read_sql_query(sql_query, db.engine)
            
            print(f"✅ Consulta pandas funciona - DataFrame com {len(df)} linhas")
            print(f"  Colunas: {list(df.columns)}")
            print(f"  Tipos de dados:")
            for col in df.columns:
                print(f"    {col}: {df[col].dtype}")
            
            # Verificar dados nulos
            print(f"  Dados nulos por coluna:")
            for col in df.columns:
                nulos = df[col].isna().sum()
                if nulos > 0:
                    print(f"    {col}: {nulos} nulos")
            
            return True
            
    except Exception as e:
        print(f"❌ ERRO na consulta pandas: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_api_dashboard():
    """Testa a API do dashboard simulando o processo"""
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.test_client() as client:
            # Fazer login primeiro (simulado)
            print("  Testando API de métricas...")
            
            # Testar diretamente as funções internas
            with app.app_context():
                from app.routes.dashboard import _carregar_df_cte, _metricas_basicas
                
                # Carregar DataFrame
                df = _carregar_df_cte()
                print(f"    DataFrame carregado: {len(df)} registros")
                
                if not df.empty:
                    # Calcular métricas
                    metricas = _metricas_basicas(df)
                    print(f"    Métricas calculadas:")
                    print(f"      Total CTEs: {metricas['total_ctes']}")
                    print(f"      Valor Total: R$ {metricas['valor_total']:,.2f}")
                    print(f"      Clientes: {metricas['clientes_unicos']}")
                    print(f"      Faturas Pagas: {metricas['faturas_pagas']}")
                
                return True
                
    except Exception as e:
        print(f"❌ ERRO no teste da API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    try:
        diagnostico_completo()
    except Exception as e:
        print(f"❌ ERRO CRÍTICO no diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()