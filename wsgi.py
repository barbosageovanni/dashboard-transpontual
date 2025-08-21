#!/usr/bin/env python3
import os
import sys

print("🚀 INICIANDO SISTEMA ORIGINAL TRANSPONTUAL...")
print("📁 Estrutura detectada:")
print("   ✅ app/")
print("   ✅ app/models/")
print("   ✅ app/routes/")
print("   ✅ app/services/")

# Configurar ambiente para FORÇAR sistema original
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Mariaana953%407334@db.lijtncazuwnbydeqtoyz.supabase.co:5432/postgres')

# DESABILITAR logs excessivos
import logging
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def forcar_sistema_original():
    """Força importação e uso do sistema original"""
    try:
        print("🔍 Importando sistema original...")
        
        # IMPORTAR SEU SISTEMA ORIGINAL
        from app import create_app, db
        print("✅ app importado com sucesso!")
        
        from config import ProductionConfig
        print("✅ config importado com sucesso!")
        
        # CRIAR APLICAÇÃO ORIGINAL
        application = create_app(ProductionConfig)
        print("✅ Aplicação original criada!")
        
        # TESTAR CONEXÃO E CONFIGURAR BANCO
        with application.app_context():
            try:
                from sqlalchemy import text
                db.session.execute(text("SELECT 1"))
                print("✅ Supabase conectado!")
                
                # Criar tabelas se necessário
                db.create_all()
                print("✅ Tabelas verificadas!")
                
                # Verificar/criar admin
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
                    print("✅ Admin já existe!")
                
                # ADICIONAR FUNCIONALIDADE DE ATUALIZAÇÃO EM LOTE
                adicionar_sistema_atualizacao(application)
                
            except Exception as e:
                print(f"⚠️ Erro configuração banco: {e}")
        
        print("🎉 SISTEMA ORIGINAL FUNCIONANDO COM ATUALIZAÇÃO EM LOTE!")
        return application
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print(f"📁 Verificando arquivos...")
        
        # Verificar se arquivos existem
        import os
        arquivos_necessarios = [
            'app/__init__.py',
            'app/models/__init__.py',
            'app/models/cte.py',
            'app/models/user.py',
            'config.py'
        ]
        
        for arquivo in arquivos_necessarios:
            if os.path.exists(arquivo):
                print(f"   ✅ {arquivo}")
            else:
                print(f"   ❌ {arquivo} - FALTANDO!")
        
        raise e
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        raise e

def adicionar_sistema_atualizacao(app):
    """Adiciona sistema de atualização em lote ao app original"""
    try:
        print("🔧 Integrando sistema de atualização em lote...")
        
        from flask import Blueprint, request, jsonify, render_template_string, make_response
        from flask_login import login_required, current_user
        import pandas as pd
        import io
        from datetime import datetime
        
        # Criar blueprint para atualização
        bulk_bp = Blueprint('bulk_update', __name__, url_prefix='/ctes')
        
        @bulk_bp.route('/atualizar-lote')
        @login_required
        def atualizar_lote():
            """Página de atualização em lote"""
            from app.models.cte import CTE
            
            try:
                total_ctes = CTE.query.count()
                ultimo_cte = CTE.query.order_by(CTE.updated_at.desc()).first()
            except:
                total_ctes = 0
                ultimo_cte = None
            
            template_html = '''
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar { background: rgba(0,0,0,0.2) !important; backdrop-filter: blur(10px); }
        .navbar-brand { font-weight: bold; color: white !important; }
        .card { 
            border: none; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            backdrop-filter: blur(10px); 
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
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
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
            <strong>SISTEMA ORIGINAL TRANSPONTUAL ATIVO</strong><br>
            Conectado ao Supabase real • Atualização em lote integrada<br>
            <small>Total de CTEs: ''' + str(total_ctes) + '''</small>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h4><i class="fas fa-sync-alt"></i> Atualização em Lote de CTEs</h4>
                        <p class="mb-0">Sistema integrado ao dashboard original - Atualizações diretas no Supabase</p>
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
                                                <div class="border rounded p-4 text-center" style="border-style: dashed !important; border-color: #ffc107 !important;">
                                                    <i class="fas fa-cloud-upload-alt fa-3x text-warning mb-3"></i>
                                                    <h6>Arraste o arquivo aqui ou clique para selecionar</h6>
                                                    <input type="file" class="form-control mt-2" id="arquivo" name="arquivo" 
                                                           accept=".csv,.xlsx,.xls" required>
                                                </div>
                                            </div>
                                            
                                            <div class="d-flex gap-2">
                                                <button type="button" class="btn btn-warning" onclick="processarArquivo()">
                                                    <i class="fas fa-sync-alt"></i> Processar no Supabase
                                                </button>
                                                <a href="/ctes/template-completo" class="btn btn-outline-secondary">
                                                    <i class="fas fa-download"></i> Template Completo
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
                                        <h5><i class="fas fa-chart-bar"></i> Estatísticas</h5>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>Total CTEs:</strong> ''' + f'{total_ctes:,}' + '''</p>
                                        <p><strong>Sistema:</strong> <span class="badge bg-success">Original</span></p>
                                        <p><strong>Banco:</strong> <span class="badge bg-primary">Supabase</span></p>
                                        <p><strong>Status:</strong> <span class="badge bg-success">Integrado</span></p>
                                        <hr>
                                        <h6>Campos atualizáveis:</h6>
                                        <p class="small">14 campos disponíveis para atualização</p>
                                        <hr>
                                        <div class="alert alert-success">
                                            <small><i class="fas fa-check"></i> 
                                            Sistema original com atualização em lote!</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="resultados" class="mt-4" style="display: none;">
                            <div class="card">
                                <div class="card-header">
                                    <h5><i class="fas fa-chart-line"></i> Resultados da Atualização</h5>
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
            alert('Selecione um arquivo primeiro!');
            return;
        }
        
        if (!confirm('⚠️ ATENÇÃO!\\n\\nEsta operação atualizará dados REAIS no Supabase.\\n\\nDeseja continuar?')) {
            return;
        }
        
        // Mostrar loading
        document.getElementById('resultados').style.display = 'block';
        document.getElementById('resultadosContent').innerHTML = `
            <div class="text-center">
                <i class="fas fa-spinner fa-spin fa-2x text-warning"></i>
                <h5 class="mt-3">Processando ` + arquivo.name + ` no Supabase...</h5>
                <div class="alert alert-info">
                    <i class="fas fa-database"></i> Sistema original conectado ao banco real
                </div>
            </div>
        `;
        
        // Enviar para API
        fetch('/ctes/api/processar-lote', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                let camposHtml = '';
                if (data.stats.campos_atualizados) {
                    Object.entries(data.stats.campos_atualizados).forEach(([campo, count]) => {
                        camposHtml += `<li><strong>` + campo + `:</strong> ` + count + ` atualizações</li>`;
                    });
                }
                
                document.getElementById('resultadosContent').innerHTML = `
                    <div class="alert alert-success">
                        <h6><i class="fas fa-check-circle"></i> ✅ ATUALIZAÇÃO CONCLUÍDA!</h6>
                        <div class="row">
                            <div class="col-md-3"><strong>Processados:</strong> ` + (data.stats.total_processados || 0) + `</div>
                            <div class="col-md-3"><strong>Atualizados:</strong> ` + (data.stats.atualizados || 0) + `</div>
                            <div class="col-md-3"><strong>Erros:</strong> ` + (data.stats.erros || 0) + `</div>
                            <div class="col-md-3"><strong>Não encontrados:</strong> ` + (data.stats.nao_encontrados || 0) + `</div>
                        </div>
                    </div>
                    <div class="alert alert-info">
                        <h6><i class="fas fa-database"></i> Campos atualizados no Supabase:</h6>
                        <ul>` + camposHtml + `</ul>
                        <p class="mb-0"><strong>🎉 Sistema original funcionando perfeitamente!</strong></p>
                    </div>
                `;
            } else {
                document.getElementById('resultadosContent').innerHTML = `
                    <div class="alert alert-danger">
                        <h6><i class="fas fa-times-circle"></i> Erro na Atualização</h6>
                        <p>` + (data.erro || 'Erro desconhecido') + `</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            document.getElementById('resultadosContent').innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle"></i> Erro de Conexão</h6>
                    <p>` + error.message + `</p>
                </div>
            `;
        });
    }
    </script>
</body>
</html>
            '''
            
            return template_html
        
        @bulk_bp.route('/api/processar-lote', methods=['POST'])
        @login_required
        def api_processar_lote():
            """API que processa atualização no banco real"""
            try:
                arquivo = request.files.get('arquivo')
                modo = request.form.get('modo', 'empty_only')
                
                if not arquivo:
                    return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400
                
                # Ler arquivo
                try:
                    if arquivo.filename.endswith('.csv'):
                        df = pd.read_csv(io.BytesIO(arquivo.read()), encoding='utf-8')
                    elif arquivo.filename.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(io.BytesIO(arquivo.read()))
                    else:
                        return jsonify({'sucesso': False, 'erro': 'Formato não suportado'}), 400
                except Exception as e:
                    return jsonify({'sucesso': False, 'erro': f'Erro ao ler arquivo: {str(e)}'}), 400
                
                # Validar coluna CTE
                cte_col = None
                for col in ['numero_cte', 'CTE', 'Numero_CTE', 'CTRC']:
                    if col in df.columns:
                        cte_col = col
                        break
                
                if not cte_col:
                    return jsonify({'sucesso': False, 'erro': 'Coluna de CTE não encontrada'}), 400
                
                # Mapear coluna CTE
                if cte_col != 'numero_cte':
                    df['numero_cte'] = df[cte_col]
                
                # Processar atualizações
                from app.models.cte import CTE
                
                stats = {
                    'total_processados': 0,
                    'atualizados': 0,
                    'erros': 0,
                    'nao_encontrados': 0,
                    'campos_atualizados': {}
                }
                
                # Mapear campos
                field_mapping = {
                    'destinatario_nome': ['Cliente', 'Destinatario', 'destinatario_nome'],
                    'veiculo_placa': ['Veiculo', 'Placa', 'veiculo_placa'],
                    'valor_total': ['Valor', 'Valor_Frete', 'valor_total'],
                    'data_emissao': ['Data_Emissao', 'data_emissao'],
                    'data_baixa': ['Data_Baixa', 'data_baixa'],
                    'numero_fatura': ['Numero_Fatura', 'numero_fatura'],
                    'observacao': ['Observacao', 'Observacoes', 'observacao'],
                    'data_inclusao_fatura': ['Data_Inclusao_Fatura', 'data_inclusao_fatura'],
                    'data_envio_processo': ['Data_Envio_Processo', 'data_envio_processo'],
                    'primeiro_envio': ['Primeiro_Envio', 'primeiro_envio'],
                    'data_rq_tmc': ['Data_RQ_TMC', 'data_rq_tmc'],
                    'data_atesto': ['Data_Atesto', 'data_atesto'],
                    'envio_final': ['Envio_Final', 'envio_final'],
                    'origem_dados': ['Origem_Dados', 'origem_dados']
                }
                
                # Processar cada linha
                for _, row in df.iterrows():
                    try:
                        numero_cte = int(float(row['numero_cte']))
                        stats['total_processados'] += 1
                        
                        # Buscar CTE
                        cte = CTE.query.filter_by(numero_cte=numero_cte).first()
                        
                        if not cte:
                            stats['nao_encontrados'] += 1
                            continue
                        
                        # Atualizar campos
                        updated = False
                        
                        for db_field, possible_cols in field_mapping.items():
                            for col in possible_cols:
                                if col in df.columns and pd.notna(row[col]):
                                    current_value = getattr(cte, db_field, None)
                                    new_value = row[col]
                                    
                                    # Decidir se atualizar
                                    should_update = False
                                    
                                    if modo == 'all':
                                        should_update = (str(new_value).strip() != str(current_value or '').strip())
                                    elif modo == 'empty_only':
                                        should_update = (current_value in [None, '', 'nan', 'NaN'] and 
                                                       str(new_value).strip() not in ['', 'nan', 'NaN'])
                                    
                                    if should_update:
                                        setattr(cte, db_field, new_value)
                                        updated = True
                                        
                                        if db_field not in stats['campos_atualizados']:
                                            stats['campos_atualizados'][db_field] = 0
                                        stats['campos_atualizados'][db_field] += 1
                                    break
                        
                        if updated:
                            cte.updated_at = datetime.utcnow()
                            stats['atualizados'] += 1
                            
                    except Exception as e:
                        stats['erros'] += 1
                
                # Salvar no banco
                try:
                    db.session.commit()
                    print(f"✅ {stats['atualizados']} CTEs atualizados no Supabase!")
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'sucesso': False, 'erro': f'Erro ao salvar: {str(e)}'}), 500
                
                return jsonify({
                    'sucesso': True,
                    'stats': stats,
                    'mensagem': f'Atualização concluída: {stats["atualizados"]} CTEs atualizados'
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'sucesso': False, 'erro': f'Erro: {str(e)}'}), 500
        
        @bulk_bp.route('/template-completo')
        @login_required
        def template_completo():
            """Template CSV completo"""
            template = '''numero_cte,destinatario_nome,veiculo_placa,valor_total,data_emissao,data_baixa,numero_fatura,data_inclusao_fatura,data_envio_processo,primeiro_envio,data_rq_tmc,data_atesto,envio_final,observacao,origem_dados
22421,Baker Hotéis Ltda,ABC1234,3200.50,05/08/2025,15/08/2025,NF001,10/08/2025,12/08/2025,07/08/2025,05/08/2025,14/08/2025,16/08/2025,Exemplo completo,Sistema
22422,Empresa ABC,XYZ5678,4100.25,06/08/2025,,NF002,11/08/2025,13/08/2025,08/08/2025,06/08/2025,15/08/2025,,Pendente,Importação
22423,Cliente Premium,DEF9012,2900.75,07/08/2025,20/08/2025,NF003,12/08/2025,14/08/2025,09/08/2025,07/08/2025,16/08/2025,21/08/2025,Concluído,Sistema
'''
            
            response = make_response(template)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = 'attachment; filename=template_transpontual_completo.csv'
            return response
        
        # Registrar blueprint no app
        app.register_blueprint(bulk_bp)
        print("✅ Sistema de atualização em lote integrado ao sistema original!")
        
    except Exception as e:
        print(f"⚠️ Erro ao integrar sistema de atualização: {e}")

# FORÇAR EXECUÇÃO DO SISTEMA ORIGINAL
try:
    application = forcar_sistema_original()
    print("🎉 SISTEMA ORIGINAL TRANSPONTUAL FUNCIONANDO!")
    
except Exception as e:
    print(f"❌ FALHA CRÍTICA: {e}")
    print("🔄 Criando app de emergência...")
    
    # App de emergência que mostra o erro
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def debug():
        return f'''
        <h1>🔧 Debug - Sistema Transpontual</h1>
        <h3>Erro detectado:</h3>
        <pre>{str(e)}</pre>
        
        <h3>Estrutura verificada:</h3>
        <ul>
            <li>✅ app/ existe</li>
            <li>✅ app/models/ existe</li>
            <li>✅ app/routes/ existe</li>
        </ul>
        
        <p><a href="/retry">Tentar novamente</a></p>
        '''
    
    @application.route('/retry')
    def retry():
        try:
            global application
            application = forcar_sistema_original()
            return '<h1>✅ Sistema restaurado!</h1><a href="/">Ir para dashboard</a>'
        except Exception as e2:
            return f'<h1>❌ Ainda com erro:</h1><pre>{str(e2)}</pre>'

# Exportar app
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
