#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Instalação - Sistema de Atualização CTE PostgreSQL
Automatiza a configuração para trabalhar com Supabase PostgreSQL
"""

import os
import sys
import subprocess
import json
import urllib.request
from pathlib import Path
from datetime import datetime

def print_header():
    """Exibe cabeçalho do instalador"""
    print("🚀 INSTALADOR - SISTEMA DE ATUALIZAÇÃO CTE POSTGRESQL")
    print("="*60)
    print("Este script configura o sistema de atualização em lote")
    print("para trabalhar com o banco PostgreSQL Supabase existente.\n")

def check_python_version():
    """Verifica versão do Python"""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário")
        print(f"   Versão atual: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor} - OK")
    return True

def check_flask_environment():
    """Verifica se o ambiente Flask está configurado"""
    print("\n🌐 Verificando ambiente Flask existente...")
    
    # Verifica se existe app.py ou __init__.py
    app_files = ['app.py', 'app/__init__.py', '__init__.py']
    flask_found = any(os.path.exists(f) for f in app_files)
    
    if not flask_found:
        print("⚠️ Ambiente Flask não detectado")
        print("💡 Certifique-se de executar na raiz do projeto Flask")
        return False
    
    # Verifica se existe models/cte.py
    model_files = ['app/models/cte.py', 'models/cte.py']
    model_found = any(os.path.exists(f) for f in model_files)
    
    if not model_found:
        print("⚠️ Modelo CTE não encontrado")
        print("💡 Verifique se app/models/cte.py existe")
        return False
    
    print("✅ Ambiente Flask detectado")
    return True

def install_dependencies():
    """Instala dependências específicas para PostgreSQL"""
    print("\n📦 Instalando dependências PostgreSQL...")
    
    dependencies = [
        "pandas>=1.5.0",
        "sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
        "xlsxwriter>=3.0.0",
        "openpyxl>=3.0.0",
        "python-dotenv>=0.19.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"📦 Instalando {dep.split('>=')[0]}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep, "--quiet"
            ])
            print(f"✅ {dep.split('>=')[0]} instalado")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {dep}")
            return False
    
    print("✅ Todas as dependências instaladas")
    return True

def test_database_connection():
    """Testa conexão com banco PostgreSQL"""
    print("\n🔗 Testando conexão com PostgreSQL...")
    
    try:
        # Tenta importar e testar conexão
        sys.path.append(os.getcwd())
        
        from app import create_app, db
        from app.models.cte import CTE
        
        app = create_app()
        
        with app.app_context():
            # Testa conexão básica
            total_ctes = CTE.query.count()
            
            print(f"✅ Conectado ao Supabase PostgreSQL")
            print(f"📊 {total_ctes} CTEs encontrados na tabela")
            
            # Verifica estrutura da tabela
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('dashboard_baker')]
            
            required_columns = [
                'numero_cte', 'destinatario_nome', 'valor_total', 
                'data_emissao', 'data_baixa'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                print(f"⚠️ Colunas ausentes: {missing_columns}")
            else:
                print("✅ Estrutura da tabela verificada")
            
            return True
            
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        print("💡 Verifique se o projeto Flask está configurado corretamente")
        return False
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        print("💡 Verifique as credenciais do Supabase")
        return False

def create_folder_structure():
    """Cria estrutura de pastas para o sistema"""
    print("\n📁 Criando estrutura de pastas...")
    
    folders = [
        "uploads", 
        "logs",
        "backups",
        "reports",
        "templates",
        "scripts"
    ]
    
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Pasta criada: {folder}/")
        except Exception as e:
            print(f"❌ Erro ao criar pasta {folder}: {str(e)}")
            return False
    
    return True

def create_config_files():
    """Cria arquivos de configuração específicos"""
    print("\n⚙️ Criando arquivos de configuração...")
    
    # Script de execução rápida
    quick_script = """#!/bin/bash
# Script de execução rápida - PostgreSQL

echo "🚀 SISTEMA DE ATUALIZAÇÃO CTE - POSTGRESQL"
echo "========================================="

# Verifica se está no diretório correto
if [ ! -f "bulk_update_cte.py" ]; then
    echo "❌ Execute este script no diretório do sistema de atualização"
    exit 1
fi

# Verifica arquivo de atualização
if [ -z "$1" ]; then
    echo "📄 Uso: $0 <arquivo_excel>"
    echo "Exemplo: $0 atualizacoes.xlsx"
    exit 1
fi

ARQUIVO="$1"
MODO="${2:-empty_only}"
BATCH="${3:-100}"

if [ ! -f "$ARQUIVO" ]; then
    echo "❌ Arquivo não encontrado: $ARQUIVO"
    exit 1
fi

echo "📋 Configuração:"
echo "  - Arquivo: $ARQUIVO"
echo "  - Modo: $MODO"
echo "  - Lote: $BATCH"
echo ""

# Executa com preview primeiro
echo "👁️ Preview das alterações:"
python bulk_update_cte.py --update-file "$ARQUIVO" --mode "$MODO" --preview-only

echo ""
read -p "▶️ Executar atualizações? (s/N): " CONFIRMA

if [[ $CONFIRMA =~ ^[Ss]$ ]]; then
    echo "🔄 Executando atualizações..."
    python bulk_update_cte.py --update-file "$ARQUIVO" --mode "$MODO" --batch-size "$BATCH"
else
    echo "❌ Execução cancelada"
fi
"""
    
    try:
        with open('quick_update.sh', 'w', encoding='utf-8') as f:
            f.write(quick_script)
        
        # Torna executável no Unix
        if os.name != 'nt':
            os.chmod('quick_update.sh', 0o755)
        
        print("✅ Script quick_update.sh criado")
    except Exception as e:
        print(f"❌ Erro ao criar script: {str(e)}")
        return False
    
    # Script Windows
    windows_script = """@echo off
REM Script de execução rápida - PostgreSQL Windows

echo 🚀 SISTEMA DE ATUALIZAÇÃO CTE - POSTGRESQL
echo =========================================

if "%1"=="" (
    echo 📄 Uso: %0 ^<arquivo_excel^>
    echo Exemplo: %0 atualizacoes.xlsx
    exit /b 1
)

set ARQUIVO=%1
set MODO=%2
if "%MODO%"=="" set MODO=empty_only
set BATCH=%3
if "%BATCH%"=="" set BATCH=100

if not exist "%ARQUIVO%" (
    echo ❌ Arquivo não encontrado: %ARQUIVO%
    exit /b 1
)

echo 📋 Configuração:
echo   - Arquivo: %ARQUIVO%
echo   - Modo: %MODO%
echo   - Lote: %BATCH%
echo.

echo 👁️ Preview das alterações:
python bulk_update_cte.py --update-file "%ARQUIVO%" --mode "%MODO%" --preview-only

echo.
set /p CONFIRMA="▶️ Executar atualizações? (s/N): "

if /i "%CONFIRMA%"=="s" (
    echo 🔄 Executando atualizações...
    python bulk_update_cte.py --update-file "%ARQUIVO%" --mode "%MODO%" --batch-size "%BATCH%"
) else (
    echo ❌ Execução cancelada
)

pause
"""
    
    try:
        with open('quick_update.bat', 'w', encoding='utf-8') as f:
            f.write(windows_script)
        print("✅ Script quick_update.bat criado")
    except Exception as e:
        print(f"❌ Erro ao criar script BAT: {str(e)}")
        return False
    
    # Arquivo de configuração do sistema
    system_config = {
        "sistema": {
            "nome": "Sistema de Atualização CTE PostgreSQL",
            "versao": "2.0.0",
            "banco": "PostgreSQL Supabase",
            "tabela": "dashboard_baker"
        },
        "database": {
            "host": "db.lijtncazuwnbydeqtoyz.supabase.co",
            "port": 5432,
            "database": "postgres",
            "ssl_required": True
        },
        "performance": {
            "batch_size_default": 100,
            "max_batch_size": 500,
            "timeout_seconds": 300,
            "retry_attempts": 3
        },
        "backup": {
            "auto_backup": True,
            "format": "json",
            "max_backups": 15,
            "compress": False
        },
        "validation": {
            "required_fields": ["numero_cte"],
            "date_fields": [
                "data_emissao", "data_baixa", "data_inclusao_fatura",
                "data_envio_processo", "primeiro_envio", "data_rq_tmc",
                "data_atesto", "envio_final"
            ],
            "numeric_fields": ["valor_total"],
            "max_cte_number": 999999999
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "max_log_files": 30,
            "auto_cleanup_days": 30
        }
    }
    
    try:
        os.makedirs('config', exist_ok=True)
        with open('config/system.json', 'w', encoding='utf-8') as f:
            json.dump(system_config, f, indent=2, ensure_ascii=False)
        print("✅ Arquivo config/system.json criado")
    except Exception as e:
        print(f"❌ Erro ao criar config: {str(e)}")
        return False
    
    return True

def create_documentation():
    """Cria documentação específica do PostgreSQL"""
    print("\n📚 Criando documentação...")
    
    readme_content = """# Sistema de Atualização CTE - PostgreSQL Supabase

## 🚀 Início Rápido

### Execução Simples
```bash
# Linux/Mac
./quick_update.sh meu_arquivo.xlsx

# Windows
quick_update.bat meu_arquivo.xlsx
```

### Execução Avançada
```bash
# Apenas preview
python bulk_update_cte.py --update-file arquivo.xlsx --preview-only

# Modo todos os campos
python bulk_update_cte.py --update-file arquivo.xlsx --mode all

# Lote menor para conexões lentas
python bulk_update_cte.py --update-file arquivo.xlsx --batch-size 50
```

## 📊 Estrutura dos Dados

O sistema trabalha com a tabela `dashboard_baker` existente no Supabase.

### Campos Principais
- `numero_cte`: Identificador único do CTE
- `destinatario_nome`: Nome do cliente/destinatário  
- `veiculo_placa`: Placa do veículo
- `valor_total`: Valor total do frete
- `data_emissao`: Data de emissão do CTE
- `data_baixa`: Data da baixa

### Campos de Processo
- `data_inclusao_fatura`: Data inclusão na fatura
- `data_envio_processo`: Data envio do processo
- `primeiro_envio`: Data do primeiro envio
- `data_rq_tmc`: Data RQ/TMC
- `data_atesto`: Data do atesto
- `envio_final`: Data do envio final

## 🔧 Configuração

### Banco de Dados
O sistema usa as mesmas configurações do projeto Flask:
- Host: db.lijtncazuwnbydeqtoyz.supabase.co
- Porta: 5432
- Banco: postgres
- SSL: Obrigatório

### Modos de Atualização
- `empty_only`: Preenche apenas campos vazios (padrão)
- `all`: Atualiza todos os campos

## 📝 Formato do Arquivo

### Excel/CSV Aceito
```csv
numero_cte,destinatario_nome,valor_total,data_emissao
202410001,Empresa ABC,1500.50,2024-10-01
202410002,Empresa XYZ,2300.75,2024-10-02
```

### Variações de Colunas Aceitas
- CTE, Numero_CTE, CTRC → numero_cte
- Cliente, Destinatario → destinatario_nome  
- Valor, Valor_Frete → valor_total
- Data_Emissao, Data Emissão → data_emissao

## 🛡️ Segurança e Backup

### Backup Automático
- Criado automaticamente antes de cada atualização
- Formato JSON para fácil restauração
- Armazenado em `backups/`

### Validações
- CTEs devem existir no banco
- Formatos de data validados
- Valores numéricos verificados
- Duplicatas detectadas

## 📊 Monitoramento

### Logs
- Logs detalhados em `logs/`
- Rotação automática
- Níveis: INFO, WARNING, ERROR

### Relatórios
- Estatísticas de atualização
- Campos mais modificados
- Performance por lote
- Armazenados em `reports/`

## 🚨 Solução de Problemas

### Erro de Conexão
```bash
# Teste a conexão
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print(db.engine.execute('SELECT 1').scalar())"
```

### Performance Lenta
```bash
# Reduza o tamanho do lote
python bulk_update_cte.py --batch-size 25
```

### CTEs Não Encontrados
```bash
# Verifique total no banco
python -c "from app import create_app; from app.models.cte import CTE; app=create_app(); app.app_context().push(); print(f'Total: {CTE.query.count()}')"
```

## 📞 Suporte

Para suporte, verifique:
1. Logs em `logs/`
2. Configuração em `config/system.json`
3. Conexão com Supabase
4. Estrutura da tabela `dashboard_baker`

Desenvolvido para integração com sistema Baker Dashboard Flask.
"""
    
    try:
        with open('README_POSTGRESQL.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ README_POSTGRESQL.md criado")
    except Exception as e:
        print(f"❌ Erro ao criar documentação: {str(e)}")
        return False
    
    # Cria arquivo de exemplos
    examples_content = """# Exemplos de Uso - PostgreSQL

## 1. Atualização Básica (Recomendado)
```bash
python bulk_update_cte.py --update-file dados.xlsx --mode empty_only
```

## 2. Preview Antes da Execução
```bash
python bulk_update_cte.py --update-file dados.xlsx --preview-only
```

## 3. Atualização de Todos os Campos
```bash
python bulk_update_cte.py --update-file dados.xlsx --mode all
```

## 4. Lotes Menores (Conexões Lentas)
```bash
python bulk_update_cte.py --update-file dados.xlsx --batch-size 25
```

## 5. Sem Backup (Grandes Volumes)
```bash
python bulk_update_cte.py --update-file dados.xlsx --no-backup
```

## 6. Interface Simplificada
```bash
python quick_run.py
```

## 7. Gerar Template do Banco
```bash
python quick_run.py
# Escolha opção 1
```

## 8. Validar Arquivo
```bash
python quick_run.py
# Escolha opção 3
```

## 9. Estatísticas do Banco
```bash
python quick_run.py
# Escolha opção 4
```

## 10. Exemplo Completo
```bash
python example_postgresql.py
# Escolha opção 1
```
"""
    
    try:
        with open('EXAMPLES.md', 'w', encoding='utf-8') as f:
            f.write(examples_content)
        print("✅ EXAMPLES.md criado")
    except Exception as e:
        print(f"❌ Erro ao criar exemplos: {str(e)}")
        return False
    
    return True

def create_gitignore():
    """Cria arquivo .gitignore específico"""
    print("\n📝 Criando .gitignore...")
    
    gitignore_content = """# Sistema de Atualização CTE PostgreSQL

# Uploads temporários
uploads/*.xlsx
uploads/*.xls
uploads/*.csv
uploads/temp_*
uploads/exemplo_*
uploads/teste_*

# Logs do sistema
logs/*.log
logs/*.txt

# Backups (podem ser grandes)
backups/*.json
backups/*.sql

# Relatórios gerados
reports/*.json
reports/*.xlsx

# Templates temporários
templates/temp_*
templates/exemplo_*

# Scripts temporários
scripts/temp_*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Configurações locais
config/local.json
config/production.json

# Temporary files
*.tmp
*.temp
temp_*
test_*
exemplo_*
"""
    
    try:
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ Arquivo .gitignore criado")
    except Exception as e:
        print(f"❌ Erro ao criar .gitignore: {str(e)}")
        return False
    
    return True

def create_helper_scripts():
    """Cria scripts auxiliares"""
    print("\n🔧 Criando scripts auxiliares...")
    
    # Script de status do sistema
    status_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Script de status do sistema - PostgreSQL
\"\"\"

import sys
import os
sys.path.append(os.getcwd())

try:
    from app import create_app, db
    from app.models.cte import CTE
    from bulk_helper import BulkUpdateHelper
    
    print("🔍 STATUS DO SISTEMA - POSTGRESQL")
    print("="*40)
    
    app = create_app()
    
    with app.app_context():
        # Testa conexão
        total_ctes = CTE.query.count()
        print(f"✅ Banco: Conectado")
        print(f"📊 CTEs: {total_ctes}")
        
        # Estatísticas
        helper = BulkUpdateHelper()
        stats = helper.get_database_statistics()
        
        print(f"📈 Com baixa: {stats['ctes_with_baixa']}")
        print(f"🔄 Completos: {stats['ctes_complete_process']}")
        
        # Verifica arquivos
        folders = ['uploads', 'logs', 'backups', 'reports']
        for folder in folders:
            if os.path.exists(folder):
                files = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
                print(f"📁 {folder}: {files} arquivos")
            else:
                print(f"❌ {folder}: pasta não existe")
        
        print("\\n✅ Sistema funcionando normalmente")

except Exception as e:
    print(f"❌ Erro: {str(e)}")
    print("💡 Verifique se está no diretório correto do projeto Flask")
"""
    
    try:
        with open('status.py', 'w', encoding='utf-8') as f:
            f.write(status_script)
        print("✅ Script status.py criado")
    except Exception as e:
        print(f"❌ Erro ao criar status.py: {str(e)}")
        return False
    
    # Script de limpeza
    cleanup_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Script de limpeza - PostgreSQL
\"\"\"

import os
import shutil
from datetime import datetime, timedelta

def cleanup_files():
    print("🧹 LIMPEZA DO SISTEMA")
    print("="*30)
    
    # Pastas para limpar
    folders_to_clean = {
        'uploads': 7,    # 7 dias
        'logs': 30,      # 30 dias  
        'backups': 60,   # 60 dias
        'reports': 30    # 30 dias
    }
    
    total_removed = 0
    total_size = 0
    
    for folder, days_old in folders_to_clean.items():
        if not os.path.exists(folder):
            continue
            
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    
                    total_removed += 1
                    total_size += file_size
                    
                    print(f"🗑️ Removido: {filepath}")
    
    size_mb = total_size / (1024 * 1024)
    print(f"\\n✅ Limpeza concluída:")
    print(f"   Arquivos removidos: {total_removed}")
    print(f"   Espaço liberado: {size_mb:.2f} MB")

if __name__ == "__main__":
    cleanup_files()
"""
    
    try:
        with open('cleanup.py', 'w', encoding='utf-8') as f:
            f.write(cleanup_script)
        print("✅ Script cleanup.py criado")
    except Exception as e:
        print(f"❌ Erro ao criar cleanup.py: {str(e)}")
        return False
    
    return True

def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("\n🔍 Verificando instalação...")
    
    checks = [
        ("Python 3.8+", check_python_version),
        ("Ambiente Flask", lambda: os.path.exists('app') or os.path.exists('app.py')),
        ("Estrutura de pastas", lambda: all(os.path.exists(p) for p in ['uploads', 'logs', 'backups', 'reports'])),
        ("Scripts principais", lambda: all(os.path.exists(f) for f in ['bulk_update_cte.py', 'bulk_helper.py'])),
        ("Scripts auxiliares", lambda: all(os.path.exists(f) for f in ['quick_update.sh', 'status.py', 'cleanup.py'])),
        ("Configuração", lambda: os.path.exists('config/system.json')),
        ("Documentação", lambda: all(os.path.exists(f) for f in ['README_POSTGRESQL.md', 'EXAMPLES.md']))
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if check_func():
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} - Erro: {str(e)}")
            all_passed = False
    
    return all_passed

def show_next_steps():
    """Mostra próximos passos após instalação"""
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("="*35)
    
    print("1. 🔍 Teste a conexão:")
    print("   python status.py")
    
    print("\n2. 📋 Gere um template:")
    print("   python quick_run.py")
    print("   (Escolha opção 1)")
    
    print("\n3. ✅ Valide um arquivo:")
    print("   python quick_run.py") 
    print("   (Escolha opção 3)")
    
    print("\n4. 🚀 Execute atualização:")
    print("   Linux/Mac: ./quick_update.sh arquivo.xlsx")
    print("   Windows: quick_update.bat arquivo.xlsx")
    print("   Manual: python bulk_update_cte.py --update-file arquivo.xlsx --preview-only")
    
    print("\n5. 🎬 Veja demonstração:")
    print("   python example_postgresql.py")
    
    print("\n6. 📊 Monitore o sistema:")
    print("   - Logs: logs/")
    print("   - Backups: backups/") 
    print("   - Relatórios: reports/")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("- Sempre use --preview-only primeiro")
    print("- Modo 'empty_only' é mais seguro")
    print("- Backups são criados automaticamente")
    print("- Valide arquivos antes de processar")

def main():
    """Função principal do instalador"""
    print_header()
    
    steps = [
        ("Verificar Python", check_python_version),
        ("Verificar ambiente Flask", check_flask_environment),
        ("Instalar dependências", install_dependencies),
        ("Testar conexão PostgreSQL", test_database_connection),
        ("Criar estrutura de pastas", create_folder_structure), 
        ("Criar arquivos de configuração", create_config_files),
        ("Criar documentação", create_documentation),
        ("Criar .gitignore", create_gitignore),
        ("Criar scripts auxiliares", create_helper_scripts),
        ("Verificar instalação", verify_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n▶️ {step_name}...")
        if not step_func():
            print(f"\n❌ Falha na etapa: {step_name}")
            print("🔧 Verifique os erros acima e execute novamente")
            return False
    
    print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*50)
    
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {str(e)}")
        sys.exit(1)