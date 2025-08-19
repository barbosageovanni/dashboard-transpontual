// Sistema de CTEs - JavaScript CORRIGIDO
$(document).ready(function() {
    configurarEventosCTEs();
    carregarListaCTEs();
});

// Variáveis globais para filtros
let filtrosAtuais = {};
let paginaAtual = 1;

function configurarEventosCTEs() {
    // Form de inserção
    $('#formInserirCTE').on('submit', function(e) {
        e.preventDefault();
        inserirCTE();
    });

    // Form de edição
    $('#formEditarCTE').on('submit', function(e) {
        e.preventDefault();
        salvarEdicaoCTE();
    });

    // Filtro de texto com Enter
    $('#filtroTexto').on('keypress', function(e) {
        if (e.which === 13) { // Enter
            aplicarFiltros();
        }
    });

    // Mudança nos selects de filtro
    $('#filtroStatusBaixa, #filtroStatusProcesso').on('change', function() {
        aplicarFiltros();
    });

    // Mudança nas datas
    $('#dataInicio, #dataFim').on('change', function() {
        aplicarFiltros();
    });
}

// ✅ CORREÇÃO: Função de debug para testar específico do CTE 22403
function testarFiltros() {
    console.log('🔍 Testando sistema completo...');
    
    // Teste específico do CTE 22403
    fetch('/ctes/api/buscar/22403')
      .then(r => r.json())
      .then(data => {
        console.log('🔍 CTE 22403 Debug:', data.cte);
        console.log('📊 Status atual:', data.cte.status_processo);
        console.log('✅ Processo completo?', data.cte.processo_completo);
        
        // Verificar cada data individualmente
        console.log('📅 Datas:');
        console.log('- Data Emissão:', data.cte.data_emissao);
        console.log('- Primeiro Envio:', data.cte.primeiro_envio);
        console.log('- Data Atesto:', data.cte.data_atesto);
        console.log('- Envio Final:', data.cte.envio_final);
        console.log('- Data Baixa:', data.cte.data_baixa);
        
        if (data.cte.debug_datas) {
            console.log('🐛 Debug datas preenchidas:', data.cte.debug_datas);
        }
      })
      .catch(err => console.error('❌ Erro teste CTE 22403:', err));
    
    // Teste de filtros gerais
    $.ajax({
        url: '/ctes/api/listar',
        method: 'GET',
        data: { search: '22403' },
        success: function(response) {
            console.log('🔍 Teste busca CTE 22403:', response);
        },
        error: function(xhr) {
            console.error('❌ Erro teste busca:', xhr);
        }
    });
}

function aplicarFiltros() {
    // Coletar valores dos filtros
    filtrosAtuais = {
        search: $('#filtroTexto').val().trim(),
        status_baixa: $('#filtroStatusBaixa').val(),
        status_processo: $('#filtroStatusProcesso').val(),
        data_inicio: $('#dataInicio').val(),
        data_fim: $('#dataFim').val()
    };
    
    // Debug
    console.log('Aplicando filtros:', filtrosAtuais);
    
    paginaAtual = 1; // Resetar para primeira página
    carregarListaCTEs();
}

function limparFiltros() {
    $('#filtroTexto').val('');
    $('#filtroStatusBaixa').val('');
    $('#filtroStatusProcesso').val('');
    $('#dataInicio').val('');
    $('#dataFim').val('');
    
    filtrosAtuais = {};
    paginaAtual = 1;
    carregarListaCTEs();
}

function carregarListaCTEs(pagina = 1) {
    paginaAtual = pagina;
    
    // Preparar parâmetros
    const params = {
        page: pagina,
        per_page: 50,
        ...filtrosAtuais
    };
    
    // Debug
    console.log('Carregando CTEs com parâmetros:', params);
    
    // Mostrar loading
    const tbody = $('#tabelaCTEs tbody');
    tbody.html(`
        <tr>
            <td colspan="7" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <br>Carregando dados...
            </td>
        </tr>
    `);
    
    $.ajax({
        url: '/ctes/api/listar',
        method: 'GET',
        data: params,
        timeout: 30000, // 30 segundos timeout
        success: function(response) {
            console.log('Resposta da API:', response);
            
            if (response.success) {
                preencherTabelaCTEs(response.ctes);
                atualizarPaginacao(response);
                $('#totalRegistros').text(`${response.total} registro(s) encontrado(s)`);
                
                // Debug info
                if (response.debug_info) {
                    console.log('Debug info:', response.debug_info);
                }
            } else {
                console.error('Erro na resposta:', response.error);
                mostrarErroTabela(`Erro: ${response.error}`);
            }
        },
        error: function(xhr, status, error) {
            console.error('Erro AJAX:', {
                status: xhr.status,
                statusText: xhr.statusText,
                response: xhr.responseText,
                error: error
            });
            
            let mensagemErro = 'Erro ao carregar dados';
            
            if (xhr.status === 0) {
                mensagemErro = 'Erro de conexão com o servidor';
            } else if (xhr.status >= 500) {
                mensagemErro = 'Erro interno do servidor';
            } else if (xhr.status === 404) {
                mensagemErro = 'Endpoint não encontrado';
            }
            
            mostrarErroTabela(mensagemErro);
            $('#totalRegistros').text('Erro ao carregar dados');
        }
    });
}

function mostrarErroTabela(mensagem) {
    const tbody = $('#tabelaCTEs tbody');
    tbody.html(`
        <tr>
            <td colspan="7" class="text-center text-danger py-4">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i><br>
                ${mensagem}<br>
                <small class="text-muted">Verifique o console para mais detalhes</small>
            </td>
        </tr>
    `);
}

function preencherTabelaCTEs(ctes) {
    const tbody = $('#tabelaCTEs tbody');
    tbody.empty();

    if (ctes.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2"></i><br>
                    Nenhum CTE encontrado com os filtros aplicados
                </td>
            </tr>
        `);
        return;
    }

    ctes.forEach(cte => {
        const statusBaixa = cte.has_baixa ? 
            '<span class="badge bg-success">Baixado</span>' : 
            '<span class="badge bg-warning text-dark">Pendente</span>';
        
        // ✅ CORREÇÃO: Melhor identificação de status de processo
        let statusProcesso;
        let processoClass;
        
        if (cte.status_processo === 'Finalizado') {
            statusProcesso = '<span class="badge bg-success">Finalizado</span>';
        } else if (cte.status_processo === 'Completo') {
            statusProcesso = '<span class="badge bg-primary">Completo</span>';
        } else if (cte.status_processo === 'Atestado') {
            statusProcesso = '<span class="badge bg-info">Atestado</span>';
        } else if (cte.status_processo === 'Enviado') {
            statusProcesso = '<span class="badge bg-warning">Enviado</span>';
        } else if (cte.status_processo === 'Emitido') {
            statusProcesso = '<span class="badge bg-secondary">Emitido</span>';
        } else {
            statusProcesso = '<span class="badge bg-light text-dark">Pendente</span>';
        }

        const dataEmissao = cte.data_emissao ? 
            new Date(cte.data_emissao).toLocaleDateString('pt-BR') : 
            '<span class="text-muted">N/A</span>';

        const row = `
            <tr>
                <td><strong>${cte.numero_cte}</strong></td>
                <td>${cte.destinatario_nome || '<span class="text-muted">N/A</span>'}</td>
                <td><strong>R$ ${cte.valor_total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</strong></td>
                <td>${dataEmissao}</td>
                <td>${statusBaixa}</td>
                <td>${statusProcesso}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary" onclick="editarCTE(${cte.numero_cte})" 
                                title="Editar" data-bs-toggle="tooltip">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="excluirCTE(${cte.numero_cte})" 
                                title="Excluir" data-bs-toggle="tooltip">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        
        tbody.append(row);
    });

    // Ativar tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
}

function atualizarPaginacao(response) {
    const paginacao = $('#paginacao');
    const ul = paginacao.find('ul');
    ul.empty();

    if (response.pages <= 1) {
        paginacao.hide();
        return;
    }

    // Botão Anterior
    const prevDisabled = !response.has_prev ? 'disabled' : '';
    ul.append(`
        <li class="page-item ${prevDisabled}">
            <a class="page-link" href="#" onclick="carregarListaCTEs(${response.current_page - 1})">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `);

    // Páginas
    const startPage = Math.max(1, response.current_page - 2);
    const endPage = Math.min(response.pages, response.current_page + 2);

    for (let i = startPage; i <= endPage; i++) {
        const active = i === response.current_page ? 'active' : '';
        ul.append(`
            <li class="page-item ${active}">
                <a class="page-link" href="#" onclick="carregarListaCTEs(${i})">${i}</a>
            </li>
        `);
    }

    // Botão Próximo
    const nextDisabled = !response.has_next ? 'disabled' : '';
    ul.append(`
        <li class="page-item ${nextDisabled}">
            <a class="page-link" href="#" onclick="carregarListaCTEs(${response.current_page + 1})">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `);

    paginacao.show();
}

// ✅ FUNÇÕES DE AUDITORIA E CORREÇÃO
function executarAuditoria() {
    if (!confirm('Executar auditoria para identificar inconsistências nos status?\n\nIsso pode demorar alguns segundos.')) {
        return;
    }
    
    $.ajax({
        url: '/ctes/api/auditoria',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                console.log('📊 Auditoria completa:', response);
                
                let mensagem = `✅ Auditoria Concluída!\n\n`;
                mensagem += `CTEs verificados: ${response.ctes_verificados}\n`;
                mensagem += `Problemas encontrados: ${response.problemas_encontrados}\n\n`;
                
                if (response.problemas.length > 0) {
                    mensagem += `Primeiros problemas:\n`;
                    response.problemas.slice(0, 5).forEach(p => {
                        mensagem += `• CTE ${p.numero_cte}: ${p.problema}\n`;
                    });
                    
                    if (response.problemas.length > 5) {
                        mensagem += `... e mais ${response.problemas.length - 5} problemas.\n`;
                    }
                    
                    mensagem += `\nVerifique o console (F12) para detalhes completos.`;
                }
                
                alert(mensagem);
            } else {
                alert('❌ Erro na auditoria: ' + response.error);
            }
        },
        error: function(xhr) {
            alert('❌ Erro ao executar auditoria');
            console.error('Erro auditoria:', xhr);
        }
    });
}

function corrigirTodosStatus() {
    if (!confirm('Recalcular status de todos os CTEs?\n\nEsta ação pode demorar alguns minutos.')) {
        return;
    }
    
    $.ajax({
        url: '/ctes/api/corrigir-status',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                alert(`✅ ${response.message}`);
                carregarListaCTEs(); // Recarregar a lista
            } else {
                alert('❌ Erro: ' + response.error);
            }
        },
        error: function(xhr) {
            alert('❌ Erro ao corrigir status');
            console.error('Erro correção:', xhr);
        }
    });
}

// Funções de Download
function downloadExcel() {
    baixarArquivo('/ctes/api/download/excel', 'Excel');
}

function downloadPDF() {
    baixarArquivo('/ctes/api/download/pdf', 'PDF');
}

function downloadCSV() {
    baixarArquivo('/ctes/api/download/csv', 'CSV');
}

function baixarArquivo(url, tipo) {
    // Adicionar filtros atuais à URL
    const params = new URLSearchParams(filtrosAtuais);
    const urlCompleta = `${url}?${params.toString()}`;
    
    // Criar elemento de download temporário
    const link = document.createElement('a');
    link.href = urlCompleta;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Mostrar feedback
    const toast = `
        <div class="toast show position-fixed top-0 end-0 m-3" role="alert">
            <div class="toast-header">
                <i class="fas fa-download text-success me-2"></i>
                <strong class="me-auto">Download ${tipo}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                Download iniciado com os filtros aplicados
            </div>
        </div>
    `;
    
    $('body').append(toast);
    
    // Remover toast após 3 segundos
    setTimeout(() => {
        $('.toast').fadeOut();
    }, 3000);
}

// ✅ CORREÇÃO: Função de inserção com URL corrigida
function inserirCTE() {
    const formData = obterDadosFormulario('#formInserirCTE');

    // Validações básicas
    if (!formData.numero_cte) {
        alert('Número do CTE é obrigatório');
        return;
    }

    if (!formData.valor_total || formData.valor_total <= 0) {
        alert('Valor total deve ser maior que zero');
        return;
    }

    $.ajax({
        url: '/ctes/api/inserir', // ✅ URL corrigida
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                alert('✅ ' + response.message);
                $('#formInserirCTE')[0].reset();
                carregarListaCTEs();
            } else {
                alert('❌ ' + response.message);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            alert('❌ ' + (response ? response.message : 'Erro ao inserir CTE'));
        }
    });
}

// ✅ CORREÇÃO: Função de busca com URL corrigida
function buscarCTEParaEdicao() {
    const numeroCte = $('#numero_cte_busca').val();
    
    if (!numeroCte) {
        alert('Digite o número do CTE');
        return;
    }

    $.ajax({
        url: `/ctes/api/buscar/${numeroCte}`, // ✅ URL corrigida
        method: 'GET',
        success: function(response) {
            if (response.success) {
                preencherFormularioEdicao(response.cte);
                $('#areaEdicao').show();
                $('#numeroCteEdicao').text(numeroCte);
            } else {
                alert('❌ ' + response.message);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            alert('❌ ' + (response ? response.message : 'Erro ao buscar CTE'));
        }
    });
}

function preencherFormularioEdicao(cte) {
    // Preencher dados principais
    $('#destinatario_nome_edit').val(cte.destinatario_nome || '');
    $('#valor_total_edit').val(cte.valor_total || '');
    $('#data_emissao_edit').val(cte.data_emissao || '');
    $('#veiculo_placa_edit').val(cte.veiculo_placa || '');
    $('#numero_fatura_edit').val(cte.numero_fatura || '');
    $('#data_baixa_edit').val(cte.data_baixa || '');
    
    // Preencher datas do processo
    $('#data_inclusao_fatura_edit').val(cte.data_inclusao_fatura || '');
    $('#data_envio_processo_edit').val(cte.data_envio_processo || '');
    $('#primeiro_envio_edit').val(cte.primeiro_envio || '');
    $('#data_rq_tmc_edit').val(cte.data_rq_tmc || '');
    $('#data_atesto_edit').val(cte.data_atesto || '');
    $('#envio_final_edit').val(cte.envio_final || '');
    
    // Observações
    $('#observacao_edit').val(cte.observacao || '');
}

function salvarEdicaoCTE() {
    const numeroCte = $('#numeroCteEdicao').text();
    const formData = obterDadosFormulario('#formEditarCTE');

    $.ajax({
        url: `/ctes/api/atualizar/${numeroCte}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                alert('✅ ' + response.message);
                cancelarEdicao();
                carregarListaCTEs();
            } else {
                alert('❌ ' + response.message);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            alert('❌ ' + (response ? response.message : 'Erro ao atualizar CTE'));
        }
    });
}

function cancelarEdicao() {
    $('#areaEdicao').hide();
    $('#numero_cte_busca').val('');
    $('#formEditarCTE')[0].reset();
}

function excluirCTE(numeroCte) {
    if (!confirm(`Tem certeza que deseja excluir o CTE ${numeroCte}?\n\nEsta ação não pode ser desfeita.`)) {
        return;
    }

    $.ajax({
        url: `/ctes/api/excluir/${numeroCte}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                alert('✅ ' + response.message);
                carregarListaCTEs();
            } else {
                alert('❌ ' + response.message);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            alert('❌ ' + (response ? response.message : 'Erro ao excluir CTE'));
        }
    });
}

function obterDadosFormulario(seletor) {
    const form = $(seletor);
    const formData = {};
    
    form.find('input, textarea, select').each(function() {
        const campo = $(this);
        const name = campo.attr('name');
        const value = campo.val();
        
        if (name) {
            // Não incluir campos vazios para evitar sobrescrever com valores nulos
            if (value && value.trim() !== '') {
                formData[name] = value.trim();
            }
        }
    });
    
    return formData;
}

function editarCTE(numeroCte) {
    $('#numero_cte_busca').val(numeroCte);
    $('#buscar-tab').click();
    setTimeout(() => {
        buscarCTEParaEdicao();
    }, 300);
}

// ============================================================================
// ADICIONAR ESTAS FUNÇÕES AO ARQUIVO static/js/ctes.js
// ============================================================================

// Adicionar ao arquivo static/js/ctes.js

/**
 * Sistema de Importação de CTEs em Lote
 * Baseado no padrão do sistema de baixas
 */

function configurarImportacaoLote() {
    // Configurar evento de upload
    $('#fileInputLote').on('change', function() {
        const file = this.files[0];
        if (file) {
            mostrarPreviaArquivo(file);
        } else {
            $('#previaArquivo').hide();
        }
    });
    
    // Configurar drag and drop
    const dropArea = $('#dropAreaLote');
    if (dropArea.length) {
        dropArea.on('dragover', function(e) {
            e.preventDefault();
            $(this).addClass('border-success bg-light');
        });
        
        dropArea.on('dragleave', function(e) {
            e.preventDefault();
            $(this).removeClass('border-success bg-light');
        });
        
        dropArea.on('drop', function(e) {
            e.preventDefault();
            $(this).removeClass('border-success bg-light');
            
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                $('#fileInputLote')[0].files = files;
                $('#fileInputLote').trigger('change');
            }
        });
    }
}

function processarArquivoLote() {
    const file = $('#fileInputLote')[0].files[0];
    
    if (!file) {
        alert('⚠️ Selecione um arquivo CSV');
        return;
    }
    
    // Validações básicas
    if (!file.name.toLowerCase().endsWith('.csv')) {
        alert('❌ Apenas arquivos CSV são permitidos');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        alert('❌ Arquivo muito grande. Máximo: 50MB');
        return;
    }
    
    const formData = new FormData();
    formData.append('arquivo', file);

    // Esconder resultados anteriores
    $('#resultadosLote').hide();
    
    // Mostrar loading
    mostrarLoadingImportacao();

    $.ajax({
        url: '/ctes/api/importar/lote',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        timeout: 300000, // 5 minutos
        success: function(response) {
            esconderLoadingImportacao();
            
            if (response.sucesso) {
                mostrarResultadosLote(response.resultados);
                
                // Recarregar lista de CTEs se estivermos na página principal
                if (typeof carregarListaCTEs === 'function') {
                    setTimeout(carregarListaCTEs, 2000);
                }
                
                // Limpar input file
                $('#fileInputLote').val('');
            } else {
                alert('❌ ' + response.erro);
            }
        },
        error: function(xhr) {
            esconderLoadingImportacao();
            const response = xhr.responseJSON;
            alert('❌ ' + (response ? response.erro : 'Erro ao processar arquivo'));
        }
    });
}

function mostrarLoadingImportacao() {
    const loadingHtml = `
        <div class="text-center py-4" id="loadingImportacao">
            <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">Processando...</span>
            </div>
            <br><br>
            <h6>📄 Processando Importação...</h6>
            <p class="text-muted">
                Validando dados, identificando duplicatas e inserindo CTEs...<br>
                <small>Isso pode levar alguns minutos dependendo do tamanho do arquivo</small>
            </p>
        </div>
    `;
    
    $('#resultadosLote').html(loadingHtml).show();
}

function esconderLoadingImportacao() {
    $('#loadingImportacao').remove();
}

function mostrarResultadosLote(resultados) {
    const alertClass = resultados.erros > 0 ? 'alert-warning' : 'alert-success';
    const iconClass = resultados.erros > 0 ? 'fa-exclamation-triangle' : 'fa-check-circle';
    
    const resumoHtml = `
        <div class="alert ${alertClass}">
            <h6><i class="fas ${iconClass}"></i> Importação Concluída!</h6>
            <div class="row text-center">
                <div class="col-md-3">
                    <strong>${resultados.processados}</strong><br>
                    <small>Processados</small>
                </div>
                <div class="col-md-3">
                    <strong class="text-success">${resultados.sucessos}</strong><br>
                    <small>Inseridos</small>
                </div>
                <div class="col-md-3">
                    <strong class="text-info">${resultados.ctes_existentes || 0}</strong><br>
                    <small>Já Existiam</small>
                </div>
                <div class="col-md-3">
                    <strong class="text-danger">${resultados.erros}</strong><br>
                    <small>Erros</small>
                </div>
            </div>
        </div>
    `;
    
    let detalhesHtml = '';
    
    // Mostrar detalhes dos erros se houver
    if (resultados.erros > 0 && resultados.detalhes) {
        const erros = resultados.detalhes.filter(d => !d.sucesso).slice(0, 10);
        
        if (erros.length > 0) {
            detalhesHtml += `
                <div class="mt-3">
                    <h6><i class="fas fa-exclamation-circle text-warning"></i> Primeiros Erros Encontrados:</h6>
                    <div class="alert alert-light">
                        <ul class="mb-0 small">
            `;
            
            erros.forEach(erro => {
                detalhesHtml += `<li>CTE ${erro.cte}: ${erro.mensagem}</li>`;
            });
            
            detalhesHtml += `
                        </ul>
                    </div>
                </div>
            `;
        }
    }
    
    // Informações adicionais
    let infoAdicionalHtml = '';
    if (resultados.tempo_processamento) {
        infoAdicionalHtml += `
            <div class="text-muted small mt-2">
                ⏱️ Tempo de processamento: ${resultados.tempo_processamento.toFixed(2)} segundos
            </div>
        `;
    }
    
    const htmlCompleto = resumoHtml + detalhesHtml + infoAdicionalHtml;
    $('#resultadosLote').html(htmlCompleto).show();
    
    console.log('📊 Resultados da importação:', resultados);
}

function mostrarPreviaArquivo(file) {
    if (!file) return;
    
    // Mostrar loading
    $('#previaArquivo').html(`
        <div class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-info" role="status"></div>
            <span class="ms-2">Analisando arquivo...</span>
        </div>
    `).show();
    
    validarArquivoImportacao(file)
        .then(function(stats) {
            const previaHtml = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-file-csv"></i> Prévia do Arquivo: ${stats.arquivo.nome}</h6>
                    <div class="row small">
                        <div class="col-md-6">
                            • Total de linhas: ${stats.arquivo.linhas_totais}<br>
                            • Linhas válidas: ${stats.arquivo.linhas_validas}<br>
                            • Linhas descartadas: ${stats.arquivo.linhas_descartadas}
                        </div>
                        <div class="col-md-6">
                            • CTEs novos: <strong class="text-success">${stats.analise.ctes_novos}</strong><br>
                            • CTEs existentes: <strong class="text-warning">${stats.analise.ctes_existentes}</strong><br>
                            ${stats.duplicatas.tem_duplicatas ? 
                                `• Duplicatas: <strong class="text-danger">${stats.duplicatas.quantidade}</strong>` : 
                                '• Sem duplicatas ✓'}
                        </div>
                    </div>
                    
                    ${stats.preview && stats.preview.length > 0 ? `
                    <details class="mt-2">
                        <summary><small>Ver primeiros registros</small></summary>
                        <div class="table-responsive mt-2">
                            <table class="table table-sm table-bordered">
                                <thead>
                                    <tr>
                                        <th>CTE</th>
                                        <th>Cliente</th>
                                        <th>Valor</th>
                                        <th>Emissão</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${stats.preview.slice(0, 3).map(row => `
                                        <tr>
                                            <td>${row.numero_cte}</td>
                                            <td>${row.destinatario_nome || 'N/A'}</td>
                                            <td>R$ ${(row.valor_total || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                                            <td>${row.data_emissao || 'N/A'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </details>
                    ` : ''}
                </div>
            `;
            
            $('#previaArquivo').html(previaHtml);
        })
        .catch(function(error) {
            $('#previaArquivo').html(`
                <div class="alert alert-danger">
                    <strong>❌ Erro na validação:</strong> ${error}
                </div>
            `);
        });
}

function validarArquivoImportacao(file) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('arquivo_csv', file);
        
        $.ajax({
            url: '/ctes/api/validar-csv',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            timeout: 30000,
            success: function(response) {
                if (response.sucesso) {
                    resolve(response.estatisticas);
                } else {
                    reject(response.erro);
                }
            },
            error: function(xhr) {
                const response = xhr.responseJSON;
                reject(response ? response.erro : 'Erro na validação');
            }
        });
    });
}

function baixarTemplateCTE() {
    const link = document.createElement('a');
    link.href = '/ctes/api/template-csv';
    link.download = 'template_ctes.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Feedback visual
    const toast = `
        <div class="toast show position-fixed top-0 end-0 m-3" role="alert">
            <div class="toast-header">
                <i class="fas fa-download text-success me-2"></i>
                <strong class="me-auto">Template CSV</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                Download do template iniciado
            </div>
        </div>
    `;
    
    $('body').append(toast);
    setTimeout(() => $('.toast').fadeOut(), 3000);
}

// Adicionar configuração quando documento carregar
$(document).ready(function() {
    configurarImportacaoLote();
});