#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Financeiro Baker - Inicializador Flask CORRIGIDO
Conecta ao banco existente no Supabase
Versão: 3.1.0 - Corrigida
"""

import os
import sys
import logging
from datetime import datetime
from app import create_app, db

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_dependencias():
    """Verifica se todas as dependências críticas estão disponíveis"""
    dependencias_criticas = [
        'flask',
        'sqlalchemy',
        'pandas',
        'psycopg2',
        'flask_login'
    ]
    
    dependencias_faltantes = []
    
    for dep in dependencias_criticas:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            dependencias_faltantes.append(dep)
    
    if dependencias_faltantes:
        print(f"❌ ERRO: Dependências faltantes: {', '.join(dependencias_faltantes)}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    return True

def verificar_variaveis_ambiente():
    """Verifica se as variáveis de ambiente necessárias estão configuradas"""
    variaveis_necessarias = [
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    variaveis_faltantes = []
    
    for var in variaveis_necessarias:
        if not os.getenv(var):
            variaveis_faltantes.append(var)
    
    if variaveis_faltantes:
        print(f"⚠️ AVISO: Variáveis de ambiente não configuradas: {', '.join(variaveis_faltantes)}")
        print("💡 O sistema usará valores padrão, mas é recomendado configurar no .env")
        return False
    
    return True

def verificar_conexao_banco():
    """Verifica conexão com o banco existente"""
    try:
        from app.models.user import User
        from app.models.cte import CTE
        
        # Testar conexão básica
        db.session.execute(db.text('SELECT 1'))
        
        # Contar registros existentes
        total_ctes = CTE.query.count()
        total_users = User.query.count()
        
        print(f"✅ Conectado ao banco Supabase")
        print(f"📊 {total_ctes} CTEs encontrados")
        print(f"👥 {total_users} usuários cadastrados")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro de conexão com banco: {e}")
        print(f"❌ Erro de conexão: {e}")
        print("💡 Verificações:")
        print("   - Credenciais do Supabase estão corretas?")
        print("   - Banco está acessível?")
        print("   - Variável DATABASE_URL está configurada?")
        return False

def criar_usuario_admin():
    """Cria usuário admin se não existir - VERSÃO CORRIGIDA"""
    try:
        from app.models.user import User
        
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("🔧 Criando usuário administrador...")
            # ✅ CRIAÇÃO CORRETA DO ADMIN
            admin = User(
                username='admin',
                email='admin@dashboardbaker.com',
                nome_completo='Administrador do Sistema',
                tipo_usuario='admin',  # ← CORREÇÃO PRINCIPAL!
                ativo=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado (admin/Admin123!)")
            
        else:
            # ✅ CORRIGIR ADMIN EXISTENTE SE NECESSÁRIO
            if admin.tipo_usuario != 'admin':
                print("🔧 Corrigindo tipo do usuário admin...")
                admin.tipo_usuario = 'admin'
                admin.ativo = True
                # Opcional: Reset da senha também
                admin.set_password('Admin123!')
                db.session.commit()
                print("✅ Tipo do admin corrigido para 'admin'")
            else:
                print("✅ Usuário admin já existe e está correto")
            
        return True
        
    except Exception as e:
        logger.exception("Erro ao criar/corrigir usuário admin")
        print(f"❌ Erro ao criar/corrigir usuário: {e}")
        return False

def verificar_estrutura_banco():
    """Verifica se a estrutura do banco está correta"""
    try:
        # Verificar se a tabela principal existe
        result = db.session.execute(db.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('dashboard_baker', 'users')
        """)).fetchall()
        
        tabelas_encontradas = [row[0] for row in result]
        
        if 'dashboard_baker' not in tabelas_encontradas:
            print("⚠️ AVISO: Tabela 'dashboard_baker' não encontrada")
            print("💡 Execute as migrações do banco se necessário")
            return False
            
        print(f"✅ Estrutura do banco verificada: {len(tabelas_encontradas)} tabelas encontradas")
        return True
        
    except Exception as e:
        logger.warning(f"Não foi possível verificar estrutura do banco: {e}")
        return True  # Continua mesmo com erro na verificação

def inicializar_sistema():
    """Inicializa o sistema completo"""
    print("🚀 DASHBOARD FINANCEIRO TRANSPONTUAL- VERSÃO CORRIGIDA")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # 1. Verificar dependências
    print("🔍 Verificando dependências...")
    if not verificar_dependencias():
        return False
    print("✅ Dependências verificadas")
    
    # 2. Verificar variáveis de ambiente
    print("\n🔍 Verificando configurações...")
    verificar_variaveis_ambiente()  # Apenas aviso, não bloqueia
    
    # 3. Criar aplicação Flask
    print("\n🏗️ Criando aplicação Flask...")
    try:
        app = create_app()
        print("✅ Aplicação Flask criada")
    except Exception as e:
        print(f"❌ Erro ao criar aplicação: {e}")
        return False
    
    # 4. Verificar conexão com banco
    print("\n🔗 Conectando ao banco Supabase...")
    with app.app_context():
        if not verificar_conexao_banco():
            print("❌ Erro: Não foi possível conectar ao banco")
            return False
        
        # 5. Verificar estrutura do banco
        print("\n🔍 Verificando estrutura do banco...")
        verificar_estrutura_banco()
        
        # 6. Criar/verificar usuário admin
        print("\n👤 Configurando usuário administrador...")
        try:
            # Criar apenas tabelas que não existem (como users)
            db.create_all()
            
            if not criar_usuario_admin():
                print("⚠️ AVISO: Problema ao configurar usuário admin")
            
            # ✅ VERIFICAÇÃO FINAL DO ADMIN
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            
            if admin and admin.is_admin:
                print(f"✅ Admin verificado: {admin.username} (tipo: {admin.tipo_usuario})")
                print("👑 Módulo de administração disponível!")
            else:
                print("⚠️ AVISO: Admin pode não estar configurado corretamente")
                
        except Exception as e:
            logger.exception("Erro na configuração inicial")
            print(f"⚠️ Aviso durante configuração: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 SISTEMA PRONTO PARA USO!")
    print("🌐 Servidor iniciado em: http://localhost:5000")
    print("👤 Login: admin")
    print("🔑 Senha: Admin123!")
    print("📊 Usando banco existente com seus dados")
    print("👑 Módulo Admin: Menu aparecerá após login")
    print("💰 Sistema de Baixas: Disponível no menu")
    print("📈 Análise Financeira: Dashboard completo")
    print("=" * 60)
    print("💡 Pressione Ctrl+C para parar o servidor")
    print()
    
    return app

def main():
    """Função principal CORRIGIDA"""
    try:
        # Inicializar sistema
        app = inicializar_sistema()
        if not app:
            print("❌ Falha na inicialização do sistema")
            sys.exit(1)
        
        # Executar aplicação
        print("🚀 Iniciando servidor Flask...")
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard Baker encerrado pelo usuário!")
        
    except Exception as e:
        logger.exception("Erro crítico durante execução")
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("💡 Verifique os logs para mais detalhes")
        sys.exit(1)

if __name__ == '__main__':
    # Configurar encoding para evitar problemas com caracteres especiais
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    main()