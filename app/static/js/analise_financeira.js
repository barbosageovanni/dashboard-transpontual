// Sistema de Análise Financeira - Dashboard Baker
let chartsFinanceira = {};
let analiseAtual = {};
let filtrosAtivos = {
    periodo: 180,
    cliente: null
};

// Configurações dos gráficos
const chartColorsFinanceira = {
    primary: '#28a745',
    secondary: '#20c997', 
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    gradient: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
};

$(document).ready(function() {
    console.log('🚀 Inicializando Análise Financeira...');
    inicializarAnaliseFinanceira();
});

function inicializarAnaliseFinanceira() {
    console.log('🚀 Inicializando sistema de análise financeira...');
    
    // Verificar se estamos na página correta
    if (!window.location.pathname.includes('analise-financeira')) {
        console.warn('⚠️ Não estamos na página de análise financeira');
        return;
    }
    
    // Verificar elementos essenciais da página
    if ($('#filtroPeriodo').length === 0) {
        console.warn('⚠️ Elementos da página não encontrados, tentando novamente em 1s...');
        setTimeout(inicializarAnaliseFinanceira, 1000);
        return;
    }
    
    carregarListaClientes();
    configurarEventos();
    configurarBotoesExportacao();
    
    // Delay para garantir que a página carregou completamente
    setTimeout(() => {
        console.log('📊 Carregando análise completa...');
        carregarAnaliseCompleta();
    }, 500);
    
    // Delay para carregar dados de inclusão
    setTimeout(() => {
        console.log('📊 Carregando faturamento por inclusão...');
        carregarFaturamentoInclusao();
    }, 1000);
}

function configurarEventos() {
    // Mudança nos filtros
    $('#filtroPeriodo').on('change', function() {
        filtrosAtivos.periodo = parseInt($(this).val());
        atualizarStatusFiltro();
    });
    
    $('#filtroCliente').on('change', function() {
        filtrosAtivos.cliente = $(this).val() || null;
        atualizarStatusFiltro();
    });
    
    // Filtro de inclusão de fatura
    $('#filtroInclusao').on('change', function() {
        carregarFaturamentoInclusao();
    });
}

// ============================================================================
// 🆕 FUNÇÕES DE FATURAMENTO POR INCLUSÃO DE FATURA
// ============================================================================

function carregarFaturamentoInclusao() {
    const filtro = parseInt($('#filtroInclusao').val()) || 30;
    
    mostrarLoading('Carregando faturamento por inclusão...');
    
    $.ajax({
        url: '/analise-financeira/api/faturamento-inclusao',
        method: 'GET',
        data: { filtro_dias: filtro },
        timeout: 15000,
        success: function(response) {
            if (response.success) {
                atualizarMetricasInclusao(response.dados);
                console.log('✅ Faturamento por inclusão carregado:', response.dados);
            } else {
                mostrarErro('Erro ao carregar faturamento: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro na API de faturamento por inclusão:', error);
            mostrarErro('Erro na comunicação com o servidor');
        },
        complete: function() {
            esconderLoading();
        }
    });
}

function atualizarMetricasInclusao(dados) {
    try {
        // Atualizar valores
        $('#faturamentoTotalInclusao').text(formatarMoeda(dados.faturamento_total));
        $('#quantidadeCTEsInclusao').text(dados.quantidade_ctes.toLocaleString());
        $('#ticketMedioInclusao').text(formatarMoeda(dados.ticket_medio));
        $('#statusInclusao').text('Status: ' + dados.status);
        $('#periodoInclusao').text(`Período: ${dados.data_inicio} a ${dados.data_fim}`);
        
        // Criar gráfico de evolução mensal
        if (dados.graficos && dados.graficos.faturamento_mensal) {
            criarGraficoFaturamentoInclusao(dados.graficos.faturamento_mensal);
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar métricas de inclusão:', error);
        mostrarErro('Erro ao processar dados de faturamento');
    }
}

function criarGraficoFaturamentoInclusao(dadosGrafico) {
    try {
        const ctx = document.getElementById('chartFaturamentoInclusao');
        if (!ctx) {
            console.warn('⚠️ Canvas chartFaturamentoInclusao não encontrado');
            return;
        }
        
        // Destruir gráfico anterior se existir
        if (chartsFinanceira.faturamentoInclusao) {
            chartsFinanceira.faturamentoInclusao.destroy();
        }
        
        chartsFinanceira.faturamentoInclusao = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dadosGrafico.labels || [],
                datasets: [{
                    label: 'Faturamento Mensal',
                    data: dadosGrafico.valores || [],
                    borderColor: chartColorsFinanceira.primary,
                    backgroundColor: chartColorsFinanceira.primary + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatarMoeda(value);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Faturamento: ' + formatarMoeda(context.parsed.y);
                            }
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('❌ Erro ao criar gráfico de faturamento por inclusão:', error);
    }
}

// ============================================================================
// FUNÇÕES PRINCIPAIS DE ANÁLISE
// ============================================================================

function carregarListaClientes() {
    $.ajax({
        url: '/analise-financeira/api/clientes',
        method: 'GET',
        timeout: 15000,
        success: function(response) {
            if (response.success) {
                preencherSelectClientes(response.clientes);
            } else {
                console.error('Erro ao carregar clientes:', response.error);
            }
        },
        error: function(xhr) {
            console.error('Erro AJAX clientes:', xhr);
        }
    });
}

function preencherSelectClientes(clientes) {
    const select = $('#filtroCliente');
    select.find('option:not(:first)').remove(); // Manter "Todos os Clientes"
    
    clientes.forEach(cliente => {
        select.append(`<option value="${cliente}">${cliente}</option>`);
    });
    
    console.log(`✅ ${clientes.length} clientes carregados`);
}

function aplicarFiltros() {
    console.log('📊 Aplicando filtros:', filtrosAtivos);
    carregarAnaliseCompleta();
}

function limparFiltros() {
    $('#filtroPeriodo').val('180');
    $('#filtroCliente').val('');
    filtrosAtivos = { periodo: 180, cliente: null };
    atualizarStatusFiltro();
    carregarAnaliseCompleta();
}

function atualizarStatusFiltro() {
    const cliente = filtrosAtivos.cliente ? ` | Cliente: ${filtrosAtivos.cliente}` : '';
    $('#statusFiltro').text(`Período: ${filtrosAtivos.periodo} dias${cliente}`);
}

function carregarAnaliseCompleta() {
    console.log('🚀 Iniciando carregamento da análise...', filtrosAtivos);
    mostrarLoading();
    
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo
    });
    
    if (filtrosAtivos.cliente) {
        params.append('filtro_cliente', filtrosAtivos.cliente);
    }
    
    console.log('📡 URL da requisição:', `/analise-financeira/api/analise-completa?${params.toString()}`);
    
    $.ajax({
        url: `/analise-financeira/api/analise-completa?${params.toString()}`,
        method: 'GET',
        timeout: 30000,
        beforeSend: function() {
            console.log('📤 Enviando requisição para análise completa...');
        },
        success: function(response) {
            console.log('✅ Resposta recebida:', response);
            
            if (response.success) {
                analiseAtual = response.analise;
                console.log('📊 Dados da análise:', analiseAtual);
                processarAnaliseCompleta(response.analise);
                esconderLoading();
                
                // Atualizar informações de exportação
                setTimeout(obterInfoExportacao, 1000);
            } else {
                console.error('❌ API retornou erro:', response.error);
                throw new Error(response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro na requisição AJAX:');
            console.error('Status:', status);
            console.error('Error:', error);
            console.error('Response:', xhr.responseText);
            console.error('Status Code:', xhr.status);
            
            esconderLoading();
            
            let mensagemErro = 'Erro ao carregar análise financeira';
            if (xhr.status === 0) {
                mensagemErro = 'Erro de conexão - verifique se o servidor está rodando';
            } else if (xhr.status === 404) {
                mensagemErro = 'Endpoint não encontrado';
            } else if (xhr.status >= 500) {
                mensagemErro = 'Erro interno do servidor';
            }
            
            mostrarErroAnalise(mensagemErro);
        }
    });
}

function processarAnaliseCompleta(analise) {
    // Atualizar cards de métricas
    atualizarCardsMetricas(analise);
    
    // Criar gráficos
    if (analise.graficos) {
        criarGraficosFinanceira(analise.graficos);
    }
    
    // Atualizar tabelas
    if (analise.concentracao_clientes && analise.concentracao_clientes.top_clientes) {
        atualizarTabelaTopClientes(analise.concentracao_clientes.top_clientes);
    }
    
    // Atualizar stress test
    if (analise.stress_test_receita && analise.stress_test_receita.cenarios) {
        atualizarStressTest(analise.stress_test_receita.cenarios);
    }
    
    // Atualizar status
    $('#statusFiltro').text(`✅ Análise atualizada | ${analise.resumo_filtro.total_ctes} CTEs analisados`);
}

function atualizarCardsMetricas(analise) {
    try {
        // Receita Atual e Variação
        if (analise.receita_mensal) {
            const receita = analise.receita_mensal;
            $('#receitaAtual').text(formatarMoeda(receita.receita_mes_corrente));
            
            // Variação percentual com cor
            const variacao = receita.variacao_percentual;
            const cardReceita = $('#cardReceitaAtual');
            let sinal = '';
            
            if (variacao > 0) {
                cardReceita.removeClass('variacao-negativa variacao-neutra').addClass('variacao-positiva');
                sinal = '+';
            } else if (variacao < 0) {
                cardReceita.removeClass('variacao-positiva variacao-neutra').addClass('variacao-negativa');
                sinal = '';
            } else {
                cardReceita.removeClass('variacao-positiva variacao-negativa').addClass('variacao-neutra');
                sinal = '';
            }
            
            $('#variacao').text(`📈 ${sinal}${variacao}% vs ${receita.mes_anterior_nome}`);
        }
        
        // Ticket Médio
        if (analise.ticket_medio) {
            const ticket = analise.ticket_medio;
            $('#ticketMedio').text(formatarMoeda(ticket.valor));
            $('#medianaTicket').text(`📊 Mediana: ${formatarMoeda(ticket.mediana)}`);
        }
        
        // Tempo de Cobrança
        if (analise.tempo_medio_cobranca) {
            const tempo = analise.tempo_medio_cobranca;
            $('#tempoCobranca').text(`${tempo.dias_medio} dias`);
            $('#tempoMediana').text(`📅 Mediana: ${tempo.mediana} dias`);
        }
        
        // Concentração
        if (analise.concentracao_clientes) {
            const concentracao = analise.concentracao_clientes;
            $('#concentracao').text(`${concentracao.percentual_top5}%`);
            
            const maiorCliente = concentracao.top_clientes[0];
            if (maiorCliente) {
                $('#maiorCliente').text(`👑 ${maiorCliente.nome.substring(0, 20)}... (${maiorCliente.percentual}%)`);
            }
        }
        
        // Tendência Linear
        if (analise.tendencia_linear) {
            const tendencia = analise.tendencia_linear;
            const inclinacao = tendencia.inclinacao;
            $('#tendenciaValor').text(inclinacao.toFixed(1));
            $('#rSquared').text(`📊 R²: ${tendencia.r_squared}`);
            
            // Cor da tendência
            const elemTendencia = $('#tendenciaValor');
            if (inclinacao > 0) {
                elemTendencia.removeClass('tendencia-negativa tendencia-neutra').addClass('tendencia-positiva');
            } else if (inclinacao < 0) {
                elemTendencia.removeClass('tendencia-positiva tendencia-neutra').addClass('tendencia-negativa');
            } else {
                elemTendencia.removeClass('tendencia-positiva tendencia-negativa').addClass('tendencia-neutra');
            }
            
            // Previsão
            $('#previsaoProximo').text(formatarMoeda(tendencia.previsao_proximo_mes));
            $('#mesesAnalise').text(`📅 Base: ${tendencia.meses_analisados || 0} meses`);
        }
        
        // 🆕 NOVO CARD: Receita por Inclusão Fatura
        if (analise.receita_por_inclusao_fatura) {
            atualizarCardReceitaInclusaoFatura(analise.receita_por_inclusao_fatura);
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar cards:', error);
    }
}

// ============================================================================
// FUNÇÕES DE GRÁFICOS
// ============================================================================

function criarGraficosFinanceira(dadosGraficos) {
    console.log('📈 Criando gráficos financeiros...', dadosGraficos);
    
    // Verificar se Chart.js está disponível
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js não disponível');
        mostrarErroChart('Chart.js não carregado');
        return;
    }
    
    try {
        // 1. Receita Mensal
        if (dadosGraficos.receita_mensal) {
            criarGraficoReceitaMensal(dadosGraficos.receita_mensal);
        }
        
        // 2. Concentração de Clientes
        if (dadosGraficos.concentracao_clientes) {
            criarGraficoConcentracao(dadosGraficos.concentracao_clientes);
        }
        
        // 3. Tendência Linear
        if (dadosGraficos.tendencia_linear) {
            criarGraficoTendencia(dadosGraficos.tendencia_linear);
        }
        
        // 4. Tempo de Cobrança
        if (dadosGraficos.tempo_cobranca) {
            criarGraficoTempoCobranca(dadosGraficos.tempo_cobranca);
        }
        
    } catch (error) {
        console.error('❌ Erro geral ao criar gráficos:', error);
    }
}

function criarGraficoReceitaMensal(dados) {
    const canvas = document.getElementById('chartReceitaMensal');
    if (!canvas) {
        console.warn('⚠️ Canvas chartReceitaMensal não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.receitaMensal) {
            chartsFinanceira.receitaMensal.destroy();
        }
        
        if (!dados.labels || dados.labels.length === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-muted p-4">Dados insuficientes</p>';
            return;
        }
        
        chartsFinanceira.receitaMensal = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Receita Mensal (R$)',
                    data: dados.valores,
                    borderColor: chartColorsFinanceira.primary,
                    backgroundColor: `${chartColorsFinanceira.primary}20`,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: chartColorsFinanceira.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Receita: ${formatarMoeda(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatarMoedaCompacta(value);
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico receita mensal criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico receita mensal:', error);
        canvas.parentElement.innerHTML = '<p class="text-center text-danger p-4">Erro ao criar gráfico</p>';
    }
}

function criarGraficoConcentracao(dados) {
    const canvas = document.getElementById('chartConcentracao');
    if (!canvas) {
        console.warn('⚠️ Canvas chartConcentracao não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.concentracao) {
            chartsFinanceira.concentracao.destroy();
        }
        
        if (!dados.labels || dados.labels.length === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-muted p-4">Dados insuficientes</p>';
            return;
        }
        
        chartsFinanceira.concentracao = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: dados.labels,
                datasets: [{
                    data: dados.valores,
                    backgroundColor: [
                        '#28a745', '#20c997', '#17a2b8', '#ffc107', '#fd7e14', '#6c757d'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${formatarMoeda(context.raw)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico concentração criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico concentração:', error);
        canvas.parentElement.innerHTML = '<p class="text-center text-danger p-4">Erro ao criar gráfico</p>';
    }
}

function criarGraficoTendencia(dados) {
    const canvas = document.getElementById('chartTendencia');
    if (!canvas) {
        console.warn('⚠️ Canvas chartTendencia não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.tendencia) {
            chartsFinanceira.tendencia.destroy();
        }
        
        if (!dados.labels || dados.labels.length === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-muted p-4">Dados insuficientes para tendência</p>';
            return;
        }
        
        chartsFinanceira.tendencia = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Receita Real',
                    data: dados.valores_reais,
                    borderColor: chartColorsFinanceira.primary,
                    backgroundColor: `${chartColorsFinanceira.primary}20`,
                    borderWidth: 2,
                    pointRadius: 5
                }, {
                    label: 'Linha de Tendência',
                    data: dados.valores_tendencia,
                    borderColor: chartColorsFinanceira.danger,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${formatarMoeda(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatarMoedaCompacta(value);
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico tendência criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico tendência:', error);
        canvas.parentElement.innerHTML = '<p class="text-center text-danger p-4">Erro ao criar gráfico</p>';
    }
}

function criarGraficoTempoCobranca(dados) {
    const canvas = document.getElementById('chartTempoCobranca');
    if (!canvas) {
        console.warn('⚠️ Canvas chartTempoCobranca não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.tempoCobranca) {
            chartsFinanceira.tempoCobranca.destroy();
        }
        
        if (!dados.labels || dados.labels.length === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-muted p-4">Dados insuficientes para tempo de cobrança</p>';
            return;
        }
        
        chartsFinanceira.tempoCobranca = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Quantidade de CTEs',
                    data: dados.valores,
                    backgroundColor: chartColorsFinanceira.info,
                    borderColor: chartColorsFinanceira.primary,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.y} CTEs`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico tempo cobrança criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico tempo cobrança:', error);
        canvas.parentElement.innerHTML = '<p class="text-center text-danger p-4">Erro ao criar gráfico</p>';
    }
}

// ============================================================================
// FUNÇÕES DE EXPORTAÇÃO
// ============================================================================

function configurarBotoesExportacao() {
    // Adicionar classe comum aos botões
    $('.btn-export-json, .btn-export-excel, .btn-export-csv, .btn-export-pdf, .btn-export-multiplo')
        .addClass('btn-exportacao');
    
    // Configurar eventos específicos
    $(document).on('click', '.btn-export-json', exportarJSON);
    $(document).on('click', '.btn-export-excel', exportarExcel);
    $(document).on('click', '.btn-export-pdf', exportarPDF);
    $(document).on('click', '.btn-export-multiplo', exportarMultiplo);
    
    // CSV com submenu
    $(document).on('click', '.btn-export-csv', function() {
        const submenu = $(this).next('.dropdown-menu');
        if (submenu.length) {
            submenu.toggle();
        } else {
            exportarCSV('resumo');
        }
    });
}

function exportarJSON() {
    exportarAnalise('json');
}

function exportarExcel() {
    exportarAnalise('excel');
}

function exportarCSV(aba = 'resumo') {
    if (!validarDadosParaExportacao()) {
        return;
    }
    
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo,
        aba: aba
    });
    
    if (filtrosAtivos.cliente) {
        params.append('filtro_cliente', filtrosAtivos.cliente);
    }
    
    const url = `/analise-financeira/api/exportar/csv?${params.toString()}`;
    executarDownload(url, `csv-${aba}`);
}

function exportarPDF() {
    if (!confirm('📄 Gerar relatório completo em PDF?\n\nEste processo pode demorar alguns segundos.')) {
        return;
    }
    
    exportarAnalise('pdf');
}

function exportarAnalise(formato = 'json') {
    if (!validarDadosParaExportacao()) {
        return;
    }
    
    mostrarLoadingExportacao(formato);
    
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo
    });
    
    if (filtrosAtivos.cliente) {
        params.append('filtro_cliente', filtrosAtivos.cliente);
    }
    
    let url;
    switch (formato.toLowerCase()) {
        case 'excel':
            url = `/analise-financeira/api/exportar/excel?${params.toString()}`;
            break;
        case 'csv':
            url = `/analise-financeira/api/exportar/csv?${params.toString()}`;
            break;
        case 'pdf':
            url = `/analise-financeira/api/exportar/pdf?${params.toString()}`;
            break;
        default:
            url = `/analise-financeira/api/exportar/json?${params.toString()}`;
    }
    
    executarDownload(url, formato);
}

function executarDownload(url, formato) {
    try {
        const link = document.createElement('a');
        link.href = url;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        setTimeout(() => {
            esconderLoadingExportacao();
            mostrarToast(`✅ Download ${formato.toUpperCase()} iniciado com sucesso`, 'success');
        }, 1000);
        
        console.log(`📥 Download ${formato} executado:`, url);
        
    } catch (error) {
        console.error('❌ Erro no download:', error);
        esconderLoadingExportacao();
        mostrarToast('❌ Erro ao iniciar download', 'error');
    }
}

function mostrarLoadingExportacao(formato) {
    $('.btn-exportacao').prop('disabled', true).addClass('loading');
    
    const mensagens = {
        'json': 'Gerando arquivo JSON...',
        'excel': 'Criando planilha Excel...',
        'csv': 'Preparando dados CSV...',
        'pdf': 'Gerando relatório PDF...'
    };
    
    $('#statusExportacao').text(mensagens[formato] || 'Processando exportação...').show();
}

function esconderLoadingExportacao() {
    $('.btn-exportacao').prop('disabled', false).removeClass('loading');
    $('#statusExportacao').hide();
}

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

function atualizarCardReceitaInclusaoFatura(dadosInclusao) {
    try {
        $('#receitaInclusaoFatura').text(formatarMoeda(dadosInclusao.receita_total_periodo));
        
        const variacaoInclusao = dadosInclusao.variacao_percentual;
        let sinalInclusao = '';
        const cardInclusao = $('#cardReceitaInclusaoFatura');
        
        if (variacaoInclusao > 0) {
            cardInclusao.removeClass('variacao-negativa variacao-neutra').addClass('variacao-positiva');
            sinalInclusao = '+';
        } else if (variacaoInclusao < 0) {
            cardInclusao.removeClass('variacao-positiva variacao-neutra').addClass('variacao-negativa');
            sinalInclusao = '';
        } else {
            cardInclusao.removeClass('variacao-positiva variacao-negativa').addClass('variacao-neutra');
            sinalInclusao = '';
        }
        
        $('#variacaoInclusao').text(`📈 ${sinalInclusao}${variacaoInclusao}% vs mês anterior`);
        
        const cobertura = dadosInclusao.percentual_cobertura;
        let iconeCobertura = '';
        
        if (cobertura >= 80) {
            iconeCobertura = '🟢';
        } else if (cobertura >= 60) {
            iconeCobertura = '🟡';
        } else {
            iconeCobertura = '🔴';
        }
        
        $('#coberturaInclusao').text(`${iconeCobertura} Cobertura: ${cobertura}% (${dadosInclusao.total_ctes_com_inclusao} CTEs)`);
        
    } catch (error) {
        console.error('❌ Erro ao atualizar card de inclusão fatura:', error);
        $('#receitaInclusaoFatura').text('R$ 0,00');
        $('#variacaoInclusao').text('📊 Dados indisponíveis');
        $('#coberturaInclusao').text('⚠️ Erro no cálculo');
    }
}

function atualizarTabelaTopClientes(topClientes) {
    const tbody = $('#tabelaTopClientes tbody');
    tbody.empty();
    
    if (!topClientes || topClientes.length === 0) {
        tbody.append('<tr><td colspan="5" class="text-center text-muted">Nenhum cliente encontrado</td></tr>');
        return;
    }
    
    topClientes.forEach(cliente => {
        let classeConcentracao = '';
        if (cliente.percentual >= 30) {
            classeConcentracao = 'concentracao-alta';
        } else if (cliente.percentual >= 15) {
            classeConcentracao = 'concentracao-media';
        } else {
            classeConcentracao = 'concentracao-baixa';
        }
        
        const impacto = cliente.percentual >= 20 ? 'Alto Risco' : 
                       cliente.percentual >= 10 ? 'Médio Risco' : 'Baixo Risco';
        
        tbody.append(`
            <tr>
                <td><strong>#${cliente.posicao}</strong></td>
                <td>${cliente.nome}</td>
                <td><strong>${formatarMoeda(cliente.receita)}</strong></td>
                <td><span class="${classeConcentracao}">${cliente.percentual}%</span></td>
                <td>${impacto}</td>
            </tr>
        `);
    });
}

function atualizarStressTest(cenarios) {
    const container = $('#stressTestContainer');
    
    if (!cenarios || cenarios.length === 0) {
        container.html('<p class="text-center text-muted">Dados insuficientes para stress test</p>');
        return;
    }
    
    let html = '<div class="row">';
    
    cenarios.forEach(cenario => {
        let classeRisco = '';
        if (cenario.percentual_impacto >= 50) {
            classeRisco = 'border-danger';
        } else if (cenario.percentual_impacto >= 30) {
            classeRisco = 'border-warning';
        } else {
            classeRisco = 'border-success';
        }
        
        html += `
            <div class="col-md-4">
                <div class="stress-card ${classeRisco}">
                    <h6><strong>${cenario.cenario}</strong></h6>
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Perda:</small><br>
                            <strong class="text-danger">${formatarMoeda(cenario.receita_perdida)}</strong>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Impacto:</small><br>
                            <strong class="text-danger">${cenario.percentual_impacto}%</strong>
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">Receita Restante:</small><br>
                        <strong class="text-success">${formatarMoeda(cenario.receita_restante)}</strong>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.html(html);
}

function mostrarLoading(mensagem = 'Carregando...') {
    $('#loadingGlobal').show();
    $('#metricas-principais').hide();
    if (mensagem) {
        $('#loadingGlobal .loading-text').text(mensagem);
    }
}

function esconderLoading() {
    $('#loadingGlobal').hide();
    $('#metricas-principais').show();
}

function mostrarErroAnalise(mensagem) {
    const html = `
        <div class="alert alert-danger text-center p-4">
            <h5><i class="fas fa-exclamation-triangle"></i> Erro na Análise</h5>
            <p>${mensagem}</p>
            <button class="btn btn-primary" onclick="carregarAnaliseCompleta()">
                <i class="fas fa-redo"></i> Tentar Novamente
            </button>
        </div>
    `;
    
    $('#metricas-principais').html(html);
}

function mostrarErroChart(mensagem) {
    $('.chart-container-financeira').each(function() {
        $(this).html(`
            <div class="text-center p-4">
                <h5 class="text-danger">⚠️ ${mensagem}</h5>
                <button class="btn btn-primary" onclick="location.reload()">
                    🔄 Recarregar Página
                </button>
            </div>
        `);
    });
}

function mostrarErro(mensagem) {
    console.error('❌', mensagem);
    mostrarToast(mensagem, 'error');
}

function mostrarToast(mensagem, tipo = 'info') {
    const cores = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning text-dark',
        'info': 'bg-info'
    };
    
    const icones = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': '💡'
    };
    
    const toast = $(`
        <div class="toast align-items-center text-white ${cores[tipo]} border-0" role="alert" style="z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    ${icones[tipo]} ${mensagem}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    if (!$('#toastContainer').length) {
        $('body').append('<div id="toastContainer" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    $('#toastContainer').append(toast);
    
    const bsToast = new bootstrap.Toast(toast[0], { delay: 5000 });
    bsToast.show();
    
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function validarDadosParaExportacao() {
    if (!analiseAtual) {
        mostrarToast('❌ Nenhuma análise disponível', 'error');
        return false;
    }
    
    if (Object.keys(analiseAtual).length === 0) {
        mostrarToast('❌ Dados de análise vazios', 'error');
        return false;
    }
    
    return true;
}

function obterInfoExportacao() {
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo
    });
    
    if (filtrosAtivos.cliente) {
        params.append('filtro_cliente', filtrosAtivos.cliente);
    }
    
    $.ajax({
        url: `/analise-financeira/api/exportar/info?${params.toString()}`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                mostrarInfoExportacao(response.info);
            }
        },
        error: function() {
            console.log('Não foi possível obter informações de exportação');
        }
    });
}

function mostrarInfoExportacao(info) {
    const infoHtml = `
        <div class="alert alert-info">
            <h6>📊 Informações da Exportação</h6>
            <div class="row">
                <div class="col-md-6">
                    <strong>Formatos disponíveis:</strong><br>
                    ${info.formatos_disponiveis.join(', ').toUpperCase()}
                </div>
                <div class="col-md-6">
                    <strong>Dados a exportar:</strong><br>
                    ${info.resumo_dados.total_ctes} CTEs (${info.resumo_dados.periodo_dias} dias)
                </div>
            </div>
        </div>
    `;
    
    if ($('#infoExportacao').length) {
        $('#infoExportacao').html(infoHtml);
    }
}

// Funções utilitárias
function formatarMoeda(valor) {
    if (typeof valor !== 'number' || isNaN(valor)) valor = 0;
    return 'R$ ' + valor.toLocaleString('pt-BR', {minimumFractionDigits: 2});
}

function formatarMoedaCompacta(valor) {
    if (typeof valor !== 'number' || isNaN(valor)) valor = 0;
    
    if (valor >= 1000000) {
        return 'R$ ' + (valor / 1000000).toFixed(1) + 'M';
    } else if (valor >= 1000) {
        return 'R$ ' + (valor / 1000).toFixed(1) + 'K';
    } else {
        return 'R$ ' + valor.toFixed(0);
    }
}

function formatarNumero(valor) {
    if (typeof valor !== 'number' || isNaN(valor)) valor = 0;
    return valor.toLocaleString('pt-BR');
}

// ============================================================================
// FUNÇÃO DE DEBUG
// ============================================================================

function testarAPI() {
    $('#resultadoTeste').html('<p>📄 Testando API...</p>');
    
    $.ajax({
        url: '/analise-financeira/api/analise-completa?filtro_dias=180',
        method: 'GET',
        timeout: 10000,
        success: function(response) {
            console.log('✅ Teste API bem-sucedido:', response);
            if (response.success) {
                $('#resultadoTeste').html(`
                    <div class="alert alert-success">
                        ✅ <strong>API funcionando!</strong><br>
                        📊 CTEs: ${response.analise.resumo_filtro.total_ctes}<br>
                        💰 Receita: R$ ${response.analise.receita_mensal.receita_mes_corrente.toFixed(2)}<br>
                        📅 Período: ${response.analise.resumo_filtro.periodo_dias} dias
                    </div>
                `);
                
                // Se funcionou, tentar atualizar a tela
                console.log('📊 Tentando atualizar interface...');
                processarAnaliseCompleta(response.analise);
            } else {
                $('#resultadoTeste').html(`
                    <div class="alert alert-warning">
                        ⚠️ API retornou erro: ${response.error}
                    </div>
                `);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro na análise:', xhr);
            $('#resultadoTeste').html(`
                <div class="alert alert-danger">
                    ❌ <strong>Erro na análise:</strong><br>
                    Status: ${xhr.status}<br>
                    Tipo: ${status}<br>
                    Erro: ${error}
                </div>
            `);
        }
    });
}

// ============================================================================
// EVENTOS E INICIALIZAÇÃO FINAL
// ============================================================================

// Auto-refresh a cada 10 minutos
setInterval(function() {
    if (document.visibilityState === 'visible') {
        console.log('🔄 Auto-refresh análise financeira');
        carregarAnaliseCompleta();
    }
}, 600000); // 10 minutos

// Exportação múltipla (placeholder para futuro)
function exportarMultiplo() {
    mostrarToast('🚧 Exportação múltipla em desenvolvimento', 'info');
}