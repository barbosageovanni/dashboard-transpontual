#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Rápido do Sistema CTEs - VERSÃO SIMPLIFICADA
teste_rapido_sistema.py - PARA TESTAR SEM CONTEXTO FLASK COMPLEXO
"""

import os
import sys
import requests
import json
from datetime import datetime

def testar_via_api():
    """Testa o sistema via requisições HTTP para as APIs"""
    print("🧪 TESTE RÁPIDO VIA API")
    print("=" * 50)
    
    # Configurar base URL
    base_url = "http://localhost:5000"
    
    # Se estiver rodando em outra porta, ajuste aqui
    if len(sys.argv) > 1:
        try:
            porta = int(sys.argv[1])
            base_url = f"http://localhost:{porta}"
        except:
            pass
    
    print(f"🌐 Testando servidor em: {base_url}")
    
    testes = {
        'servidor_respondendo': False,
        'api_test_conexao': False,
        'api_listar_simples': False,
        'api_listar_completa': False,
        'diagnostico_disponivel': False
    }
    
    detalhes = {}
    
    # ==================== TESTE 1: SERVIDOR RESPONDENDO ====================
    print("\n1️⃣ Testando se o servidor está rodando...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code < 500:
            testes['servidor_respondendo'] = True
            print("✅ Servidor está respondendo")
        else:
            print(f"⚠️ Servidor respondendo com erro {response.status_code}")
    except Exception as e:
        print(f"❌ Servidor não responde: {e}")
        print("💡 Verifique se o Flask está rodando e na porta correta")
        return testes, detalhes
    
    # ==================== TESTE 2: API DE TESTE DE CONEXÃO ====================
    print("\n2️⃣ Testando API de conexão...")
    try:
        response = requests.get(f"{base_url}/ctes/api/test-conexao", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('conexao') == 'OK':
                testes['api_test_conexao'] = True
                detalhes['total_ctes'] = data.get('total_ctes', 0)
                print(f"✅ API de conexão OK - {detalhes['total_ctes']} CTEs no banco")
            else:
                print(f"⚠️ API de conexão com problemas: {data}")
        elif response.status_code == 401:
            print("⚠️ API requer autenticação - teste será limitado")
            testes['api_test_conexao'] = 'REQUER_LOGIN'
        else:
            print(f"❌ API de conexão falhou: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            except:
                print(f"   Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro ao testar API de conexão: {e}")
    
    # ==================== TESTE 3: API DE LISTAGEM SIMPLES ====================
    print("\n3️⃣ Testando API de listagem simples...")
    try:
        response = requests.get(f"{base_url}/ctes/api/listar-simples?per_page=5", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                testes['api_listar_simples'] = True
                detalhes['ctes_retornados'] = len(data.get('data', []))
                print(f"✅ API listagem simples OK - {detalhes['ctes_retornados']} CTEs retornados")
                
                # Mostrar exemplo de dados se houver
                if data.get('data'):
                    exemplo = data['data'][0]
                    print(f"   Exemplo: CTE {exemplo.get('numero_cte')} - {exemplo.get('destinatario_nome', 'N/A')}")
            else:
                print(f"⚠️ API listagem simples retornou erro: {data.get('error', 'Erro desconhecido')}")
        elif response.status_code == 401:
            print("⚠️ API de listagem requer autenticação")
        else:
            print(f"❌ API listagem simples falhou: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('error', 'Erro desconhecido')}")
            except:
                pass
    except Exception as e:
        print(f"❌ Erro ao testar API de listagem simples: {e}")
    
    # ==================== TESTE 4: API DE LISTAGEM COMPLETA ====================
    print("\n4️⃣ Testando API de listagem completa...")
    try:
        response = requests.get(f"{base_url}/ctes/api/listar?per_page=10", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                testes['api_listar_completa'] = True
                total_encontrado = data.get('pagination', {}).get('total', 0)
                detalhes['total_paginado'] = total_encontrado
                print(f"✅ API listagem completa OK - {total_encontrado} CTEs total")
            else:
                print(f"⚠️ API listagem completa com problemas: {data.get('error', 'Erro desconhecido')}")
        elif response.status_code == 401:
            print("⚠️ API de listagem completa requer autenticação")
        else:
            print(f"❌ API listagem completa falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar API de listagem completa: {e}")
    
    # ==================== TESTE 5: API DE DIAGNÓSTICO ====================
    print("\n5️⃣ Testando API de diagnóstico...")
    try:
        response = requests.get(f"{base_url}/ctes/api/diagnostico-simples", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                testes['diagnostico_disponivel'] = True
                diagnostico = data.get('diagnostico_simples', {})
                resumo = diagnostico.get('resumo_rapido', {})
                print(f"✅ API de diagnóstico OK - Status: {resumo.get('status', 'Desconhecido')}")
                
                # Mostrar testes básicos
                testes_basicos = diagnostico.get('testes_basicos', {})
                for nome, resultado in testes_basicos.items():
                    print(f"   {nome}: {resultado}")
                    
            else:
                print(f"⚠️ API de diagnóstico com problemas: {data.get('error', 'Erro desconhecido')}")
        elif response.status_code == 401:
            print("⚠️ API de diagnóstico requer autenticação")
        elif response.status_code == 404:
            print("⚠️ API de diagnóstico não encontrada - adicione às rotas")
        else:
            print(f"❌ API de diagnóstico falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar API de diagnóstico: {e}")
    
    return testes, detalhes

def testar_arquivos_locais():
    """Testa se os arquivos importantes existem no sistema"""
    print("\n📁 VERIFICANDO ARQUIVOS DO SISTEMA")
    print("=" * 40)
    
    arquivos_importantes = {
        'app/__init__.py': 'Arquivo principal da aplicação',
        'app/models/cte.py': 'Modelo CTE',
        'app/routes/ctes.py': 'Rotas dos CTEs', 
        'app/utils/date_utils.py': 'Utilitário de datas (correção)',
        'requirements.txt': 'Dependências',
        'run.py': 'Script de inicialização',
        'app.py': 'Script de inicialização alternativo'
    }
    
    arquivos_encontrados = {}
    
    for arquivo, descricao in arquivos_importantes.items():
        if os.path.exists(arquivo):
            try:
                tamanho = os.path.getsize(arquivo)
                arquivos_encontrados[arquivo] = {
                    'existe': True,
                    'tamanho': tamanho,
                    'descricao': descricao
                }
                print(f"✅ {arquivo} - {tamanho} bytes")
            except Exception as e:
                arquivos_encontrados[arquivo] = {
                    'existe': True,
                    'erro': str(e),
                    'descricao': descricao
                }
                print(f"⚠️ {arquivo} - erro ao ler: {e}")
        else:
            arquivos_encontrados[arquivo] = {
                'existe': False,
                'descricao': descricao
            }
            print(f"❌ {arquivo} - não encontrado")
    
    return arquivos_encontrados

def gerar_relatorio(testes, detalhes, arquivos):
    """Gera relatório final do teste"""
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    # Contar sucessos
    sucessos = sum(1 for v in testes.values() if v is True)
    total_testes = len(testes)
    
    print(f"\n🎯 RESULTADO GERAL: {sucessos}/{total_testes} testes passaram")
    
    # Status geral
    if sucessos == total_testes:
        status = "✅ SISTEMA FUNCIONANDO PERFEITAMENTE"
        cor = "VERDE"
    elif sucessos >= total_testes * 0.8:
        status = "🟡 SISTEMA FUNCIONANDO COM PEQUENOS PROBLEMAS"
        cor = "AMARELO" 
    elif sucessos >= total_testes * 0.5:
        status = "🟠 SISTEMA COM PROBLEMAS SIGNIFICATIVOS"
        cor = "LARANJA"
    else:
        status = "🔴 SISTEMA COM PROBLEMAS CRÍTICOS"
        cor = "VERMELHO"
    
    print(f"\n{status}")
    
    # Detalhes dos testes
    print(f"\n📋 DETALHES DOS TESTES:")
    for teste, resultado in testes.items():
        if resultado is True:
            print(f"   ✅ {teste.replace('_', ' ').title()}")
        elif resultado is False:
            print(f"   ❌ {teste.replace('_', ' ').title()}")
        else:
            print(f"   ⚠️ {teste.replace('_', ' ').title()}: {resultado}")
    
    # Informações úteis
    if detalhes:
        print(f"\n📊 INFORMAÇÕES:")
        for key, value in detalhes.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    # Arquivos críticos faltando
    arquivos_faltando = [nome for nome, info in arquivos.items() if not info['existe']]
    if arquivos_faltando:
        print(f"\n❗ ARQUIVOS CRÍTICOS FALTANDO:")
        for arquivo in arquivos_faltando[:3]:  # Mostrar apenas os 3 primeiros
            print(f"   • {arquivo}")
    
    # Próximas ações recomendadas
    print(f"\n🔧 PRÓXIMAS AÇÕES RECOMENDADAS:")
    
    if cor == "VERDE":
        print("   • Sistema funcionando bem!")
        print("   • Execute diagnóstico completo via API se precisar de mais detalhes")
        print("   • Continue o desenvolvimento normal")
    elif cor == "AMARELO":
        print("   • Verifique os testes que falharam")
        print("   • Considere implementar as correções sugeridas")
        print("   • Sistema está utilizável mas pode melhorar")
    elif cor == "LARANJA":
        print("   • Implemente os artefatos de correção fornecidos")
        print("   • Verifique logs do servidor Flask")
        print("   • Teste cada API individualmente")
    else:  # VERMELHO
        print("   • 🚨 AÇÃO IMEDIATA NECESSÁRIA")
        print("   • Verificar se o servidor Flask está rodando")
        print("   • Implementar TODOS os artefatos de correção")
        print("   • Verificar configuração do banco de dados")
        print("   • Reiniciar a aplicação")
    
    # Comandos úteis
    print(f"\n💡 COMANDOS ÚTEIS:")
    print("   • Para testar APIs: curl http://localhost:5000/ctes/api/test-conexao")
    print("   • Para ver logs: tail -f nohup.out (se usando nohup)")
    print("   • Para diagnóstico via browser: http://localhost:5000/ctes/api/diagnostico-simples")
    
    # Salvar relatório em arquivo
    relatorio_completo = {
        'timestamp': datetime.now().isoformat(),
        'status_geral': status,
        'cor': cor,
        'sucessos': sucessos,
        'total_testes': total_testes,
        'testes': testes,
        'detalhes': detalhes,
        'arquivos': arquivos
    }
    
    nome_arquivo = f"teste_rapido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {nome_arquivo}")
    
    return status, cor

def main():
    """Função principal"""
    print("🚀 TESTE RÁPIDO DO SISTEMA CTEs")
    print("Versão simplificada - sem contexto Flask complexo")
    print("=" * 60)
    
    # Executar testes
    testes, detalhes = testar_via_api()
    arquivos = testar_arquivos_locais()
    
    # Gerar relatório final
    status, cor = gerar_relatorio(testes, detalhes, arquivos)
    
    print(f"\n🏁 TESTE CONCLUÍDO - STATUS: {cor}")
    
    # Retornar código de saída apropriado
    if cor == "VERDE":
        return 0  # Sucesso
    elif cor in ["AMARELO", "LARANJA"]:
        return 1  # Problemas menores
    else:
        return 2  # Problemas críticos

if __name__ == "__main__":
    import sys
    
    print("📋 Uso: python teste_rapido_sistema.py [porta]")
    print("Exemplo: python teste_rapido_sistema.py 5000")
    print()
    
    try:
        codigo_saida = main()
        sys.exit(codigo_saida)
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
        sys.exit(3)
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(4)