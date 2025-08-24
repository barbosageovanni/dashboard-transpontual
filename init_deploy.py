#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialização para Deploy - Dashboard Baker
Executa configurações necessárias após deploy
"""

import os
import sys
from datetime import datetime

def init_deploy():
    """Função principal de inicialização"""
    print("🚀 INICIANDO CONFIGURAÇÃO PÓS-DEPLOY")
    print("=" * 50)
    
    try:
        # Importar app
        from app import create_app, db
        from app.models.user import User
        from app.models.cte import CTE
        
        # Criar contexto da aplicação
        app = create_app()
        
        with app.app_context():
            
            # 1. VERIFICAR CONEXÃO COM BANCO
            print("📊 1. Verificando conexão com banco de dados...")
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                print("   ✅ Conexão com banco OK")
            except Exception as e:
                print(f"   ❌ Erro na conexão: {e}")
                return False
            
            # 2. CRIAR TABELAS
            print("🗄️  2. Criando/verificando tabelas...")
            try:
                db.create_all()
                print("   ✅ Tabelas criadas/verificadas")
            except Exception as e:
                print(f"   ❌ Erro ao criar tabelas: {e}")
                return False
            
            # 3. VERIFICAR/CRIAR USUÁRIO ADMIN
            print("👤 3. Verificando usuário administrador...")
            try:
                admin_count = User.query.filter_by(tipo_usuario='admin', ativo=True).count()
                
                if admin_count == 0:
                    print("   ⚠️  Nenhum admin encontrado, criando admin inicial...")
                    sucesso, resultado = User.criar_admin_inicial()
                    
                    if sucesso:
                        print("   ✅ Admin criado com sucesso")
                        print(f"   📋 {resultado}")
                    else:
                        print(f"   ❌ Erro ao criar admin: {resultado}")
                        return False
                else:
                    print(f"   ✅ {admin_count} administrador(es) encontrado(s)")
                    
            except Exception as e:
                print(f"   ❌ Erro na verificação de admin: {e}")
                return False
            
            # 4. VERIFICAR ESTRUTURA DOS MODELOS
            print("🏗️  4. Verificando estrutura dos modelos...")
            try:
                # Testar modelo CTE
                total_ctes = CTE.query.count()
                print(f"   📋 CTEs no sistema: {total_ctes}")
                
                # Testar modelo User
                total_users = User.query.count()
                print(f"   👥 Usuários no sistema: {total_users}")
                
                print("   ✅ Modelos funcionando corretamente")
                
            except Exception as e:
                print(f"   ❌ Erro nos modelos: {e}")
                return False
            
            # 5. CONFIGURAÇÕES DE PRODUÇÃO
            print("⚙️  5. Aplicando configurações de produção...")
            try:
                # Verificar variáveis de ambiente críticas
                env_vars = {
                    'FLASK_ENV': os.environ.get('FLASK_ENV'),
                    'SECRET_KEY': 'SET' if os.environ.get('SECRET_KEY') else 'NOT_SET',
                    'DATABASE_URL': 'SET' if os.environ.get('DATABASE_URL') else 'NOT_SET',
                }
                
                print("   📋 Variáveis de ambiente:")
                for var, value in env_vars.items():
                    status = "✅" if value not in [None, 'NOT_SET'] else "⚠️ "
                    print(f"      {status} {var}: {value}")
                
                # Verificar se está em produção
                if os.environ.get('FLASK_ENV') == 'production':
                    print("   🏭 Modo produção ativado")
                else:
                    print("   🔧 Modo desenvolvimento detectado")
                
            except Exception as e:
                print(f"   ❌ Erro nas configurações: {e}")
            
            # 6. TESTAR FUNCIONALIDADES CRÍTICAS
            print("🧪 6. Testando funcionalidades críticas...")
            try:
                # Testar criação de CTE (se não existir nenhum)
                if CTE.query.count() == 0:
                    print("   📝 Criando CTE de exemplo...")
                    cte_exemplo = CTE(
                        numero_cte=999999,
                        destinatario_nome="Sistema - Teste Deploy",
                        valor_total=0.01,
                        observacao="CTE criado durante inicialização do sistema"
                    )
                    db.session.add(cte_exemplo)
                    db.session.commit()
                    print("   ✅ CTE de exemplo criado")
                
                print("   ✅ Funcionalidades testadas com sucesso")
                
            except Exception as e:
                print(f"   ⚠️  Erro nos testes (não crítico): {e}")
            
            # 7. RELATÓRIO FINAL
            print("📊 7. Relatório final do sistema...")
            try:
                stats = {
                    'total_ctes': CTE.query.count(),
                    'total_users': User.query.count(),
                    'admin_users': User.query.filter_by(tipo_usuario='admin', ativo=True).count(),
                    'timestamp': datetime.now().isoformat()
                }
                
                print("   📈 Estatísticas finais:")
                for key, value in stats.items():
                    print(f"      • {key}: {value}")
                
            except Exception as e:
                print(f"   ⚠️  Erro no relatório: {e}")
    
    except Exception as e:
        print(f"❌ ERRO CRÍTICO NA INICIALIZAÇÃO: {e}")
        return False
    
    print("=" * 50)
    print("🎉 INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("🌐 Sistema pronto para receber tráfego")
    return True

def verificar_saude():
    """Verificação rápida de saúde do sistema"""
    print("🔍 Verificação de saúde do sistema...")
    
    try:
        from app import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Testar banco
            db.session.execute(text('SELECT 1'))
            print("✅ Banco de dados: OK")
            
            # Testar modelos
            from app.models.user import User
            from app.models.cte import CTE
            
            User.query.count()
            print("✅ Modelo User: OK")
            
            CTE.query.count()
            print("✅ Modelo CTE: OK")
            
            print("🎉 Sistema totalmente operacional!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "health":
            return verificar_saude()
        elif command == "init":
            return init_deploy()
        else:
            print("Comandos disponíveis: init, health")
            return False
    else:
        # Executar inicialização por padrão
        return init_deploy()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)