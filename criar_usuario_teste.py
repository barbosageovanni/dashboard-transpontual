#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar usuário de teste com senha conhecida
"""

import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def criar_usuario_teste():
    """Criar usuário de teste"""
    app = create_app()
    
    with app.app_context():
        # Verificar se já existe
        teste = User.query.filter_by(username='teste').first()
        if teste:
            print("✅ Usuário 'teste' já existe")
            # Testar senha
            if teste.check_password('123456'):
                print("✅ Senha '123456' funciona")
                return True
            else:
                print("❌ Senha '123456' não funciona, recriando usuário...")
                db.session.delete(teste)
                db.session.commit()
        
        # Criar novo usuário
        try:
            novo_usuario = User(
                username='teste',
                email='teste@teste.com',
                nome_completo='Usuário Teste',
                tipo_usuario='admin',
                ativo=True
            )
            novo_usuario.set_password('123456')
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            print("✅ Usuário 'teste' criado com senha '123456'")
            
            # Verificar se funcionou
            if novo_usuario.check_password('123456'):
                print("✅ Verificação: senha '123456' funciona")
                return True
            else:
                print("❌ Verificação: senha não funciona")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    criar_usuario_teste()
