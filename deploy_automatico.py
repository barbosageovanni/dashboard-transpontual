#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Automático para Railway - Dashboard Baker Flask
Execute este script para fazer deploy automatizado
"""

import os
import subprocess
import sys
from pathlib import Path

def executar_comando(comando, descricao):
    """Executa comando e retorna resultado"""
    print(f"🔄 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descricao} - Sucesso")
            return True, result.stdout
        else:
            print(f"❌ {descricao} - Erro: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {descricao} - Exceção: {e}")
        return False, str(e)

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    arquivos_necessarios = [
        'Procfile',
        'wsgi.py', 
        'requirements.txt',
        'railway.toml',
        'app/__init__.py'
    ]
    
    print("🔍 Verificando arquivos necessários...")
    todos_presentes = True
    
    for arquivo in arquivos_necessarios:
        if Path(arquivo).exists():
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - AUSENTE")
            todos_presentes = False
    
    return todos_presentes

def deploy_railway():
    """Faz deploy no Railway"""
    print("🚄 DEPLOY AUTOMATIZADO - RAILWAY")
    print("=" * 50)
    
    # 1. Verificar arquivos
    if not verificar_arquivos():
        print("❌ Arquivos necessários ausentes. Execute setup_deploy.py primeiro.")
        return False
    
    # 2. Verificar se Railway CLI está instalado
    print("\n🔧 Verificando Railway CLI...")
    sucesso, output = executar_comando("railway --version", "Verificar Railway CLI")
    
    if not sucesso:
        print("📦 Railway CLI não encontrado. Instalando...")
        sucesso, output = executar_comando("npm install -g @railway/cli", "Instalar Railway CLI")
        if not sucesso:
            print("❌ Erro ao instalar Railway CLI. Instale manualmente:")
            print("   npm install -g @railway/cli")
            return False
    
    # 3. Verificar se está logado
    print("\n🔑 Verificando login no Railway...")
    sucesso, output = executar_comando("railway whoami", "Verificar login")
    
    if not sucesso:
        print("🔐 Não está logado no Railway. Fazendo login...")
        print("🌐 Uma página será aberta no navegador para autenticação.")
        sucesso, output = executar_comando("railway login", "Fazer login no Railway")
        if not sucesso:
            print("❌ Erro no login. Tente manualmente: railway login")
            return False
    else:
        print(f"✅ Logado como: {output.strip()}")
    
    # 4. Verificar Git
    print("\n📝 Verificando Git...")
    sucesso, output = executar_comando("git status", "Verificar status Git")
    if not sucesso:
        print("🔧 Inicializando repositório Git...")
        executar_comando("git init", "Inicializar Git")
        executar_comando("git add .", "Adicionar arquivos")
        executar_comando('git commit -m "Deploy inicial"', "Commit inicial")
    
    # 5. Verificar se projeto está linkado
    print("\n🔗 Verificando projeto Railway...")
    sucesso, output = executar_comando("railway status", "Verificar projeto linkado")
    
    if not sucesso or "No project linked" in output:
        print("🔗 Projeto não está linkado. Criando novo projeto...")
        sucesso, output = executar_comando("railway link", "Conectar projeto")
        
        if not sucesso:
            print("🆕 Criando novo projeto no Railway...")
            sucesso, output = executar_comando("railway login", "Relogin")
            sucesso, output = executar_comando("railway init", "Criar projeto")
            
            if not sucesso:
                print("❌ Erro ao criar projeto. Tente manualmente:")
                print("   railway login")
                print("   railway init")
                return False
    
    # 6. Deploy
    print("\n🚀 Iniciando deploy no Railway...")
    print("⏳ Isso pode levar alguns minutos...")
    
    sucesso, output = executar_comando("railway up", "Deploy no Railway")
    
    if sucesso:
        print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("🌐 Sua aplicação estará disponível em alguns minutos.")
        print("📊 Acesse o painel: https://railway.app/dashboard")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure as variáveis de ambiente no painel Railway:")
        print("   - FLASK_ENV=production")
        print("   - SECRET_KEY=sua-chave-secreta-forte")
        print("2. Aguarde a aplicação inicializar")
        print("3. Teste o endpoint /health")
        return True
    else:
        print("\n❌ ERRO NO DEPLOY")
        print("🔍 Verifique:")
        print("1. Conexão com internet")
        print("2. Autenticação no Railway")
        print("3. Logs no painel Railway")
        return False

def main():
    """Função principal"""
    print("🚀 DEPLOY AUTOMÁTICO - DASHBOARD BAKER FLASK")
    print("=" * 60)
    
    # Verificar se está no diretório correto
    if not Path("app").exists():
        print("❌ Execute este script na pasta raiz do projeto!")
        return False
    
    # Menu de opções
    print("\n📋 OPÇÕES DE DEPLOY:")
    print("1. 🚄 Railway (Recomendado - Automático)")
    print("2. 📖 Mostrar instruções manuais")
    print("3. ❌ Cancelar")
    
    escolha = input("\nEscolha uma opção (1-3): ").strip()
    
    if escolha == "1":
        return deploy_railway()
    elif escolha == "2":
        print("\n📖 INSTRUÇÕES MANUAIS:")
        print("1. Railway: railway login && railway up")
        print("2. Render: Conecte seu repo em https://render.com")
        print("3. Heroku: heroku create nome-app && git push heroku main")
        print("\n📚 Veja DEPLOY_GUIDE_FINAL.md para detalhes completos")
        return True
    else:
        print("👋 Deploy cancelado")
        return True

if __name__ == "__main__":
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Deploy interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
