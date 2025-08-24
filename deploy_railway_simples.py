#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Passo a Passo - Railway
"""

import subprocess
import sys

def executar_comando(comando):
    """Executa comando e mostra output em tempo real"""
    print(f"\n🔄 Executando: {comando}")
    print("-" * 50)
    
    try:
        result = subprocess.run(comando, shell=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚄 DEPLOY RAILWAY - PASSO A PASSO")
    print("=" * 50)
    
    comandos = [
        ("railway login", "Fazer login no Railway"),
        ("railway init", "Criar/conectar projeto"), 
        ("railway up", "Fazer deploy")
    ]
    
    for comando, descricao in comandos:
        print(f"\n📋 {descricao}")
        input("Pressione ENTER para continuar...")
        
        if not executar_comando(comando):
            print(f"❌ Erro em: {comando}")
            resposta = input("Continuar mesmo assim? (s/N): ")
            if resposta.lower() != 's':
                print("👋 Deploy interrompido")
                return False
    
    print("\n🎉 DEPLOY CONCLUÍDO!")
    print("📊 Painel: https://railway.app/dashboard")
    print("\n📋 Configure as variáveis de ambiente:")
    print("- FLASK_ENV=production")
    print("- SECRET_KEY=sua-chave-secreta-forte")
    
    return True

if __name__ == "__main__":
    main()
