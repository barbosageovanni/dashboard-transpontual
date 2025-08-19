#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração para atualizar estrutura do banco
Adiciona colunas faltantes na tabela users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrar_banco():
    """Executa migração do banco de dados"""
    
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migração do banco...")
        
        try:
            # Verificar conexão
            db.session.execute(text("SELECT 1"))
            print("✅ Conexão com banco estabelecida")
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
        
        try:
            # 1. Verificar estrutura atual da tabela users
            print("\n📋 Verificando estrutura da tabela users...")
            
            # Query para verificar colunas existentes
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            
            colunas_existentes = [row[0] for row in result.fetchall()]
            print(f"Colunas existentes: {colunas_existentes}")
            
            # 2. Definir colunas necessárias
            colunas_necessarias = {
                'nome_completo': 'VARCHAR(200)',
                'tipo_usuario': 'VARCHAR(20) DEFAULT \'user\'',
                'ativo': 'BOOLEAN DEFAULT TRUE',
                'ultimo_login': 'TIMESTAMP',
                'total_logins': 'INTEGER DEFAULT 0'
            }
            
            # 3. Adicionar colunas faltantes
            for coluna, tipo in colunas_necessarias.items():
                if coluna not in colunas_existentes:
                    print(f"➕ Adicionando coluna: {coluna}")
                    try:
                        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {coluna} {tipo}"))
                        db.session.commit()
                        print(f"✅ Coluna {coluna} adicionada")
                    except Exception as e:
                        print(f"⚠️ Erro ao adicionar {coluna}: {e}")
                        db.session.rollback()
                else:
                    print(f"✅ Coluna {coluna} já existe")
            
            # 4. Verificar e atualizar dados existentes
            print("\n🔄 Atualizando dados existentes...")
            
            # Definir tipo_usuario para registros existentes
            try:
                db.session.execute(text("""
                    UPDATE users 
                    SET tipo_usuario = CASE 
                        WHEN username = 'admin' THEN 'admin'
                        ELSE 'user'
                    END
                    WHERE tipo_usuario IS NULL OR tipo_usuario = ''
                """))
                db.session.commit()
                print("✅ Tipos de usuário atualizados")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar tipos: {e}")
                db.session.rollback()
            
            # Definir ativo = true para todos
            try:
                db.session.execute(text("UPDATE users SET ativo = TRUE WHERE ativo IS NULL"))
                db.session.commit()
                print("✅ Status ativo atualizado")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar status: {e}")
                db.session.rollback()
            
            # Definir total_logins = 0 para registros existentes
            try:
                db.session.execute(text("UPDATE users SET total_logins = 0 WHERE total_logins IS NULL"))
                db.session.commit()
                print("✅ Total de logins atualizado")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar logins: {e}")
                db.session.rollback()
            
            # 5. Criar usuários padrão se não existirem
            print("\n👥 Verificando usuários padrão...")
            
            # Importar User para usar o método de hash
            from werkzeug.security import generate_password_hash
            
            usuarios_padrao = [
                {
                    'username': 'admin',
                    'email': 'admin@baker.com',
                    'password': 'admin123',
                    'nome_completo': 'Administrador do Sistema',
                    'tipo_usuario': 'admin',
                    'ativo': True,
                    'total_logins': 0
                },
                {
                    'username': 'user',
                    'email': 'user@baker.com', 
                    'password': 'password123',
                    'nome_completo': 'Usuário Padrão',
                    'tipo_usuario': 'user',
                    'ativo': True,
                    'total_logins': 0
                },
                {
                    'username': 'demo',
                    'email': 'demo@baker.com',
                    'password': 'demo123',
                    'nome_completo': 'Usuário Demo',
                    'tipo_usuario': 'viewer',
                    'ativo': True,
                    'total_logins': 0
                }
            ]
            
            for user_data in usuarios_padrao:
                # Verificar se usuário já existe
                result = db.session.execute(text(
                    "SELECT id FROM users WHERE username = :username"
                ), {'username': user_data['username']})
                
                if result.fetchone() is None:
                    print(f"➕ Criando usuário: {user_data['username']}")
                    
                    # Gerar hash da senha
                    password_hash = generate_password_hash(user_data['password'])
                    
                    try:
                        db.session.execute(text("""
                            INSERT INTO users (username, email, password_hash, nome_completo, tipo_usuario, ativo, total_logins, created_at, updated_at)
                            VALUES (:username, :email, :password_hash, :nome_completo, :tipo_usuario, :ativo, :total_logins, NOW(), NOW())
                        """), {
                            'username': user_data['username'],
                            'email': user_data['email'],
                            'password_hash': password_hash,
                            'nome_completo': user_data['nome_completo'],
                            'tipo_usuario': user_data['tipo_usuario'],
                            'ativo': user_data['ativo'],
                            'total_logins': user_data['total_logins']
                        })
                        
                        db.session.commit()
                        print(f"✅ Usuário {user_data['username']} criado")
                    except Exception as e:
                        print(f"❌ Erro ao criar usuário {user_data['username']}: {e}")
                        db.session.rollback()
                else:
                    print(f"✅ Usuário {user_data['username']} já existe")
            
            print(f"\n🎉 Migração concluída com sucesso!")
            
            # 6. Verificar estrutura final
            print("\n📋 Estrutura final da tabela users:")
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
            
            # 7. Mostrar usuários criados
            print("\n👥 Usuários no sistema:")
            result = db.session.execute(text("""
                SELECT username, email, tipo_usuario, ativo 
                FROM users 
                ORDER BY tipo_usuario, username
            """))
            
            for row in result.fetchall():
                status = "✅ Ativo" if row[3] else "❌ Inativo"
                print(f"  - {row[0]} ({row[2]}) - {row[1]} - {status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if migrar_banco():
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Execute: python popular_dados_teste.py")
        print("2. Execute: python iniciar.py")
        print("3. Acesse: http://localhost:5000")
        print("\n🔐 CREDENCIAIS:")
        print("  admin / admin123 (Administrador)")
        print("  user / password123 (Usuário)")
        print("  demo / demo123 (Demo)")
    else:
        print("\n❌ Falha na migração. Verifique os erros acima.")