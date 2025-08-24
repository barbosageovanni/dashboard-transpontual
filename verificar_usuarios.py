#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar usuários no banco de dados
"""

import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def verificar_usuarios():
    """Verificar usuários no banco"""
    app = create_app()
    
    with app.app_context():
        print("=== Usuários no banco ===")
        users = User.query.all()
        
        if not users:
            print("❌ Nenhum usuário encontrado no banco!")
            return False
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Ativo: {user.ativo}")
            print(f"Tipo: {user.tipo_usuario}")
            print("---")
        
        # Verificar se existe admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"✅ Usuário admin encontrado - Ativo: {admin.ativo}")
            return True
        else:
            print("❌ Usuário admin não encontrado!")
            return False

if __name__ == "__main__":
    verificar_usuarios()
