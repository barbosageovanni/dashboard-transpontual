#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar usuário de teste com senha conhecida
"""

import sys
import os

# Configurar encoding UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
            print("[OK] Usuario 'teste' ja existe")
            # Testar senha
            if teste.check_password('123456'):
                print("[OK] Senha '123456' funciona")
                print("\n" + "="*50)
                print("LOGIN: usuario=teste senha=123456")
                print("="*50)
                return True
            else:
                print("[AVISO] Senha '123456' nao funciona, recriando usuario...")
                db.session.delete(teste)
                db.session.commit()

        # Criar novo usuário
        try:
            novo_usuario = User(
                username='teste',
                email='teste@teste.com',
                nome_completo='Usuario Teste',
                tipo_usuario='admin',
                ativo=True
            )
            novo_usuario.set_password('123456')

            db.session.add(novo_usuario)
            db.session.commit()

            print("[OK] Usuario 'teste' criado com senha '123456'")

            # Verificar se funcionou
            if novo_usuario.check_password('123456'):
                print("[OK] Verificacao: senha '123456' funciona")
                print("\n" + "="*50)
                print("LOGIN: usuario=teste senha=123456")
                print("="*50)
                return True
            else:
                print("[ERRO] Verificacao: senha nao funciona")
                return False

        except Exception as e:
            print(f"[ERRO] Erro ao criar usuario: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    criar_usuario_teste()
