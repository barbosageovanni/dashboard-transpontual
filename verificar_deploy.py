#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Deploy Railway e Configurar Variáveis
"""

import subprocess
import json

def executar_comando(comando):
    """Executa comando e retorna output"""
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔍 DIAGNÓSTICO DO DEPLOY RAILWAY")
    print("=" * 50)
    
    # 1. Verificar logs de build
    print("\n📋 Verificando logs...")
    sucesso, output, error = executar_comando("railway logs")
    if sucesso:
        print("📄 Logs recentes:")
        print(output[-1000:])  # Últimas 1000 caracteres
    else:
        print(f"❌ Erro ao obter logs: {error}")
    
    # 2. Verificar variáveis de ambiente
    print("\n🔧 Configurando variáveis de ambiente...")
    
    variaveis = [
        ("FLASK_ENV", "production"),
        ("SECRET_KEY", "dashboard-baker-secret-key-production-2024-super-secure"),
        ("PORT", "8080"),
        ("PYTHONPATH", "/app")
    ]
    
    for nome, valor in variaveis:
        print(f"🔄 Configurando {nome}...")
        sucesso, output, error = executar_comando(f'railway variables set {nome}="{valor}"')
        if sucesso:
            print(f"✅ {nome} configurado")
        else:
            print(f"❌ Erro ao configurar {nome}: {error}")
    
    # 3. Redeploy
    print("\n🚀 Fazendo redeploy...")
    sucesso, output, error = executar_comando("railway up --detach")
    if sucesso:
        print("✅ Redeploy iniciado")
        print("🌐 Aguarde alguns minutos e verifique:")
        print("📊 Painel: https://railway.app/dashboard")
    else:
        print(f"❌ Erro no redeploy: {error}")
    
    return True

if __name__ == "__main__":
    main()
