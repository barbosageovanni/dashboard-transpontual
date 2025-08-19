#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção para criar usuários sem conflito de updated_at
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
from werkzeug.security import generate_password_hash

def criar_usuarios():
    """Cria usuários sem usar updated_at conflitante"""
    
    app = create_app()
    
    with app.app_context():
        print("👥 Criando usuários padrão...")
        
        usuarios = [
            ('user', 'user@baker.com', 'password123', 'Usuário Padrão', 'user'),
            ('demo', 'demo@baker.com', 'demo123', 'Usuário Demo', 'viewer')
        ]
        
        for username, email, password, nome, tipo in usuarios:
            try:
                # Verificar se existe
                result = db.session.execute(text("SELECT id FROM users WHERE username = :username"), 
                                           {'username': username})
                
                if not result.fetchone():
                    # Criar usuário SEM updated_at
                    password_hash = generate_password_hash(password)
                    
                    db.session.execute(text("""
                        INSERT INTO users (username, email, password_hash, nome_completo, tipo_usuario, ativo, total_logins)
                        VALUES (:username, :email, :password_hash, :nome_completo, :tipo_usuario, TRUE, 0)
                    """), {
                        'username': username,
                        'email': email,
                        'password_hash': password_hash,
                        'nome_completo': nome,
                        'tipo_usuario': tipo
                    })
                    
                    db.session.commit()
                    print(f"✅ Usuário {username} criado com sucesso!")
                else:
                    print(f"✅ Usuário {username} já existe")
                    
            except Exception as e:
                print(f"❌ Erro ao criar usuário {username}: {e}")
                db.session.rollback()
        
        # Verificar usuários criados
        print("\n👥 Usuários no sistema:")
        result = db.session.execute(text("SELECT username, tipo_usuario, ativo FROM users ORDER BY tipo_usuario"))
        for row in result.fetchall():
            status = "✅" if row[2] else "❌"
            print(f"  {status} {row[0]} ({row[1]})")
        
        return True

if __name__ == "__main__":
    if criar_usuarios():
        print("\n🚀 AGORA EXECUTE:")
        print("python iniciar.py")
    else:
        print("\n❌ Erro na criação de usuários")