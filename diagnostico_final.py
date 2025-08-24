#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Final - Por que o sistema não carrega a interface nova?
diagnostico_final.py
"""

import subprocess
import sys
import os

def verificar_dependencias():
    """Verifica se dependências críticas estão instaladas"""
    print("🔍 VERIFICANDO DEPENDÊNCIAS CRÍTICAS:")
    print("=" * 50)
    
    dependencias = {
        'scipy': 'pip install scipy',
        'pandas': 'pip install pandas', 
        'dateutil': 'pip install python-dateutil'
    }
    
    faltando = []
    
    for dep, comando in dependencias.items():
        try:
            if dep == 'dateutil':
                import dateutil
            else:
                __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - FALTANDO!")
            faltando.append(comando)
    
    if faltando:
        print(f"\n🔧 INSTALAR DEPENDÊNCIAS FALTANDO:")
        for comando in faltando:
            print(f"   {comando}")
        return False
    else:
        print(f"\n✅ Todas as dependências estão instaladas")
        return True

def verificar_servidor():
    """Verifica se servidor está rodando e qual porta"""
    print(f"\n🔍 VERIFICANDO SERVIDOR:")
    print("=" * 50)
    
    try:
        import requests
        
        urls_teste = [
            'http://localhost:5000',
            'http://127.0.0.1:5000',
            'http://localhost:8000',
            'http://127.0.0.1:8000'
        ]
        
        servidor_ativo = None
        for url in urls_teste:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    servidor_ativo = url
                    print(f"✅ Servidor ativo em: {url}")
                    break
            except:
                continue
        
        if not servidor_ativo:
            print("❌ Nenhum servidor Flask detectado!")
            print("🔧 SOLUÇÃO: Execute 'python iniciar.py'")
            return None
        
        # Testar rota específica de análise financeira
        try:
            analise_url = f"{servidor_ativo}/analise-financeira/"
            response = requests.get(analise_url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Rota análise financeira OK: {analise_url}")
                
                # Verificar se retorna a interface nova
                content = response.text
                if 'projecoes-tab' in content:
                    print("✅ Interface nova sendo servida!")
                    return servidor_ativo
                else:
                    print("❌ Interface ANTIGA sendo servida (cache ou template errado)")
                    return "INTERFACE_ANTIGA"
            else:
                print(f"❌ Rota análise financeira ERRO: {response.status_code}")
                return "ERRO_ROTA"
                
        except Exception as e:
            print(f"❌ Erro ao testar rota: {str(e)}")
            return "ERRO_CONEXAO"
            
    except ImportError:
        print("⚠️ requests não instalado - não foi possível testar servidor")
        return "REQUESTS_FALTANDO"

def verificar_processo_flask():
    """Verifica processos Flask rodando"""
    print(f"\n🔍 VERIFICANDO PROCESSOS FLASK:")
    print("=" * 50)
    
    try:
        # Windows
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            print("✅ Processo Python detectado")
            
            # Contar processos
            linhas = [l for l in result.stdout.split('\n') if 'python.exe' in l]
            print(f"📊 {len(linhas)} processo(s) Python ativo(s)")
            
            return True
        else:
            print("❌ Nenhum processo Python ativo")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar processos: {str(e)}")
        return False

def gerar_comando_teste():
    """Gera comandos específicos para testar"""
    print(f"\n🧪 COMANDOS DE TESTE:")
    print("=" * 50)
    
    comandos = [
        ("Testar importação dos serviços", 
         "python -c \"from app.services.projecoes_service import ProjecoesService; print('✅ ProjecoesService OK')\""),
        
        ("Testar rota diretamente",
         "python -c \"from app import create_app; app = create_app(); print('✅ App criada'); print([str(r) for r in app.url_map.iter_rules() if 'analise' in str(r)])\""),
        
        ("Verificar template carregado",
         "python -c \"import os; print('Template existe:', os.path.exists('app/templates/analise_financeira/index.html'))\""),
         
        ("Testar dependências críticas",
         "python -c \"import scipy, pandas, dateutil; print('✅ Todas dependências OK')\"")
    ]
    
    for desc, cmd in comandos:
        print(f"\n📝 {desc}:")
        print(f"   {cmd}")

def main():
    print("🎯 DIAGNÓSTICO FINAL - POR QUE NÃO FUNCIONA?")
    print("=" * 60)
    print("📋 Baseado no diagnóstico anterior:")
    print("   ✅ Todos os arquivos estão corretos")
    print("   ✅ Template é a versão nova")
    print("   ✅ Blueprints registrados")
    print("   ❓ Mas interface antiga ainda aparece...")
    
    # 1. Verificar dependências
    deps_ok = verificar_dependencias()
    
    # 2. Verificar servidor
    servidor_status = verificar_servidor()
    
    # 3. Verificar processos
    processo_ok = verificar_processo_flask()
    
    # 4. Gerar comandos de teste
    gerar_comando_teste()
    
    # 5. DIAGNÓSTICO FINAL
    print(f"\n🎯 DIAGNÓSTICO FINAL:")
    print("=" * 60)
    
    problemas = []
    
    if not deps_ok:
        problemas.append("❌ Dependências faltando (scipy, dateutil)")
    
    if servidor_status == "INTERFACE_ANTIGA":
        problemas.append("❌ Servidor serve interface antiga (cache/restart needed)")
    elif servidor_status == "ERRO_ROTA":
        problemas.append("❌ Rota de análise financeira com erro")
    elif servidor_status == "ERRO_CONEXAO":
        problemas.append("❌ Servidor não responde")
    elif servidor_status is None:
        problemas.append("❌ Servidor não está rodando")
    
    if not processo_ok:
        problemas.append("❌ Processo Flask não ativo")
    
    if problemas:
        print("🚨 PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   {problema}")
        
        print(f"\n🔧 SOLUÇÃO STEP-BY-STEP:")
        
        if not deps_ok:
            print("1️⃣ INSTALAR DEPENDÊNCIAS:")
            print("   pip install scipy python-dateutil pandas")
        
        print("2️⃣ PARAR SERVIDOR COMPLETAMENTE:")
        print("   - Fechar terminal Flask (Ctrl+C)")
        print("   - Verificar se não há outros processos Python")
        
        print("3️⃣ REINICIAR SERVIDOR:")
        print("   python iniciar.py")
        
        print("4️⃣ LIMPAR CACHE NAVEGADOR:")
        print("   - Ctrl+F5 (hard refresh)")
        print("   - Ou abrir aba anônima/privada")
        
        print("5️⃣ ACESSAR URL CORRETA:")
        print("   http://localhost:5000/analise-financeira/")
        print("   (NÃO /dashboard/ - essa é a página antiga!)")
        
        print("6️⃣ VERIFICAR CONSOLE DO NAVEGADOR:")
        print("   - F12 → Console")
        print("   - Procurar erros JavaScript")
        
    else:
        print("✅ Tudo parece estar funcionando!")
        print("🎯 VERIFICAÇÕES FINAIS:")
        print("   1. Acesse: http://localhost:5000/analise-financeira/")
        print("   2. Limpe cache: Ctrl+F5")
        print("   3. Verifique console: F12")
    
    print(f"\n💡 DICA IMPORTANTE:")
    print("Se você está acessando /dashboard/, essa é a página ANTIGA!")
    print("A nova interface está em /analise-financeira/")
    
    print("=" * 60)

if __name__ == "__main__":
    main()