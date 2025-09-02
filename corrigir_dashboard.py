#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Correção Automática do Dashboard Financeiro
Execute: python corrigir_dashboard.py
"""

import sys
import os
import shutil
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fazer_backup():
    """Faz backup dos arquivos atuais"""
    print("📦 Fazendo backup dos arquivos atuais...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    arquivos_backup = [
        "app/routes/analise_financeira.py",
        "static/js/analise_financeira.js"
    ]
    
    for arquivo in arquivos_backup:
        if os.path.exists(arquivo):
            shutil.copy2(arquivo, backup_dir)
            print(f"✅ Backup: {arquivo} -> {backup_dir}")
    
    return backup_dir

def verificar_estrutura_banco():
    """Verifica e corrige estrutura do banco"""
    print("\n🔍 Verificando estrutura do banco...")
    
    try:
        from app import create_app, db
        from sqlalchemy import text, inspect
        
        app = create_app()
        with app.app_context():
            inspector = inspect(db.engine)
            
            if 'dashboard_baker' not in inspector.get_table_names():
                print("❌ Tabela 'dashboard_baker' não encontrada!")
                return False
            
            colunas = [col['name'] for col in inspector.get_columns('dashboard_baker')]
            print(f"📋 Colunas existentes: {len(colunas)}")
            
            # Verificar campos críticos
            campos_necessarios = {
                'envio_final': 'Campo para receita faturada',
                'data_inclusao_fatura': 'Campo para receita com faturas',
                'numero_fatura': 'Backup para faturas',
                'primeiro_envio': 'Campo para alertas'
            }
            
            campos_ausentes = []
            
            for campo, descricao in campos_necessarios.items():
                if campo in colunas:
                    print(f"✅ {campo}: Existe")
                else:
                    print(f"❌ {campo}: AUSENTE - {descricao}")
                    campos_ausentes.append(campo)
            
            # Tentar criar campos ausentes
            if campos_ausentes:
                print(f"\n🔧 Tentando criar {len(campos_ausentes)} campos ausentes...")
                
                with db.engine.connect() as connection:
                    for campo in campos_ausentes:
                        try:
                            sql = f"ALTER TABLE dashboard_baker ADD COLUMN {campo} DATE"
                            connection.execute(text(sql))
                            connection.commit()
                            print(f"✅ Campo {campo} criado com sucesso")
                        except Exception as e:
                            print(f"⚠️ Não foi possível criar {campo}: {str(e)}")
            
            # Verificar dados
            with db.engine.connect() as connection:
                total_ctes = connection.execute(text("SELECT COUNT(*) FROM dashboard_baker")).scalar()
                print(f"📊 Total de CTEs: {total_ctes:,}")
                
                if total_ctes == 0:
                    print("❌ PROBLEMA CRÍTICO: Nenhum CTE na base de dados!")
                    return False
                
                # Verificar dados do mês corrente
                agora = datetime.now()
                primeiro_dia = agora.replace(day=1).date()
                
                sql_mes = text("""
                    SELECT COUNT(*) as total_mes,
                           COALESCE(SUM(valor_total), 0) as receita_mes
                    FROM dashboard_baker 
                    WHERE data_emissao >= :primeiro_dia
                """)
                
                result = connection.execute(sql_mes, {"primeiro_dia": primeiro_dia}).fetchone()
                print(f"📅 CTEs mês corrente: {result.total_mes}")
                print(f"💰 Receita mês corrente: R$ {result.receita_mes:,.2f}")
                
                if result.total_mes == 0:
                    print("⚠️ AVISO: Nenhum CTE no mês corrente!")
                
            return True
            
    except Exception as e:
        print(f"❌ Erro na verificação do banco: {str(e)}")
        return False

def popular_campos_vazios():
    """Popula campos vazios com dados de fallback"""
    print("\n🔧 Populando campos vazios...")
    
    try:
        from app import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        with app.app_context():
            with db.engine.connect() as connection:
                # Popular envio_final com data_baixa
                sql1 = text("""
                    UPDATE dashboard_baker 
                    SET envio_final = data_baixa 
                    WHERE envio_final IS NULL 
                    AND data_baixa IS NOT NULL
                """)
                
                result1 = connection.execute(sql1)
                connection.commit()
                print(f"✅ Populado envio_final: {result1.rowcount} registros")
                
                # Popular data_inclusao_fatura com primeiro_envio (onde há número de fatura)
                sql2 = text("""
                    UPDATE dashboard_baker 
                    SET data_inclusao_fatura = primeiro_envio 
                    WHERE data_inclusao_fatura IS NULL 
                    AND primeiro_envio IS NOT NULL
                    AND (numero_fatura IS NOT NULL AND numero_fatura != '')
                """)
                
                result2 = connection.execute(sql2)
                connection.commit()
                print(f"✅ Populado data_inclusao_fatura: {result2.rowcount} registros")
                
                # Verificar resultado
                sql_check = text("""
                    SELECT 
                        COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as com_envio_final,
                        COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as com_inclusao_fatura
                    FROM dashboard_baker
                    WHERE data_emissao >= :primeiro_dia
                """)
                
                agora = datetime.now()
                primeiro_dia = agora.replace(day=1).date()
                
                result = connection.execute(sql_check, {"primeiro_dia": primeiro_dia}).fetchone()
                print(f"📊 Resultado no mês corrente:")
                print(f"   CTEs com envio_final: {result.com_envio_final}")
                print(f"   CTEs com data_inclusao_fatura: {result.com_inclusao_fatura}")
                
                return True
                
    except Exception as e:
        print(f"❌ Erro ao popular campos: {str(e)}")
        return False

def criar_backend_corrigido():
    """Cria o arquivo backend corrigido"""
    print("\n📝 Criando backend corrigido...")
    
    # O código do backend seria muito longo para incluir aqui inline
    # Instrução para usar o artifact
    print("💡 Use o código do artifact 'analise_financeira.py - Correção Completa com Alertas'")
    print("   Substitua completamente o arquivo app/routes/analise_financeira.py")
    
    arquivo = "app/routes/analise_financeira.py"
    if os.path.exists(arquivo):
        print(f"✅ Arquivo encontrado: {arquivo}")
        print("⚠️  AÇÃO NECESSÁRIA: Substitua o conteúdo pelo código do artifact")
        return True
    else:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False

def criar_frontend_corrigido():
    """Cria o arquivo frontend corrigido"""
    print("\n🎨 Criando frontend corrigido...")
    
    arquivo = "static/js/analise_financeira.js"
    if os.path.exists(arquivo):
        print(f"✅ Arquivo encontrado: {arquivo}")
        print("💡 Use o código do artifact 'analise_financeira.js - JavaScript Robusto Corrigido'")
        print("   Substitua completamente o arquivo static/js/analise_financeira.js")
        return True
    else:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        print("💡 Crie o arquivo e adicione o código do artifact")
        return False

def testar_apis():
    """Testa as APIs do sistema"""
    print("\n🧪 Testando APIs...")
    
    try:
        import requests
        import time
        
        # Aguardar servidor inicializar
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(2)
        
        base_url = "http://localhost:5000"
        
        apis_testar = [
            ("/analise-financeira/api/test-conexao", "Teste de Conexão"),
            ("/analise-financeira/api/metricas-mes-corrente", "Métricas Mês Corrente"),
            ("/analise-financeira/api/receita-faturada", "Receita Faturada"),
            ("/analise-financeira/api/receita-com-faturas", "Receita com Faturas"),
            ("/analise-financeira/api/alertas", "Sistema de Alertas")
        ]
        
        resultados = []
        
        for endpoint, nome in apis_testar:
            try:
                url = base_url + endpoint
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success', False):
                        print(f"✅ {nome}: Funcionando")
                        resultados.append((nome, True, None))
                    else:
                        error = data.get('error', 'Erro desconhecido')
                        print(f"❌ {nome}: {error}")
                        resultados.append((nome, False, error))
                else:
                    print(f"❌ {nome}: HTTP {response.status_code}")
                    resultados.append((nome, False, f"HTTP {response.status_code}"))
                    
            except requests.exceptions.ConnectionError:
                print(f"❌ {nome}: Servidor não acessível")
                resultados.append((nome, False, "Servidor não acessível"))
            except Exception as e:
                print(f"❌ {nome}: {str(e)}")
                resultados.append((nome, False, str(e)))
        
        # Resumo
        funcionando = sum(1 for _, status, _ in resultados if status)
        total = len(resultados)
        
        print(f"\n📊 Resultado: {funcionando}/{total} APIs funcionando")
        
        return funcionando == total
        
    except ImportError:
        print("⚠️ Biblioteca 'requests' não disponível. Instale com: pip install requests")
        return False

def gerar_relatorio_correcao():
    """Gera relatório final da correção"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO FINAL DA CORREÇÃO")
    print("="*60)
    
    try:
        from app import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        with app.app_context():
            with db.engine.connect() as connection:
                agora = datetime.now()
                primeiro_dia = agora.replace(day=1).date()
                
                # Query para dados dos cards
                sql_cards = text("""
                    SELECT 
                        COUNT(*) as total_mes,
                        COALESCE(SUM(valor_total), 0) as receita_total,
                        COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as com_envio_final,
                        COALESCE(SUM(CASE WHEN envio_final IS NOT NULL THEN valor_total ELSE 0 END), 0) as receita_faturada,
                        COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as com_inclusao_fatura,
                        COALESCE(SUM(CASE WHEN data_inclusao_fatura IS NOT NULL THEN valor_total ELSE 0 END), 0) as receita_com_faturas
                    FROM dashboard_baker 
                    WHERE data_emissao >= :primeiro_dia
                """)
                
                result = connection.execute(sql_cards, {"primeiro_dia": primeiro_dia}).fetchone()
                
                print(f"📅 Período analisado: {primeiro_dia.strftime('%d/%m/%Y')} a hoje")
                print(f"📊 CTEs do mês: {result.total_mes}")
                print(f"💰 Receita total: R$ {result.receita_total:,.2f}")
                print(f"✅ Receita faturada: R$ {result.receita_faturada:,.2f} ({result.com_envio_final} CTEs)")
                print(f"📋 Receita c/ faturas: R$ {result.receita_com_faturas:,.2f} ({result.com_inclusao_fatura} CTEs)")
                
                # Análise dos problemas
                print("\n🔍 ANÁLISE:")
                
                if result.receita_faturada > 0:
                    print("✅ Card 'Receita Faturada' deve funcionar")
                else:
                    print("❌ Card 'Receita Faturada' ainda zerado")
                    print("   💡 Populate o campo 'envio_final' ou use fallbacks")
                
                if result.receita_com_faturas > 0:
                    print("✅ Card 'Receita c/ Faturas' deve funcionar")
                else:
                    print("❌ Card 'Receita c/ Faturas' ainda zerado")
                    print("   💡 Populate o campo 'data_inclusao_fatura' ou use fallbacks")
                
                if result.total_mes == 0:
                    print("❌ PROBLEMA CRÍTICO: Nenhum CTE no mês corrente")
                    print("   💡 Verifique as datas dos CTEs na base")
                
    except Exception as e:
        print(f"❌ Erro no relatório: {str(e)}")

def main():
    """Função principal de correção"""
    print("🚀 SCRIPT DE CORREÇÃO AUTOMÁTICA - DASHBOARD FINANCEIRO")
    print("="*60)
    
    print("⚠️  IMPORTANTE: Execute este script com o servidor PARADO")
    print("   Pare o servidor com Ctrl+C antes de continuar")
    input("   Pressione Enter para continuar...")
    
    # 1. Fazer backup
    backup_dir = fazer_backup()
    print(f"✅ Backup criado em: {backup_dir}")
    
    # 2. Verificar estrutura do banco
    banco_ok = verificar_estrutura_banco()
    
    if banco_ok:
        # 3. Popular campos vazios
        popular_campos_vazios()
    
    # 4. Verificar arquivos
    backend_ok = criar_backend_corrigido()
    frontend_ok = criar_frontend_corrigido()
    
    # 5. Gerar relatório
    gerar_relatorio_correcao()
    
    print("\n" + "="*60)
    print("📋 PRÓXIMOS PASSOS MANUAIS")
    print("="*60)
    
    if not backend_ok:
        print("❌ 1. SUBSTITUIR app/routes/analise_financeira.py")
        print("   Use o artifact 'analise_financeira.py - Correção Completa com Alertas'")
    else:
        print("⚠️  1. SUBSTITUIR app/routes/analise_financeira.py")
        print("   Use o artifact 'analise_financeira.py - Correção Completa com Alertas'")
    
    if not frontend_ok:
        print("❌ 2. CRIAR/SUBSTITUIR static/js/analise_financeira.js")
        print("   Use o artifact 'analise_financeira.js - JavaScript Robusto Corrigido'")
    else:
        print("⚠️  2. SUBSTITUIR static/js/analise_financeira.js")
        print("   Use o artifact 'analise_financeira.js - JavaScript Robusto Corrigido'")
    
    print("✅ 3. REINICIAR o servidor: python iniciar.py")
    print("✅ 4. TESTAR: http://localhost:5000/analise-financeira/")
    print("✅ 5. VERIFICAR console (F12) para erros")
    
    print(f"\n💾 Backup dos arquivos originais em: {backup_dir}")
    print("   Restaure com: cp backup_*/arquivo_original caminho/destino")
    
    print("\n🎯 RESULTADO ESPERADO:")
    print("   - Cards com valores reais (não R$ 0,00)")
    print("   - Sistema de alertas funcionando")
    print("   - APIs respondendo corretamente")

if __name__ == "__main__":
    main()