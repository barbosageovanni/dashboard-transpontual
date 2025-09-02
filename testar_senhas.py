#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste detalhado de autenticação
"""

import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def testar_senhas():
    """Testar diferentes senhas para o usuário admin"""
    app = create_app()
    
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ Usuário admin não encontrado!")
            return
        
        print(f"✅ Usuário admin encontrado: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Ativo: {admin.ativo}")
        
        # Testar diferentes senhas comuns
        senhas_teste = [
            "admin123",
            "admin",
            "123456",
            "password",
            "admin@123",
            "transpontual",
            "dashboard"
        ]
        
        print("\n=== Testando senhas ===")
        for senha in senhas_teste:
            try:
                resultado = admin.check_password(senha)
                print(f"Senha '{senha}': {'✅ CORRETA' if resultado else '❌ incorreta'}")
                if resultado:
                    return senha
            except Exception as e:
                print(f"Senha '{senha}': ❌ erro - {e}")
        
        print("\n❌ Nenhuma senha funcionou!")
        return None

if __name__ == "__main__":
    senha_correta = testar_senhas()
