#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar estrutura do banco
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def verificar_estrutura():
    """Verifica estrutura do banco"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICAÇÃO DO BANCO DE DADOS")
        print("=" * 50)
        
        try:
            # 1. Verificar conexão
            db.session.execute(text("SELECT 1"))
            print("✅ Conexão com banco estabelecida")
            
            # 2. Verificar tabelas
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tabelas = [row[0] for row in result.fetchall()]
            print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
            for tabela in tabelas:
                print(f"  - {tabela}")
            
            # 3. Verificar estrutura da tabela users
            if 'users' in tabelas:
                print(f"\n👥 ESTRUTURA DA TABELA USERS:")
                result = db.session.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """))
                
                for row in result.fetchall():
                    default_val = f" DEFAULT {row[3]}" if row[3] else ""
                    nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                    print(f"  - {row[0]}: {row[1]} {nullable}{default_val}")
                
                # Contar usuários
                result = db.session.execute(text("SELECT COUNT(*) FROM users"))
                total_users = result.fetchone()[0]
                print(f"\n📊 Total de usuários: {total_users}")
                
                if total_users > 0:
                    result = db.session.execute(text("""
                        SELECT username, tipo_usuario, ativo 
                        FROM users 
                        ORDER BY tipo_usuario, username
                    """))
                    
                    print("👤 Usuários cadastrados:")
                    for row in result.fetchall():
                        status = "✅" if row[2] else "❌"
                        print(f"  {status} {row[0]} ({row[1]})")
            
            # 4. Verificar estrutura da tabela dashboard_baker
            if 'dashboard_baker' in tabelas:
                print(f"\n📊 ESTRUTURA DA TABELA DASHBOARD_BAKER:")
                result = db.session.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'dashboard_baker'
                    ORDER BY ordinal_position
                """))
                
                colunas_cte = []
                for row in result.fetchall():
                    nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                    print(f"  - {row[0]}: {row[1]} {nullable}")
                    colunas_cte.append(row[0])
                
                # Contar CTEs
                result = db.session.execute(text("SELECT COUNT(*) FROM dashboard_baker"))
                total_ctes = result.fetchone()[0]
                print(f"\n📊 Total de CTEs: {total_ctes}")
                
                if total_ctes > 0:
                    # Estatísticas básicas
                    result = db.session.execute(text("""
                        SELECT 
                            COUNT(*) as total,
                            SUM(valor_total) as valor_total,
                            COUNT(DISTINCT destinatario_nome) as clientes,
                            COUNT(DISTINCT veiculo_placa) as veiculos,
                            COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa
                        FROM dashboard_baker
                    """))
                    
                    stats = result.fetchone()
                    print(f"💰 Valor total: R$ {stats[1] or 0:,.2f}")
                    print(f"👥 Clientes únicos: {stats[2] or 0}")
                    print(f"🚛 Veículos únicos: {stats[3] or 0}")
                    print(f"✅ CTEs com baixa: {stats[4] or 0}")
            
            print("\n✅ Verificação concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return False

if __name__ == "__main__":
    verificar_estrutura()