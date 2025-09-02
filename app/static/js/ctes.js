/**
 * Sistema de CTEs - JavaScript COMPLETO E CORRIGIDO
 * static/js/ctes.js - Versão de Produção
 * 
 * Inclui: Listagem, CRUD, Filtros, Export e Upload
 */

// ===================================
// CONFIGURAÇÃO E INICIALIZAÇÃO
// ===================================

// Variáveis globais
let filtrosAtuais = {};
let paginaAtual = 1;
let totalPaginas = 1;

// Inicialização principal
$(document).ready(function() {
    console.log('🚀 Sistema de CTEs inicializado');
    configurarEventos();
    carregarListaCTEs();
    testConexao();
});

function configurarEventos() {
    // Eventos de filtros
    configurarEventosFiltros();
    
    // Eventos de CRUD
    configurarEventosCRUD();
    
    // Eventos de export
    configurarEventosExport();
    
    // Eventos de debug
    configurarEventosDebug();
}

// ===================================
// SISTEMA DE FILTROS E BUSCA
// ===================================

function configurarEventosFiltros() {
    // Filtro de texto com Enter
    $('#filtroTexto').on('keypress', function(e) {
        if (e.which === 13) {
            aplicarFiltros();
        }
    });
    
    // Mudança nos selects
    $('#filtroStatusBaixa, #filtroStatusProcesso').on('change', aplicarFiltros);
    
    // Mudança nas datas
    $('#dataInicio, #dataFim').on('change', aplicarFiltros);
    
    // Botões
    $('#btnBuscar').on('click', aplicarFiltros);
    $('#btnLimpar').on('click', limparFiltros);
}

function aplicarFiltros() {
    console.log('🔍 Aplicando filtros...');
    
    // Coletar valores dos filtros
    filtrosAtuais = {
        search: $('#filtroTexto').val().trim(),
        status_baixa: $('#filtroStatusBaixa').val(),
        status_processo: $('#filtroStatusProcesso').val(),
        data_inicio: $('#dataInicio').val(),
        data_fim: $('#dataFim').val()
    };
    
    console.log('Filtros aplicados:', filtrosAtuais);
    
    paginaAtual = 1;
    carregarListaCTEs();
}

function limparFiltros() {
    console.log('🧹 Limpando filtros...');
    
    $('#filtroTexto').val('');
    $('#filtroStatusBaixa').val('');
    $('#filtroStatusProcesso').val('');
    $('#dataInicio').val('');
    $('#dataFim').val('');
    
    filtrosAtuais = {};
    paginaAtual = 1;
    carregarListaCTEs();
}

// ===================================
// CARREGAMENTO DA LISTA DE CTEs
// ===================================

function carregarListaCTEs(pagina = 1) {
    paginaAtual = pagina;
    
    console.log(`📊 Carregando CTEs - Página ${pagina}`);
    
    // Preparar parâmetros
    const params = {
        page: pagina,
        per_page: 50,
        ...filtrosAtuais
    };
    
    console.log('Parâmetros da requisição:', params);
    
    // Mostrar loading na tabela
    mostrarLoadingTabela();
    
    // Fazer requisição
    $.ajax({
        url: '/ctes/api/listar',
        method: 'GET',
        data: params,
        timeout: 30000,
        success: function(response) {
            console.log('✅ Resposta da API:', response);
            
            if (response.success) {
                preencherTabelaCTEs(response.data || response.ctes || []);
                atualizarPaginacao(response.pagination);
                atualizarContadores(response);
                
                // Debug adicional
                if (response.meta) {
                    console.log('📊 Meta informações:', response.meta);
                }
            } else {
                console.error('❌ Erro na resposta:', response.error);
                mostrarErroTabela(response.error || 'Erro desconhecido');
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro AJAX:', { xhr, status, error });
            
            let mensagemErro = 'Erro ao carregar CTEs';
            
            if (status === 'timeout') {
                mensagemErro = 'Timeout - servidor demorou para responder';
            } else if (xhr.status === 0) {
                mensagemErro = 'Erro de conexão - verifique se o servidor está rodando';
            } else if (xhr.status >= 500) {
                mensagemErro = `Erro interno do servidor (${xhr.status})`;
            } else if (xhr.status === 404) {
                mensagemErro = 'API não encontrada - verifique as rotas';
            }
            
            mostrarErroTabela(mensagemErro);
        }
    });
}

function mostrarLoadingTabela() {
    const tbody = $('#tabelaCTEs tbody');
    tbody.html(`
        <tr>
            <td colspan="7" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <div class="mt-2">Carregando dados...</div>
            </td>
        </tr>
    `);
    
    $('#totalRegistros').text('Carregando...');
}

function mostrarErroTabela(mensagem) {
    const tbody = $('#tabelaCTEs tbody');
    tbody.html(`
        <tr>
            <td colspan="7" class="text-center py-4 text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                <div><strong>Erro:</strong> ${mensagem}</div>
                <button class="btn btn-outline-primary btn-sm mt-2" onclick="carregarListaCTEs()">
                    <i class="fas fa-retry"></i> Tentar Novamente
                </button>
            </td>
        </tr>
    `);
    
    $('#totalRegistros').text('0 registros encontrados');
    $('#paginacao').hide();
}

function preencherTabelaCTEs(ctes) {
    const tbody = $('#tabelaCTEs tbody');
    
    if (!ctes || ctes.length === 0) {
        tbody.html(`
            <tr>
                <td colspan="7" class="text-center py-4 text-muted">
                    <i class="fas fa-inbox fa-2x mb-2"></i>
                    <div>Nenhum CTE encontrado</div>
                    <small>Tente ajustar os filtros de busca</small>
                </td>
            </tr>
        `);
        return;
    }
    
    console.log(`📋 Preenchendo tabela com ${ctes.length} CTEs`);
    
    let html = '';
    
    ctes.forEach(cte => {
        // Formatações
        const valor = formatarMoeda(cte.valor_total || 0);
        const dataEmissao = formatarData(cte.data_emissao);
        const statusBaixa = formatarStatusBaixa(cte);
        const statusProcesso = formatarStatusProcesso(cte);
        
        html += `
            <tr>
                <td><strong>${cte.numero_cte || 'N/A'}</strong></td>
                <td>
                    <div>${cte.destinatario_nome || 'N/A'}</div>
                    <small class="text-muted">${cte.veiculo_placa || ''}</small>
                </td>
                <td><strong>${valor}</strong></td>
                <td>${dataEmissao}</td>
                <td>${statusBaixa}</td>
                <td>${statusProcesso}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-outline-primary" 
                                onclick="editarCTE(${cte.numero_cte})" 
                                title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger" 
                                onclick="excluirCTE(${cte.numero_cte})" 
                                title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.html(html);
}

// ===================================
// FORMATAÇÃO DE DADOS
// ===================================

function formatarMoeda(valor) {
    if (!valor || valor === 0) return 'R$ 0,00';
    
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function formatarData(data) {
    if (!data) return '-';
    
    try {
        const date = new Date(data);
        return date.toLocaleDateString('pt-BR');
    } catch (e) {
        return data;
    }
}

function formatarStatusBaixa(cte) {
    if (cte.has_baixa || cte.data_baixa) {
        return '<span class="badge bg-success">Pago</span>';
    } else {
        return '<span class="badge bg-warning">Pendente</span>';
    }
}

function formatarStatusProcesso(cte) {
    if (cte.processo_completo) {
        return '<span class="badge bg-success">Completo</span>';
    } else {
        return '<span class="badge bg-warning">Em Andamento</span>';
    }
}

// ===================================
// PAGINAÇÃO
// ===================================

function atualizarPaginacao(pagination) {
    if (!pagination) {
        $('#paginacao').hide();
        return;
    }
    
    totalPaginas = pagination.pages || 1;
    const currentPage = pagination.current_page || 1;
    const hasNext = pagination.has_next || false;
    const hasPrev = pagination.has_prev || false;
    
    if (totalPaginas <= 1) {
        $('#paginacao').hide();
        return;
    }
    
    let html = '';
    
    // Botão Anterior
    html += `
        <li class="page-item ${!hasPrev ? 'disabled' : ''}">
            <button class="page-link" ${hasPrev ? `onclick="carregarListaCTEs(${currentPage - 1})"` : ''}>
                <i class="fas fa-chevron-left"></i>
            </button>
        </li>
    `;
    
    // Números das páginas
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPaginas, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <button class="page-link" onclick="carregarListaCTEs(${i})">${i}</button>
            </li>
        `;
    }
    
    // Botão Próximo
    html += `
        <li class="page-item ${!hasNext ? 'disabled' : ''}">
            <button class="page-link" ${hasNext ? `onclick="carregarListaCTEs(${currentPage + 1})"` : ''}>
                <i class="fas fa-chevron-right"></i>
            </button>
        </li>
    `;
    
    $('#paginacao ul').html(html);
    $('#paginacao').show();
}

function atualizarContadores(response) {
    const total = response.pagination?.total || response.total || 0;
    const itemsRetornados = response.meta?.items_returned || (response.data || response.ctes || []).length;
    
    $('#totalRegistros').text(`${total} registro(s) encontrado(s)`);
    
    if (itemsRetornados !== total) {
        $('#totalRegistros').append(` - Mostrando ${itemsRetornados}`);
    }
}

// ===================================
// SISTEMA CRUD
// ===================================

function configurarEventosCRUD() {
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
    
    // Busca para edição
    $('#btnBuscarCTE').on('click', buscarCTEParaEdicao);
    $('#numero_cte_busca').on('keypress', function(e) {
        if (e.which === 13) {
            buscarCTEParaEdicao();
        }
    });
    
    // Cancelar edição
    $('#btnCancelarEdicao').on('click', cancelarEdicao);
}

function inserirCTE() {
    const formData = obterDadosFormulario('#formInserirCTE');
    
    console.log('📝 Inserindo CTE:', formData);
    
    // Validações básicas
    if (!formData.numero_cte) {
        alert('❌ Número do CTE é obrigatório');
        return;
    }
    
    if (!formData.valor_total || formData.valor_total <= 0) {
        alert('❌ Valor total deve ser maior que zero');
        return;
    }
    
    $.ajax({
        url: '/ctes/api/criar',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('✅ CTE inserido:', response);
            
            if (response.success) {
                alert('✅ ' + (response.message || 'CTE inserido com sucesso'));
                $('#formInserirCTE')[0].reset();
                carregarListaCTEs();
            } else {
                alert('❌ ' + (response.message || response.error || 'Erro ao inserir'));
            }
        },
        error: function(xhr) {
            console.error('❌ Erro ao inserir CTE:', xhr);
            const response = xhr.responseJSON;
            alert('❌ ' + (response?.message || response?.error || 'Erro ao inserir CTE'));
        }
    });
}

function buscarCTEParaEdicao() {
    const numeroCte = $('#numero_cte_busca').val().trim();
    
    if (!numeroCte) {
        alert('❌ Digite o número do CTE');
        return;
    }
    
    console.log('🔍 Buscando CTE para edição:', numeroCte);
    
    $.ajax({
        url: `/ctes/api/buscar/${numeroCte}`,
        method: 'GET',
        success: function(response) {
            console.log('✅ CTE encontrado:', response);
            
            if (response.success) {
                preencherFormularioEdicao(response.cte);
                $('#areaEdicao').show();
                $('#numeroCteEdicao').text(numeroCte);
            } else {
                alert('❌ ' + (response.message || 'CTE não encontrado'));
            }
        },
        error: function(xhr) {
            console.error('❌ Erro ao buscar CTE:', xhr);
            const response = xhr.responseJSON;
            alert('❌ ' + (response?.message || 'Erro ao buscar CTE'));
        }
    });
}

function preencherFormularioEdicao(cte) {
    console.log('📝 Preenchendo formulário de edição:', cte);
    
    // Dados principais
    $('#destinatario_nome_edit').val(cte.destinatario_nome || '');
    $('#valor_total_edit').val(cte.valor_total || '');
    $('#data_emissao_edit').val(formatarDataInput(cte.data_emissao));
    $('#veiculo_placa_edit').val(cte.veiculo_placa || '');
    $('#numero_fatura_edit').val(cte.numero_fatura || '');
    $('#data_baixa_edit').val(formatarDataInput(cte.data_baixa));
    
    // Datas do processo
    $('#data_inclusao_fatura_edit').val(formatarDataInput(cte.data_inclusao_fatura));
    $('#data_envio_processo_edit').val(formatarDataInput(cte.data_envio_processo));
    $('#primeiro_envio_edit').val(formatarDataInput(cte.primeiro_envio));
    $('#data_rq_tmc_edit').val(formatarDataInput(cte.data_rq_tmc));
    $('#data_atesto_edit').val(formatarDataInput(cte.data_atesto));
    $('#envio_final_edit').val(formatarDataInput(cte.envio_final));
    
    // Observações
    $('#observacao_edit').val(cte.observacao || '');
}

function formatarDataInput(data) {
    if (!data) return '';
    
    try {
        const date = new Date(data);
        return date.toISOString().split('T')[0];
    } catch (e) {
        return '';
    }
}

function salvarEdicaoCTE() {
    const numeroCte = $('#numeroCteEdicao').text();
    const formData = obterDadosFormulario('#formEditarCTE');
    
    console.log('💾 Salvando edição do CTE:', numeroCte, formData);
    
    $.ajax({
        url: `/ctes/api/atualizar/${numeroCte}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('✅ CTE atualizado:', response);
            
            if (response.success) {
                alert('✅ ' + (response.message || 'CTE atualizado com sucesso'));
                cancelarEdicao();
                carregarListaCTEs();
            } else {
                alert('❌ ' + (response.message || 'Erro ao atualizar'));
            }
        },
        error: function(xhr) {
            console.error('❌ Erro ao atualizar CTE:', xhr);
            const response = xhr.responseJSON;
            alert('❌ ' + (response?.message || 'Erro ao atualizar CTE'));
        }
    });
}

function editarCTE(numeroCte) {
    console.log('📝 Iniciando edição do CTE:', numeroCte);
    
    $('#numero_cte_busca').val(numeroCte);
    $('#buscar-tab').click();
    
    setTimeout(() => {
        buscarCTEParaEdicao();
    }, 300);
}

function excluirCTE(numeroCte) {
    if (!confirm(`❌ Tem certeza que deseja excluir o CTE ${numeroCte}?\n\nEsta ação não pode ser desfeita.`)) {
        return;
    }
    
    console.log('🗑️ Excluindo CTE:', numeroCte);
    
    $.ajax({
        url: `/ctes/api/excluir/${numeroCte}`,
        method: 'DELETE',
        success: function(response) {
            console.log('✅ CTE excluído:', response);
            
            if (response.success) {
                alert('✅ ' + (response.message || 'CTE excluído com sucesso'));
                carregarListaCTEs();
            } else {
                alert('❌ ' + (response.message || 'Erro ao excluir'));
            }
        },
        error: function(xhr) {
            console.error('❌ Erro ao excluir CTE:', xhr);
            const response = xhr.responseJSON;
            alert('❌ ' + (response?.message || 'Erro ao excluir CTE'));
        }
    });
}

function cancelarEdicao() {
    $('#areaEdicao').hide();
    $('#numero_cte_busca').val('');
    $('#formEditarCTE')[0].reset();
}

function obterDadosFormulario(seletor) {
    const form = $(seletor);
    const formData = {};
    
    form.find('input, textarea, select').each(function() {
        const campo = $(this);
        const name = campo.attr('name');
        const value = campo.val();
        
        if (name) {
            if (value && value.trim() !== '') {
                formData[name] = value.trim();
            }
        }
    });
    
    console.log('📋 Dados do formulário coletados:', formData);
    return formData;
}

// ===================================
// SISTEMA DE EXPORT
// ===================================

function configurarEventosExport() {
    $('#btnExportExcel, [onclick="downloadExcel()"]').on('click', downloadExcel);
    $('#btnExportPDF, [onclick="downloadPDF()"]').on('click', downloadPDF);
    $('#btnExportCSV, [onclick="downloadCSV()"]').on('click', downloadCSV);
}

function downloadExcel() {
    console.log('📊 Exportando para Excel...');
    
    const params = new URLSearchParams(filtrosAtuais);
    const url = `/ctes/api/download/excel?${params.toString()}`;
    
    window.open(url, '_blank');
}

function downloadPDF() {
    console.log('📄 Exportando para PDF...');
    
    const params = new URLSearchParams(filtrosAtuais);
    const url = `/ctes/api/download/pdf?${params.toString()}`;
    
    window.open(url, '_blank');
}

function downloadCSV() {
    console.log('📋 Exportando para CSV...');
    
    const params = new URLSearchParams(filtrosAtuais);
    const url = `/ctes/api/download/csv?${params.toString()}`;
    
    window.open(url, '_blank');
}

// ===================================
// SISTEMA DE DEBUG E DIAGNÓSTICO
// ===================================

function configurarEventosDebug() {
    $('#btnDebug, [onclick="testarFiltros()"]').on('click', testarFiltros);
}

function testConexao() {
    console.log('🔍 Testando conexão da API...');
    
    $.ajax({
        url: '/ctes/api/test-conexao',
        method: 'GET',
        timeout: 10000,
        success: function(response) {
            if (response.success && response.conexao === 'OK') {
                console.log('✅ API conectada:', response);
            } else {
                console.warn('⚠️ API com problemas:', response);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro na API:', {xhr, status, error});
        }
    });
}

function testarFiltros() {
    console.log('🧪 Iniciando teste de filtros...');
    
    // Teste de conectividade
    testConexao();
    
    // Teste da API de listagem
    $.ajax({
        url: '/ctes/api/listar',
        method: 'GET',
        data: { per_page: 5 },
        success: function(response) {
            console.log('✅ Teste de listagem:', response);
            alert(`✅ API funcionando!\nTotal de CTEs: ${response.pagination?.total || 0}`);
        },
        error: function(xhr) {
            console.error('❌ Erro no teste:', xhr);
            alert('❌ Erro na API de listagem');
        }
    });
    
    // Teste específico se houver CTE na URL
    const urlParams = new URLSearchParams(window.location.search);
    const testCTE = urlParams.get('test_cte');
    
    if (testCTE) {
        console.log(`🔍 Testando CTE específico: ${testCTE}`);
        
        $.ajax({
            url: `/ctes/api/buscar/${testCTE}`,
            method: 'GET',
            success: function(response) {
                console.log(`✅ CTE ${testCTE} encontrado:`, response);
            },
            error: function(xhr) {
                console.error(`❌ Erro ao buscar CTE ${testCTE}:`, xhr);
            }
        });
    }
}

// Adicionar função de teste no ctes.js
function testarConexaoAPI() {
    console.log('🧪 Testando conectividade da API...');
    
    $.ajax({
        url: '/ctes/api/test-basic',
        method: 'GET',
        success: function(response) {
            console.log('✅ Teste básico:', response);
            if (response.success) {
                alert(`✅ Conectividade OK!\nTotal registros: ${response.total_registros}`);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro no teste básico:', error);
            alert('❌ Erro de conectividade: ' + error);
        }
    });
}


// ===================================
// FUNÇÕES AUXILIARES E UTILITÁRIOS
// ===================================

function recarregarPagina() {
    window.location.reload();
}

function irParaPagina(pagina) {
    carregarListaCTEs(pagina);
}

function buscarCTE(numeroCTE) {
    $('#filtroTexto').val(numeroCTE);
    aplicarFiltros();
}

function limparTabela() {
    $('#tabelaCTEs tbody').empty();
    $('#totalRegistros').text('');
    $('#paginacao').hide();
}

function downloadExcel() {
    console.log('Iniciando download Excel...');
    baixarArquivo('/ctes/api/download/excel', 'Excel');
}

function downloadPDF() {
    console.log('Iniciando download PDF...');
    baixarArquivo('/ctes/api/download/pdf', 'PDF');
}

function downloadCSV() {
    console.log('Iniciando download CSV...');
    baixarArquivo('/ctes/api/download/csv', 'CSV');
}

function baixarArquivo(url, tipo) {
    try {
        // Capturar filtros atuais da página
        const search = $('#searchInput').val() || '';
        const statusBaixa = $('#filtroStatusBaixa').val() || '';
        
        // Montar URL com filtros
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (statusBaixa) params.append('status_baixa', statusBaixa);
        
        const urlCompleta = params.toString() ? `${url}?${params.toString()}` : url;
        
        console.log(`Download ${tipo}:`, urlCompleta);
        
        // Mostrar loading
        mostrarToast(`Preparando download ${tipo}...`, 'info');
        
        // Criar link temporário para download
        const link = document.createElement('a');
        link.href = urlCompleta;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Feedback de sucesso
        setTimeout(() => {
            mostrarToast(`Download ${tipo} iniciado com sucesso!`, 'success');
        }, 1000);
        
    } catch (error) {
        console.error(`Erro no download ${tipo}:`, error);
        mostrarToast(`Erro no download ${tipo}`, 'error');
    }
}

function mostrarToast(mensagem, tipo = 'info') {
    const iconMap = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle', 
        'info': 'fa-info-circle',
        'warning': 'fa-exclamation-triangle'
    };
    
    const colorMap = {
        'success': 'text-success',
        'error': 'text-danger',
        'info': 'text-info', 
        'warning': 'text-warning'
    };
    
    const toast = `
        <div class="toast show position-fixed top-0 end-0 m-3" role="alert" style="z-index: 9999;">
            <div class="toast-header">
                <i class="fas ${iconMap[tipo]} ${colorMap[tipo]} me-2"></i>
                <strong class="me-auto">Sistema</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${mensagem}
            </div>
        </div>
    `;
    
    $('body').append(toast);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        $('.toast').fadeOut(() => $('.toast').remove());
    }, 5000);
}
// ===================================
// EXPOSIÇÃO GLOBAL PARA DEBUG
// ===================================

window.CTEsSystem = {
    carregarListaCTEs,
    aplicarFiltros,
    limparFiltros,
    testarFiltros,
    testConexao,
    filtrosAtuais,
    paginaAtual,
    totalPaginas
};

console.log('📋 Sistema de CTEs carregado completamente. Use CTEsSystem para debug.');