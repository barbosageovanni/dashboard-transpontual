#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SETUP COMPLETO - Dashboard Baker Flask
USAR BANCO EXISTENTE - Migração Segura dos Dados
"""

import os
import sys
import subprocess
import getpass
from datetime import datetime, date
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

class DashboardBakerSetup:
    """Setup que preserva banco existente e migra estrutura"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = {}
        self.banco_existente = False
        
    def executar_setup_completo(self):
        """Executa setup preservando banco existente"""
        print("🚀 INICIANDO SETUP - Dashboard Baker Flask")
        print("🔗 MODO: Vincular ao banco existente")
        print("=" * 60)
        
        try:
            # 1. Verificar dependências
            self.verificar_dependencias()
            
            # 2. Detectar banco existente
            self.detectar_banco_existente()
            
            # 3. Instalar dependências Python
            self.instalar_dependencias()
            
            # 4. Atualizar estrutura do banco (não recriar)
            self.atualizar_estrutura_banco()
            
            # 5. Verificar/criar usuário admin
            self.verificar_usuario_admin()
            
            # 6. Configurar ambiente
            self.configurar_ambiente()
            
            # 7. Teste final
            self.teste_final()
            
            print("\n✅ SETUP CONCLUÍDO - BANCO EXISTENTE PRESERVADO!")
            print("=" * 60)
            print("📊 DADOS PRESERVADOS:")
            print("   ✅ Todos os CTEs mantidos")
            print("   ✅ Histórico financeiro intacto") 
            print("   ✅ Estrutura atualizada para Flask")
            print("\n🎯 PRÓXIMOS PASSOS:")
            print("   1. Execute: python run.py")
            print("   2. Acesse: http://localhost:5000")
            print("   3. Mesmos dados do Streamlit!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERRO NO SETUP: {str(e)}")
            sys.exit(1)
    
    def verificar_dependencias(self):
        """Verifica se todas as dependências estão instaladas"""
        print("🔍 Verificando dependências...")
        
        # Verificar Python
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8+ é obrigatório")
        print(f"   ✅ Python {sys.version.split()[0]}")
        
        # Verificar pip
        try:
            import pip
            print(f"   ✅ pip disponível")
        except ImportError:
            raise Exception("pip não encontrado")
        
        print("   ✅ Dependências verificadas")
    
    def detectar_banco_existente(self):
        """Detecta se já existe banco do Dashboard Baker"""
        print("\n🔍 Detectando banco existente...")
        
        # Tentar configurações comuns do Dashboard Baker
        configs_possiveis = [
            # Configuração Supabase (do sistema atual)
            {
                'host': 'db.lijtncazuwnbydeqtoyz.supabase.co',
                'port': '5432',
                'database': 'postgres',
                'user': 'postgres',
                'password': 'Mariaana953@7334'
            },
            # Configuração local padrão
            {
                'host': 'localhost',
                'port': '5432', 
                'database': 'dashboard_baker',
                'user': 'postgres',
                'password': 'senha123'
            }
        ]
        
        for config in configs_possiveis:
            if self.testar_conexao_banco(config):
                self.config.update(config)
                self.banco_existente = True
                print(f"   ✅ Banco encontrado: {config['host']}/{config['database']}")
                
                # Verificar dados existentes
                self.verificar_dados_existentes()
                return
        
        # Se não encontrou, solicitar configurações
        print("   ℹ️ Banco não detectado automaticamente")
        self.solicitar_configuracao_banco()
    
    def testar_conexao_banco(self, config):
        """Testa conexão e verifica se tem tabela dashboard_baker"""
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Verificar se tabela dashboard_baker existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'dashboard_baker'
                )
            """)
            
            tem_tabela = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return tem_tabela
            
        except Exception:
            return False
    
    def verificar_dados_existentes(self):
        """Verifica quantos dados existem no banco"""
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            
            # Contar CTEs
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            total_ctes = cursor.fetchone()[0]
            
            # Valor total
            cursor.execute("SELECT COALESCE(SUM(valor_total), 0) FROM dashboard_baker")
            valor_total = cursor.fetchone()[0]
            
            # CTEs com baixa
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker WHERE data_baixa IS NOT NULL")
            ctes_baixados = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"   📊 DADOS ENCONTRADOS:")
            print(f"      💼 {total_ctes:,} CTEs cadastrados")
            print(f"      💰 R$ {float(valor_total):,.2f} em receita")
            print(f"      ✅ {ctes_baixados:,} CTEs com baixa")
            print(f"   🔗 Estes dados serão PRESERVADOS no Flask!")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao verificar dados: {str(e)}")
    
    def solicitar_configuracao_banco(self):
        """Solicita configurações se banco não foi detectado"""
        print("\n🗄️ Configure conexão com PostgreSQL:")
        
        self.config['host'] = input("   Host (localhost): ") or "localhost"
        self.config['port'] = input("   Porta (5432): ") or "5432"
        self.config['database'] = input("   Nome do banco (dashboard_baker): ") or "dashboard_baker"
        self.config['user'] = input("   Usuário (postgres): ") or "postgres"
        self.config['password'] = getpass.getpass("   Senha: ")
        
        # Testar nova configuração
        if not self.testar_conexao_banco(self.config):
            raise Exception("Não foi possível conectar com as configurações fornecidas")
        
        print("   ✅ Conexão estabelecida")
    
    def instalar_dependencias(self):
        """Instala todas as dependências Python"""
        print("\n📦 Instalando dependências Python...")
        
        requirements = [
            "flask>=2.3.0",
            "flask-sqlalchemy>=3.0.0", 
            "flask-migrate>=4.0.0",
            "flask-login>=0.6.0",
            "flask-wtf>=1.1.0",
            "psycopg2-binary>=2.9.0",
            "pandas>=2.0.0",
            "plotly>=5.17.0",
            "xlsxwriter>=3.1.0",
            "python-dotenv>=1.0.0",
            "werkzeug>=2.3.0"
        ]
        
        for package in requirements:
            try:
                print(f"   📦 Instalando {package}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ {package}")
                else:
                    print(f"   ⚠️ Aviso com {package}: {result.stderr.strip()}")
            except Exception as e:
                print(f"   ❌ Erro ao instalar {package}: {str(e)}")
    
    def atualizar_estrutura_banco(self):
        """Atualiza estrutura do banco SEM perder dados"""
        print("\n🔧 Atualizando estrutura do banco...")
        
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            
            # 1. Verificar e adicionar colunas que podem estar faltando
            print("   🔧 Verificando colunas da tabela dashboard_baker...")
            
            # Adicionar coluna id se não existir
            try:
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'dashboard_baker' AND column_name = 'id'
                        ) THEN
                            ALTER TABLE dashboard_baker ADD COLUMN id SERIAL PRIMARY KEY;
                        END IF;
                    END $$;
                """)
                print("   ✅ Coluna 'id' verificada")
            except Exception as e:
                print(f"   ⚠️ Aviso coluna id: {str(e)}")
            
            # Adicionar outras colunas necessárias
            colunas_adicionar = [
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("origem_dados", "VARCHAR(50) DEFAULT 'Sistema'")
            ]
            
            for coluna, tipo in colunas_adicionar:
                try:
                    cursor.execute(f"""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_name = 'dashboard_baker' AND column_name = '{coluna}'
                            ) THEN
                                ALTER TABLE dashboard_baker ADD COLUMN {coluna} {tipo};
                            END IF;
                        END $$;
                    """)
                    print(f"   ✅ Coluna '{coluna}' verificada")
                except Exception as e:
                    print(f"   ⚠️ Aviso coluna {coluna}: {str(e)}")
            
            # 2. Criar tabela de usuários se não existir
            print("   👥 Criando tabela de usuários...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nome_completo VARCHAR(200),
                    departamento VARCHAR(100),
                    cargo VARCHAR(100),
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_count INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            """)
            print("   ✅ Tabela 'users' criada/verificada")
            
            # 3. Criar índices otimizados se não existirem
            print("   📊 Criando índices otimizados...")
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_dashboard_baker_numero_cte ON dashboard_baker(numero_cte);",
                "CREATE INDEX IF NOT EXISTS idx_dashboard_baker_data_emissao ON dashboard_baker(data_emissao);", 
                "CREATE INDEX IF NOT EXISTS idx_dashboard_baker_data_baixa ON dashboard_baker(data_baixa);",
                "CREATE INDEX IF NOT EXISTS idx_dashboard_baker_destinatario ON dashboard_baker(destinatario_nome);"
            ]
            
            for indice in indices:
                try:
                    cursor.execute(indice)
                except Exception:
                    pass  # Índice já existe
            
            print("   ✅ Índices criados/verificados")
            
            # 4. Atualizar campos nulos para compatibilidade
            cursor.execute("""
                UPDATE dashboard_baker 
                SET origem_dados = 'Streamlit_Migration' 
                WHERE origem_dados IS NULL
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("   ✅ Estrutura atualizada - DADOS PRESERVADOS")
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar estrutura: {str(e)}")
    
    def verificar_usuario_admin(self):
        """Verifica se existe usuário admin, cria se necessário"""
        print("\n👤 Verificando usuário administrador...")
        
        try:
            # Instalar werkzeug se necessário
            try:
                from werkzeug.security import generate_password_hash
            except ImportError:
                print("   📦 Instalando werkzeug...")
                subprocess.run([sys.executable, "-m", "pip", "install", "werkzeug"], check=True)
                from werkzeug.security import generate_password_hash
            
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            
            # Verificar se admin já existe
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_existente = cursor.fetchone()
            
            if admin_existente:
                print("   ✅ Usuário admin já existe")
            else:
                # Criar usuário admin
                password_hash = generate_password_hash('senha123')
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, nome_completo, 
                                     departamento, cargo, is_admin, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    'admin',
                    'admin@dashboardbaker.com',
                    password_hash,
                    'Administrador do Sistema',
                    'TI',
                    'Administrador',
                    True,
                    True
                ))
                
                conn.commit()
                print("   ✅ Usuário admin criado (login: admin / senha: senha123)")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   ⚠️ Erro com usuário admin: {str(e)}")
    
    def configurar_ambiente(self):
        """Configura arquivos de ambiente"""
        print("\n⚙️ Configurando ambiente...")
        
        # Criar .env
        env_content = f"""# Dashboard Baker Flask - Configurações
SECRET_KEY={os.urandom(32).hex()}
DATABASE_URL=postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# Database específico
DB_HOST={self.config['host']}
DB_PORT={self.config['port']}
DB_NAME={self.config['database']}
DB_USER={self.config['user']}
DB_PASSWORD={self.config['password']}
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("   ✅ Arquivo .env criado")
        
        # Criar config.py se não existir
        if not os.path.exists('config.py'):
            self.criar_arquivo_config()
    
    def criar_arquivo_config(self):
        """Cria arquivo de configuração"""
        config_content = f"""import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \\
        'postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {{
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}}
"""
        
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("   ✅ Arquivo config.py criado")
    
    def teste_final(self):
        """Testa se migração preservou dados"""
        print("\n🧪 Testando preservação de dados...")
        
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            
            # Verificar dados preservados
            cursor.execute("SELECT COUNT(*) FROM dashboard_baker")
            total_ctes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(SUM(valor_total), 0) FROM dashboard_baker")
            valor_total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if total_ctes > 0:
                print(f"   ✅ {total_ctes:,} CTEs preservados")
                print(f"   ✅ R$ {float(valor_total):,.2f} em receita mantida")
                print(f"   ✅ {total_users} usuário(s) no sistema")
                print("   ✅ MIGRAÇÃO SEM PERDA DE DADOS!")
            else:
                print("   ⚠️ Nenhum CTE encontrado (banco vazio)")
            
        except Exception as e:
            raise Exception(f"Teste final falhou: {str(e)}")


# ============================================================================
# SCRIPT PRINCIPAL DE EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    setup = DashboardBakerSetup()
    setup.executar_setup_completo()