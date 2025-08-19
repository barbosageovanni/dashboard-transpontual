#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico Completo - Dashboard Baker
Execute para identificar e corrigir problemas do sistema
"""

import sys
import os
from datetime import datetime

def diagnosticar_sistema():
    """Executa diagnóstico completo do sistema"""
    
    print("🔍 DIAGNÓSTICO COMPLETO - DASHBOARD BAKER")
    print("=" * 60)
    print(f"⏰ Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Verificar estrutura de arquivos
    print("\n📁 1. VERIFICANDO ESTRUTURA DE ARQUIVOS...")
    verificar_estrutura_arquivos()
    
    # 2. Testar conexão com banco
    print("\n🗄️ 2. TESTANDO CONEXÃO COM BANCO...")
    testar_conexao_banco()
    
    # 3. Verificar usuários
    print("\n👥 3. VERIFICANDO USUÁRIOS...")
    verificar_usuarios()
    
    # 4. Verificar CTEs
    print("\n📋 4. VERIFICANDO CTEs...")
    verificar_ctes()
    
    # 5. Verificar blueprints
    print("\n🔗 5. VERIFICANDO BLUEPRINTS...")
    verificar_blueprints()
    
    # 6. Sugestões de correção
    print("\n🛠️ 6. SUGESTÕES DE CORREÇÃO...")
    sugerir_correcoes()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO CONCLUÍDO!")
    print("=" * 60)

def verificar_estrutura_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    arquivos_necessarios = [
        'app/__init__.py',
        'app/models/user.py',
        'app/models/cte.py',
        'app/routes/auth.py',
        'app/routes/dashboard.py',
        'app/routes/baixas.py',
        'app/routes/ctes.py',
        'app/routes/admin.py',  # Novo
        'app/templates/base.html',
        'app/templates/dashboard/index.html',
        'app/static/js/dashboard.js',
        'config.py',
        'iniciar.py'
    ]
    
    arquivos_faltando = []
    arquivos_ok = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            arquivos_ok.append(arquivo)
            print(f"   ✅ {arquivo}")
        else:
            arquivos_faltando.append(arquivo)
            print(f"   ❌ {arquivo}")
    
    if arquivos_faltando:
        print(f"\n   🚨 ARQUIVOS FALTANDO: {len(arquivos_faltando)}")
        for arquivo in arquivos_faltando:
            print(f"      - {arquivo}")
    else:
        print(f"\n   ✅ Todos os {len(arquivos_ok)} arquivos encontrados!")

def testar_conexao_banco():
    """Testa conexão com o banco de dados"""
    try:
        # Tentar importar e conectar
        sys.path.append('.')
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            # Testar conexão
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            if result:
                print("   ✅ Conexão com banco OK")
                
                # Verificar tabelas
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                print(f"   📊 Tabelas encontradas: {len(tables)}")
                for table in tables:
                    print(f"      - {table}")
                
                # Verificar se tabelas principais existem
                tabelas_necessarias = ['users', 'dashboard_baker']
                for tabela in tabelas_necessarias:
                    if tabela in tables:
                        print(f"   ✅ Tabela {tabela} existe")
                    else:
                        print(f"   ❌ Tabela {tabela} NÃO existe")
            else:
                print("   ❌ Erro na conexão com banco")
                
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {str(e)}")
        print("   💡 Verifique as credenciais do Supabase")

def verificar_usuarios():
    """Verifica se existe usuário admin"""
    try:
        sys.path.append('.')
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        with app.app_context():
            total_users = User.query.count()
            admin_users = User.query.filter_by(tipo_usuario='admin').count()
            active_users = User.query.filter_by(ativo=True).count()
            
            print(f"   📊 Total de usuários: {total_users}")
            print(f"   👑 Administradores: {admin_users}")
            print(f"   ✅ Usuários ativos: {active_users}")
            
            # Verificar se existe admin
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"   ✅ Admin existe: {admin.username}")
                print(f"      - Email: {admin.email}")
                print(f"      - Ativo: {admin.ativo}")
                print(f"      - Tipo: {admin.tipo_usuario}")
                print(f"      - Bloqueado: {admin.is_locked()}")
            else:
                print("   ❌ Admin NÃO existe")
                print("   💡 Execute: flask criar-admin")
                
    except Exception as e:
        print(f"   ❌ Erro ao verificar usuários: {str(e)}")

def verificar_ctes():
    """Verifica dados dos CTEs"""
    try:
        sys.path.append('.')
        from app import create_app, db
        from app.models.cte import CTE
        
        app = create_app()
        with app.app_context():
            total_ctes = CTE.query.count()
            valor_total = db.session.query(db.func.sum(CTE.valor_total)).scalar() or 0
            ctes_com_baixa = CTE.query.filter(CTE.data_baixa.isnot(None)).count()
            
            print(f"   📊 Total de CTEs: {total_ctes}")
            print(f"   💰 Valor total: R$ {valor_total:,.2f}")
            print(f"   ✅ CTEs com baixa: {ctes_com_baixa}")
            print(f"   ⏳ CTEs pendentes: {total_ctes - ctes_com_baixa}")
            
            if total_ctes == 0:
                print("   ⚠️ Nenhum CTE cadastrado")
                print("   💡 Importe dados via interface ou CSV")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar CTEs: {str(e)}")

def verificar_blueprints():
    """Verifica se todos os blueprints estão registrados"""
    try:
        sys.path.append('.')
        from app import create_app
        
        app = create_app()
        
        blueprints_esperados = [
            'auth', 'dashboard', 'baixas', 'ctes', 'admin'
        ]
        
        blueprints_registrados = list(app.blueprints.keys())
        
        print(f"   📊 Blueprints registrados: {len(blueprints_registrados)}")
        
        for bp in blueprints_esperados:
            if bp in blueprints_registrados:
                print(f"   ✅ {bp}")
            else:
                print(f"   ❌ {bp} (FALTANDO)")
        
        # Blueprints extras
        extras = set(blueprints_registrados) - set(blueprints_esperados)
        if extras:
            print(f"   📎 Extras: {', '.join(extras)}")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar blueprints: {str(e)}")

def sugerir_correcoes():
    """Sugere correções baseadas no diagnóstico"""
    print("   🔧 AÇÕES RECOMENDADAS:")
    print()
    
    print("   1️⃣ CORRIGIR ERRO IMEDIATO:")
    print("      • Substitua o arquivo app/models/user.py")
    print("      • Substitua o arquivo app/templates/base.html")
    print("      • Adicione os comandos CLI ao app/__init__.py")
    print()
    
    print("   2️⃣ RESETAR ADMIN:")
    print("      flask reset-admin")
    print()
    
    print("   3️⃣ VERIFICAR BANCO:")
    print("      flask init-db")
    print()
    
    print("   4️⃣ TESTAR SISTEMA:")
    print("      python iniciar.py")
    print("      • Acesse: http://localhost:5000")
    print("      • Login: admin / Admin123!")
    print()
    
    print("   5️⃣ SE PERSISTIR PROBLEMA:")
    print("      • Verifique logs no terminal")
    print("      • Confirme conexão Supabase")
    print("      • Execute flask stats")

if __name__ == '__main__':
    diagnosticar_sistema()