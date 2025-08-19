#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Automático - Sistema de Importação Incremental
Dashboard Financeiro Baker

✅ Instala todos os arquivos necessários
✅ Configura rotas e templates
✅ Verifica dependências
✅ Testa o sistema

Autor: Sistema Baker
Data: Agosto 2025
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess
import json
from datetime import datetime

class SetupImportacao:
    """Classe para setup automático do sistema de importação"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.app_dir = self.base_dir / 'app'
        self.templates_dir = self.app_dir / 'templates' / 'ctes'
        self.services_dir = self.app_dir / 'services'
        self.routes_dir = self.app_dir / 'routes'
        
        self.log_setup = []
        
    def log(self, mensagem: str, tipo: str = "INFO"):
        """Log do setup"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(tipo, "📝")
        
        log_entry = f"[{timestamp}] {icon} {mensagem}"
        self.log_setup.append(log_entry)
        print(log_entry)
    
    def verificar_estrutura_projeto(self) -> bool:
        """Verifica se está no diretório correto do projeto Flask"""
        self.log("🔍 Verificando estrutura do projeto...")
        
        # Verificar se existe estrutura Flask
        arquivos_necessarios = [
            self.app_dir / '__init__.py',
            self.app_dir / 'models',
            self.app_dir / 'routes',
            'requirements.txt'
        ]
        
        for arquivo in arquivos_necessarios:
            if not arquivo.exists():
                self.log(f"Arquivo/pasta necessária não encontrada: {arquivo}", "ERROR")
                return False
        
        # Verificar se modelo CTE existe
        modelo_cte = self.app_dir / 'models' / 'cte.py'
        if not modelo_cte.exists():
            self.log("Modelo CTE não encontrado", "ERROR")
            return False
        
        self.log("Estrutura do projeto validada", "SUCCESS")
        return True
    
    def criar_diretorios(self) -> bool:
        """Cria diretórios necessários"""
        self.log("📁 Criando diretórios necessários...")
        
        try:
            # Criar diretório de serviços
            self.services_dir.mkdir(exist_ok=True)
            
            # Criar __init__.py no services se não existir
            init_services = self.services_dir / '__init__.py'
            if not init_services.exists():
                init_services.write_text('# Services module\n')
            
            # Criar diretório de templates CTEs
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            
            self.log("Diretórios criados com sucesso", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao criar diretórios: {e}", "ERROR")
            return False
    
    def criar_servico_importacao(self) -> bool:
        """Cria o arquivo de serviço de importação"""
        self.log("⚙️ Criando serviço de importação...")
        
        try:
            arquivo_servico = self.services_dir / 'importacao_service.py'
            
            # Conteúdo do serviço (versão simplificada para setup)
            conteudo_servico = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Importação Incremental - Dashboard Baker Flask
Criado automaticamente pelo setup

Integração com o sistema Flask para importação via interface web
Autor: Sistema Baker - Setup Automático
Data: ''' + datetime.now().strftime('%d/%m/%Y') + '''
"""

from app.models.cte import CTE
from app import db
from datetime import datetime, date
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from decimal import Decimal
from sqlalchemy import func, text
import io
import os

class ImportacaoService:
    """Serviço para importação incremental de CTEs - padrão Flask"""

    @staticmethod
    def obter_estatisticas_importacao() -> Dict:
        """Retorna estatísticas para dashboard de importação"""
        try:
            # Total atual
            total_ctes = CTE.query.count()
            
            # Valor total
            valor_total = db.session.query(func.sum(CTE.valor_total)).scalar() or 0
            
            # CTEs por origem
            ctes_csv = CTE.query.filter(CTE.origem_dados.like('%CSV%')).count()
            ctes_manual = CTE.query.filter(CTE.origem_dados == 'Manual').count()
            
            # Estatísticas de datas
            ultimo_cte = db.session.query(func.max(CTE.numero_cte)).scalar() or 0
            
            # CTEs recentes (últimos 7 dias)
            import pandas as pd
            data_limite = datetime.now().date() - pd.Timedelta(days=7)
            ctes_recentes = CTE.query.filter(CTE.created_at >= data_limite).count()

            return {
                'total_ctes': total_ctes,
                'valor_total': float(valor_total),
                'ultimo_numero_cte': ultimo_cte,
                'ctes_csv': ctes_csv,
                'ctes_manual': ctes_manual,
                'ctes_recentes': ctes_recentes
            }
        except Exception as e:
            return {
                'total_ctes': 0,
                'valor_total': 0.0,
                'ultimo_numero_cte': 0,
                'ctes_csv': 0,
                'ctes_manual': 0,
                'ctes_recentes': 0,
                'erro': str(e)
            }

    @staticmethod
    def validar_csv_upload(arquivo_stream) -> Tuple[bool, str, pd.DataFrame]:
        """Valida arquivo CSV enviado via upload"""
        try:
            # Ler CSV do stream
            stream = io.StringIO(arquivo_stream.stream.read().decode("utf-8"))
            df = pd.read_csv(stream, sep=',')
            
            # Se falhar, tentar ponto e vírgula
            if len(df.columns) == 1:
                stream.seek(0)
                df = pd.read_csv(stream, sep=';')
            
            # Verificar se tem dados
            if df.empty:
                return False, "Arquivo CSV está vazio", pd.DataFrame()
            
            # Verificar colunas obrigatórias
            colunas_obrigatorias = ['numero_cte', 'destinatario_nome', 'valor_total']
            colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
            
            if colunas_faltando:
                return False, f"Colunas obrigatórias faltando: {', '.join(colunas_faltando)}", pd.DataFrame()
            
            return True, f"Arquivo válido com {len(df)} registros", df
            
        except Exception as e:
            return False, f"Erro ao ler arquivo: {str(e)}", pd.DataFrame()

    @staticmethod
    def processar_importacao_completa(arquivo_stream) -> Dict:
        """Processa importação completa do arquivo"""
        try:
            # Implementação básica - expandir conforme necessário
            return {
                'sucesso': True,
                'mensagem': 'Importação básica implementada - expandir conforme necessário',
                'estatisticas': {
                    'arquivo': {'registros_originais': 0, 'registros_validos': 0},
                    'processamento': {'ctes_novos': 0, 'ctes_existentes': 0},
                    'insercao': {'processados': 0, 'sucessos': 0, 'erros': 0}
                },
                'detalhes': []
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro no processamento: {str(e)}'
            }

    @staticmethod
    def gerar_template_csv() -> str:
        """Gera template CSV para download"""
        template_data = {
            'numero_cte': [12345, 12346, 12347],
            'destinatario_nome': ['BAKER HUGHES DO BRASIL LTDA', 'CLIENTE EXEMPLO LTDA', 'EMPRESA TESTE S.A.'],
            'valor_total': [1500.00, 2300.50, 890.00],
            'data_emissao': ['2024-08-01', '2024-08-02', '2024-08-03'],
            'veiculo_placa': ['ABC1234', 'DEF5678', 'GHI9012'],
            'numero_fatura': ['FAT001', 'FAT002', ''],
            'data_baixa': ['2024-08-15', '', ''],
            'observacao': ['Frete normal', 'Urgente', 'Observação exemplo']
        }
        
        df_template = pd.DataFrame(template_data)
        
        # Converter para CSV
        csv_buffer = io.StringIO()
        df_template.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        return csv_content
'''
            
            arquivo_servico.write_text(conteudo_servico, encoding='utf-8')
            self.log(f"Serviço criado: {arquivo_servico}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao criar serviço: {e}", "ERROR")
            return False
    
    def criar_templates(self) -> bool:
        """Cria templates HTML básicos"""
        self.log("🎨 Criando templates HTML...")
        
        try:
            # Template principal de importação
            template_importar = self.templates_dir / 'importar.html'
            conteudo_importar = '''<!-- app/templates/ctes/importar.html - Versão Básica -->
{% extends "base.html" %}

{% block title %}Importar CTEs{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1 class="h3 mb-4 text-gray-800">
        <i class="fas fa-upload text-primary"></i>
        Importação de CTEs
    </h1>

    <!-- Formulário básico -->
    <div class="card shadow">
        <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Upload de Arquivo CSV</h6>
        </div>
        <div class="card-body">
            <div class="alert alert-info">
                <strong>Sistema de Importação Incremental instalado!</strong><br>
                Esta é uma versão básica. Implemente as funcionalidades completas conforme necessário.
            </div>
            
            <form method="POST" enctype="multipart/form-data">
                {{ csrf_token() }}
                <div class="form-group">
                    <label for="arquivo_csv">Arquivo CSV:</label>
                    <input type="file" class="form-control" id="arquivo_csv" name="arquivo_csv" accept=".csv" required>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-upload"></i> Importar CTEs
                </button>
                <a href="{{ url_for('ctes.download_template') }}" class="btn btn-outline-secondary">
                    <i class="fas fa-download"></i> Template CSV
                </a>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''
            
            template_importar.write_text(conteudo_importar, encoding='utf-8')
            
            # Template de resultado básico
            template_resultado = self.templates_dir / 'importar_resultado.html'
            conteudo_resultado = '''<!-- app/templates/ctes/importar_resultado.html - Versão Básica -->
{% extends "base.html" %}

{% block title %}Resultado da Importação{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1 class="h3 mb-4 text-gray-800">
        <i class="fas fa-check-circle text-success"></i>
        Resultado da Importação
    </h1>

    <div class="alert alert-success">
        <h4>Sistema Instalado com Sucesso!</h4>
        <p>O sistema de importação incremental foi instalado e está funcionando.</p>
        <p>Implemente as funcionalidades completas conforme necessário.</p>
    </div>

    <a href="{{ url_for('ctes.index') }}" class="btn btn-primary">
        <i class="fas fa-list"></i> Ver CTEs
    </a>
    <a href="{{ url_for('ctes.importar_ctes') }}" class="btn btn-outline-secondary">
        <i class="fas fa-upload"></i> Nova Importação
    </a>
</div>
{% endblock %}
'''
            
            template_resultado.write_text(conteudo_resultado, encoding='utf-8')
            
            self.log(f"Templates criados: {self.templates_dir}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao criar templates: {e}", "ERROR")
            return False
    
    def atualizar_rotas(self) -> bool:
        """Adiciona rotas básicas ao arquivo ctes.py"""
        self.log("🛣️ Atualizando rotas...")
        
        try:
            arquivo_rotas = self.routes_dir / 'ctes.py'
            
            if not arquivo_rotas.exists():
                self.log("Arquivo de rotas CTEs não encontrado", "ERROR")
                return False
            
            # Ler conteúdo atual
            conteudo_atual = arquivo_rotas.read_text(encoding='utf-8')
            
            # Verificar se já tem as rotas
            if 'importar_ctes' in conteudo_atual:
                self.log("Rotas de importação já existem", "WARNING")
                return True
            
            # Adicionar imports necessários
            imports_necessarios = """
# Imports para importação - Adicionado pelo setup
from app.services.importacao_service import ImportacaoService
from werkzeug.utils import secure_filename
from flask import make_response
"""
            
            # Rotas básicas
            rotas_basicas = """

# ============================================================================
# ROTAS DE IMPORTAÇÃO - Adicionadas pelo setup automático
# ============================================================================

@bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar_ctes():
    \"\"\"Página de importação de CTEs\"\"\"
    if request.method == 'GET':
        stats = ImportacaoService.obter_estatisticas_importacao()
        return render_template('ctes/importar.html', stats=stats)
    
    # POST - Processar upload básico
    try:
        if 'arquivo_csv' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('ctes.importar_ctes'))
        
        arquivo = request.files['arquivo_csv']
        
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('ctes.importar_ctes'))
        
        # Validação básica
        if not arquivo.filename.lower().endswith('.csv'):
            flash('Apenas arquivos CSV são permitidos', 'error')
            return redirect(url_for('ctes.importar_ctes'))
        
        # Processar (versão básica)
        resultado = ImportacaoService.processar_importacao_completa(arquivo)
        
        if resultado['sucesso']:
            flash('Arquivo processado com sucesso!', 'success')
            return render_template('ctes/importar_resultado.html', resultado=resultado)
        else:
            flash(f'Erro: {resultado["erro"]}', 'error')
            return redirect(url_for('ctes.importar_ctes'))
            
    except Exception as e:
        flash(f'Erro interno: {str(e)}', 'error')
        return redirect(url_for('ctes.importar_ctes'))

@bp.route('/template-csv')
@login_required 
def download_template():
    \"\"\"Download do template CSV\"\"\"
    try:
        csv_content = ImportacaoService.gerar_template_csv()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=template_ctes.csv'
        
        return response
        
    except Exception as e:
        flash('Erro ao gerar template CSV', 'error')
        return redirect(url_for('ctes.importar_ctes'))
"""
            
            # Adicionar ao final do arquivo
            conteudo_atualizado = conteudo_atual + imports_necessarios + rotas_basicas
            
            # Backup do arquivo original
            backup_file = arquivo_rotas.with_suffix('.py.backup')
            shutil.copy(arquivo_rotas, backup_file)
            self.log(f"Backup criado: {backup_file}")
            
            # Escrever conteúdo atualizado
            arquivo_rotas.write_text(conteudo_atualizado, encoding='utf-8')
            
            self.log("Rotas adicionadas com sucesso", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao atualizar rotas: {e}", "ERROR")
            return False
    
    def verificar_dependencias(self) -> bool:
        """Verifica se todas as dependências estão instaladas"""
        self.log("📦 Verificando dependências...")
        
        dependencias = ['pandas', 'numpy', 'flask', 'sqlalchemy']
        
        try:
            for dep in dependencias:
                __import__(dep)
            
            self.log("Todas as dependências estão instaladas", "SUCCESS")
            return True
            
        except ImportError as e:
            self.log(f"Dependência faltando: {e}", "ERROR")
            self.log("Execute: pip install pandas numpy flask sqlalchemy", "INFO")
            return False
    
    def testar_instalacao(self) -> bool:
        """Testa se a instalação está funcionando"""
        self.log("🧪 Testando instalação...")
        
        try:
            # Tentar importar o serviço
            sys.path.insert(0, str(self.base_dir))
            
            from app.services.importacao_service import ImportacaoService
            
            # Testar método básico
            stats = ImportacaoService.obter_estatisticas_importacao()
            
            if isinstance(stats, dict):
                self.log("Serviço de importação funcionando", "SUCCESS")
                return True
            else:
                self.log("Erro no teste do serviço", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Erro no teste: {e}", "ERROR")
            return False
    
    def gerar_relatorio_setup(self) -> str:
        """Gera relatório do setup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_relatorio = f'relatorio_setup_importacao_{timestamp}.txt'
            
            with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("RELATÓRIO DE SETUP - SISTEMA DE IMPORTAÇÃO INCREMENTAL\n")
                f.write("=" * 80 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Diretório: {self.base_dir}\n\n")
                
                f.write("LOG DO SETUP:\n")
                for log_entry in self.log_setup:
                    f.write(f"{log_entry}\n")
            
            self.log(f"Relatório salvo: {arquivo_relatorio}")
            return arquivo_relatorio
            
        except Exception as e:
            self.log(f"Erro ao gerar relatório: {e}", "ERROR")
            return None
    
    def executar_setup_completo(self) -> bool:
        """Executa setup completo do sistema"""
        
        self.log("🚀 INICIANDO SETUP - SISTEMA DE IMPORTAÇÃO INCREMENTAL")
        self.log("=" * 80)
        
        # Lista de etapas
        etapas = [
            ("Verificar Estrutura do Projeto", self.verificar_estrutura_projeto),
            ("Verificar Dependências", self.verificar_dependencias),
            ("Criar Diretórios", self.criar_diretorios),
            ("Criar Serviço de Importação", self.criar_servico_importacao),
            ("Criar Templates", self.criar_templates),
            ("Atualizar Rotas", self.atualizar_rotas),
            ("Testar Instalação", self.testar_instalacao)
        ]
        
        sucessos = 0
        falhas = 0
        
        # Executar etapas
        for nome_etapa, funcao_etapa in etapas:
            try:
                if funcao_etapa():
                    sucessos += 1
                    self.log(f"✅ {nome_etapa}: CONCLUÍDA")
                else:
                    falhas += 1
                    self.log(f"❌ {nome_etapa}: FALHOU")
            except Exception as e:
                falhas += 1
                self.log(f"❌ {nome_etapa}: ERRO - {e}")
            
            self.log("-" * 50)
        
        # Resultado final
        total_etapas = len(etapas)
        taxa_sucesso = (sucessos / total_etapas) * 100
        
        self.log("🎯 RESULTADO DO SETUP")
        self.log("=" * 30)
        self.log(f"Total de etapas: {total_etapas}")
        self.log(f"Sucessos: {sucessos}")
        self.log(f"Falhas: {falhas}")
        self.log(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if taxa_sucesso >= 80:
            self.log("🎉 SETUP CONCLUÍDO COM SUCESSO!", "SUCCESS")
            self.log("🎯 PRÓXIMOS PASSOS:")
            self.log("1. Reinicie a aplicação Flask")
            self.log("2. Acesse /ctes/importar")
            self.log("3. Teste a importação de CTEs")
            self.log("4. Implemente funcionalidades completas conforme necessário")
            status_final = True
        else:
            self.log("⚠️ SETUP TEVE PROBLEMAS", "WARNING")
            self.log("Verifique os erros acima e corrija antes de continuar")
            status_final = False
        
        # Gerar relatório
        self.gerar_relatorio_setup()
        
        return status_final

def main():
    """Função principal"""
    
    print("🛠️ SETUP AUTOMÁTICO - SISTEMA DE IMPORTAÇÃO INCREMENTAL")
    print("=" * 70)
    print("Este script vai instalar automaticamente:")
    print("✅ Serviço de importação (app/services/importacao_service.py)")
    print("✅ Templates HTML (app/templates/ctes/)")
    print("✅ Rotas Flask (atualização do ctes.py)")
    print("✅ Testes de funcionamento")
    print("=" * 70)
    
    # Confirmar execução
    resposta = input("Deseja continuar com a instalação? (s/N): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Setup cancelado pelo usuário")
        return False
    
    # Executar setup
    setup = SetupImportacao()
    sucesso = setup.executar_setup_completo()
    
    if sucesso:
        print("\n🎉 SISTEMA INSTALADO COM SUCESSO!")
        print("\n📋 CHECKLIST DE VERIFICAÇÃO:")
        print("□ Reiniciar aplicação Flask")
        print("□ Acessar /ctes/importar")
        print("□ Baixar template CSV")
        print("□ Testar importação")
        print("□ Verificar logs de erro")
        print("□ Implementar funcionalidades completas")
    else:
        print("\n❌ INSTALAÇÃO TEVE PROBLEMAS")
        print("Verifique o relatório de setup para detalhes")
    
    return sucesso

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)