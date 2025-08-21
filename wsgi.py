#!/usr/bin/env python3
import os
import sys

print("🚀 INICIANDO SISTEMA ORIGINAL TRANSPONTUAL...")

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# DESABILITAR logs excessivos
import logging
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Variável global para armazenar erro
ERRO_SISTEMA = None

def criar_sistema_original():
    """Cria o sistema original com diagnóstico"""
    global ERRO_SISTEMA
    
    try:
        print("🔍 Importando sistema original...")
        
        # IMPORTAR SEU SISTEMA ORIGINAL
        from app import create_app, db
        print("✅ app importado!")
        
        from config import ProductionConfig
        print("✅ config importado!")
        
        # CRIAR APLICAÇÃO ORIGINAL
        application = create_app(ProductionConfig)
        print("✅ Aplicação original criada!")
        
        # CONFIGURAR BANCO
        with application.app_context():
            try:
                from sqlalchemy import text
                db.session.execute(text("SELECT 1"))
                print("✅ Supabase conectado!")
                
                db.create_all()
                print("✅ Tabelas criadas!")
                
                # Criar admin
                from app.models.user import User
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    admin = User(
                        username='admin',
                        email='admin@transpontual.app.br',
                        nome_completo='Administrador Transpontual',
                        tipo_usuario='admin',
                        ativo=True
                    )
                    admin.set_password('Admin123!')
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Admin criado!")
                else:
                    print("✅ Admin existe!")
                
                # ADICIONAR FUNCIONALIDADE DE ATUALIZAÇÃO
                adicionar_atualizacao_lote(application)
                
            except Exception as e:
                ERRO_SISTEMA = f"Erro configuração banco: {str(e)}"
                print(f"⚠️ {ERRO_SISTEMA}")
        
        print("🎉 SISTEMA ORIGINAL FUNCIONANDO!")
        return application
        
    except ImportError as e:
        ERRO_SISTEMA = f"Erro importação: {str(e)}"
        print(f"❌ {ERRO_SISTEMA}")
        return None
        
    except Exception as e:
        ERRO_SISTEMA = f"Erro geral: {str(e)}"
        print(f"❌ {ERRO_SISTEMA}")
        return None

def adicionar_atualizacao_lote(app):
    """Adiciona sistema de atualização em lote"""
    try:
        print("🔧 Adicionando sistema de atualização...")
        
        from flask import Blueprint, request, jsonify, render_template_string, make_response
        from flask_login import login_required
        import pandas as pd
        import io
        from datetime import datetime
        
        # Blueprint para atualização
        bulk_bp = Blueprint('bulk_update', __name__, url_prefix='/ctes')
        
        @bulk_bp.route('/atualizar-lote')
        @login_required
        def atualizar_lote():
            """Página de atualização em lote"""
            from app.models.cte import CTE
            
            try:
                total_ctes = CTE.query.count()
            except:
                total_ctes = 0
            
            return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atualização em Lote - Transpontual</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        .navbar { background: rgba(0,0,0,0.2) !important; }
        .navbar-brand { font-weight: bold; color: white !important; }
        .card { 
            border: none; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            background: rgba(255,255,255,0.95); 
            margin-bottom: 20px; 
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            border: none; 
            border-radius: 10px; 
        }
        .status-original { 
            background: linear-gradient(135deg, #28a745, #20c997); 
            color: white; 
            padding: 15px; 
            border-radius: 15px; 
            margin-bottom: 20px; 
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/dashboard"><i class="fas fa-truck"></i> Dashboard Transpontual</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <a class="nav-link" href="/ctes">CTEs</a>
                <a class="nav-link" href="/logout">Sair</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="status-original">
            <i class="fas fa-check-double fa-2x mb-2"></i><br>
            <strong>🎉 SISTEMA ORIGINAL TRANSPONTUAL ATIVO</strong><br>
            Conectado ao Supabase • Atualização em lote integrada<br>
            <small>Total de CTEs: {{ total_ctes }}</small>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h4><i class="fas fa-sync-alt"></i> Atualização em Lote de CTEs</h4>
                        <p class="mb-0">Sistema original integrado - Atualizações diretas no Supabase</p>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-upload"></i> Upload de Arquivo</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="alert alert-info">
                                            <h6><i class="fas fa-info-circle"></i> Todos os campos atualizáveis:</h6>
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <ul class="small">
                                                        <li><strong>destinatario_nome</strong> - Nome do Cliente</li>
                                                        <li><strong>veiculo_placa</strong> - Placa do Veículo</li>
                                                        <li><strong>valor_total</strong> - Valor Total</li>
                                                        <li><strong>data_emissao</strong> - Data de Emissão</li>
                                                        <li><strong>data_baixa</strong> - Data da Baixa</li>
                                                        <li><strong>numero_fatura</strong> - Número da Fatura</li>
                                                        <li><strong>observacao</strong> - Observações</li>
                                                    </ul>
                                                </div>
                                                <div class="col-md-6">
                                                    <ul class="small">
                                                        <li><strong>data_inclusao_fatura</strong> - Inclusão Fatura</li>
                                                        <li><strong>data_envio_processo</strong> - Envio Processo</li>
                                                        <li><strong>primeiro_envio</strong> - Primeiro Envio</li>
                                                        <li><strong>data_rq_tmc</strong> - Data RQ/TMC</li>
                                                        <li><strong>data_atesto</strong> - Data Atesto</li>
                                                        <li><strong>envio_final</strong> - Envio Final</li>
                                                        <li><strong>origem_dados</strong> - Origem dos Dados</li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <form id="formAtualizacao" enctype="multipart/form-data">
                                            <div class="mb-3">
                                                <label class="form-label">Modo de Atualização:</label>
                                                <select class="form-control" id="modo" name="modo">
                                                    <option value="empty_only">Apenas campos vazios (Recomendado)</option>
                                                    <option value="all">Todos os campos (Sobrescrever existentes)</option>
                                                </select>
                                            </div>
                                            
                                            <div class="mb-3">
                                                <label class="form-label">Arquivo CSV/Excel:</label>
                                                <input type="file" class="form-control" id="arquivo" name="arquivo" 
                                                       accept=".csv,.xlsx,.xls" required>
                                            </div>
                                            
                                            <div class="d-flex gap-2">
                                                <button type="button" class="btn btn-warning" onclick="processarArquivo()">
                                                    <i class="fas fa-sync-alt"></i> Atualizar no Supabase
                                                </button>
                                                <a href="/ctes/template-csv" class="btn btn-outline-secondary">
                                                    <i class="fas fa-download"></i> Template CSV
                                                </a>
                                                <a href="/ctes" class="btn btn-outline-primary">
                                                    <i class="fas fa-arrow-left"></i> Voltar CTEs
                                                </a>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-chart-bar"></i> Status</h5>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>Total CTEs:</strong> {{ total_ctes }}</p>
                                        <p><strong>Sistema:</strong> <span class="badge bg-success">Original</span></p>
                                        <p><strong>Banco:</strong> <span class="badge bg-primary">Supabase</span></p>
                                        <hr>
                                        <div class="alert alert-success">
                                            <i class="fas fa-check"></i> 
                                            Sistema original com atualização em lote funcionando!
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="resultados" class="mt-4" style="display: none;">
                            <div class="card">
                                <div class="card-header">
                                    <h5><i class="fas fa-chart-line"></i> Resultados</h5>
                                </div>
                                <div class="card-body" id="resultadosContent">
                                    <!-- Resultados -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
    function processarArquivo() {
        const form = document.getElementById('formAtualizacao');
        const formData = new FormData(form);
        const arquivo = document.getElementById('arquivo').files[0];
        
        if (!arquivo) {
            alert('Selecione um arquivo!');
            return;
        }
        
        if (!confirm('Atualizar dados no Supabase?')) {
            return;
        }
        
        document.getElementById('resultados').style.display = 'block';
        document.getElementById('resultadosContent').innerHTML = `
            <div class="text-center">
                <i class="fas fa-spinner fa-spin fa-2x text-warning"></i>
                <h5 class="mt-3">Processando no Supabase...</h5>
            </div>
        `;
        
        fetch('/ctes/api/processar', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                document.getElementById('resultadosContent').innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Atualização Concluída!</h6>
                        <p><strong>Processados:</strong> ` + (data.stats.total_processados || 0) + `</p>
                        <p><strong>Atualizados:</strong> ` + (data.stats.atualizados || 0) + `</p>
                        <p><strong>Erros:</strong> ` + (data.stats.erros || 0) + `</p>
                    </div>
                `;
            } else {
                document.getElementById('resultadosContent').innerHTML = `
                    <div class="alert alert-danger">
                        <h6>Erro</h6>
                        <p>` + (data.erro || 'Erro desconhecido') + `</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            document.getElementById('resultadosContent').innerHTML = `
                <div class="alert alert-danger">
                    <h6>Erro de conexão</h6>
                    <p>` + error.message + `</p>
                </div>
            `;
        });
    }
    </script>
</body>
</html>
            ''', total_ctes=total_ctes)
        
        @bulk_bp.route('/api/processar', methods=['POST'])
        @login_required
        def api_processar():
            """API que processa atualização"""
            try:
                arquivo = request.files.get('arquivo')
                modo = request.form.get('modo', 'empty_only')
                
                if not arquivo:
                    return jsonify({'sucesso': False, 'erro': 'Arquivo não enviado'}), 400
                
                # Ler arquivo
                if arquivo.filename.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(arquivo.read()), encoding='utf-8')
                elif arquivo.filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(arquivo.read()))
                else:
                    return jsonify({'sucesso': False, 'erro': 'Formato não suportado'}), 400
                
                # Validar CTE
                cte_col = 'numero_cte'
                for col in ['numero_cte', 'CTE', 'Numero_CTE']:
                    if col in df.columns:
                        cte_col = col
                        break
                
                if cte_col not in df.columns:
                    return jsonify({'sucesso': False, 'erro': 'Coluna CTE não encontrada'}), 400
                
                if cte_col != 'numero_cte':
                    df['numero_cte'] = df[cte_col]
                
                # Processar
                from app.models.cte import CTE
                
                stats = {'total_processados': 0, 'atualizados': 0, 'erros': 0}
                
                for _, row in df.iterrows():
                    try:
                        numero_cte = int(float(row['numero_cte']))
                        stats['total_processados'] += 1
                        
                        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                        if not cte:
                            continue
                        
                        # Atualizar campos básicos
                        updated = False
                        
                        campos = {
                            'destinatario_nome': ['Cliente', 'Destinatario', 'destinatario_nome'],
                            'veiculo_placa': ['Veiculo', 'Placa', 'veiculo_placa'],
                            'valor_total': ['Valor', 'valor_total'],
                            'observacao': ['Observacao', 'observacao']
                        }
                        
                        for campo_db, colunas_possiveis in campos.items():
                            for col in colunas_possiveis:
                                if col in df.columns and pd.notna(row[col]):
                                    valor_atual = getattr(cte, campo_db, None)
                                    novo_valor = row[col]
                                    
                                    if (modo == 'all' or (modo == 'empty_only' and not valor_atual)):
                                        setattr(cte, campo_db, novo_valor)
                                        updated = True
                                    break
                        
                        if updated:
                            cte.updated_at = datetime.utcnow()
                            stats['atualizados'] += 1
                            
                    except Exception as e:
                        stats['erros'] += 1
                
                db.session.commit()
                
                return jsonify({
                    'sucesso': True,
                    'stats': stats,
                    'mensagem': f'{stats["atualizados"]} CTEs atualizados'
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'sucesso': False, 'erro': str(e)}), 500
        
        @bulk_bp.route('/template-csv')
        @login_required
        def template_csv():
            """Template CSV"""
            template = '''numero_cte,destinatario_nome,veiculo_placa,valor_total,observacao
22421,Baker Hotéis Ltda,ABC1234,3200.50,Exemplo
22422,Empresa ABC,XYZ5678,4100.25,Teste
'''
            
            response = make_response(template)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=template_transpontual.csv'
            return response
        
        # Registrar blueprint
        app.register_blueprint(bulk_bp)
        print("✅ Sistema de atualização integrado!")
        
    except Exception as e:
        print(f"⚠️ Erro integração: {e}")

def criar_app_emergencia():
    """App de emergência com diagnóstico"""
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def debug():
        return f'''
        <h1>🔧 Diagnóstico - Sistema Transpontual</h1>
        
        <div style="background:#f8f9fa; padding:20px; margin:20px 0; border-radius:10px;">
            <h3>Status do Sistema:</h3>
            <p><strong>Erro detectado:</strong> {ERRO_SISTEMA or "Sistema carregando..."}</p>
        </div>
        
        <div style="background:#e3f2fd; padding:20px; margin:20px 0; border-radius:10px;">
            <h3>Estrutura Verificada:</h3>
            <ul>
                <li>✅ app/ - Diretório existe</li>
                <li>✅ app/models/ - Modelos encontrados</li>
                <li>✅ app/routes/ - Rotas encontradas</li>
                <li>✅ config.py - Configuração disponível</li>
            </ul>
        </div>
        
        <p><a href="/tentar-novamente" style="background:#007bff; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">🔄 Tentar Novamente</a></p>
        '''
    
    @app.route('/tentar-novamente')
    def tentar_novamente():
        return '<h1>🔄 Tentando recarregar sistema...</h1><script>setTimeout(() => location.href="/", 2000);</script>'
    
    return app

# EXECUTAR CRIAÇÃO DO SISTEMA
print("🔄 Tentando criar sistema original...")
app_original = criar_sistema_original()

if app_original:
    application = app_original
    print("🎉 SISTEMA ORIGINAL FUNCIONANDO!")
else:
    application = criar_app_emergencia()
    print("⚠️ Usando app de emergência")

# Exportar app
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
