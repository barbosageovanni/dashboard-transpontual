// ============================================================================
// ANÁLISE FINANCEIRA - VERSÃO CORRIGIDA COMPLETA
// JavaScript totalmente funcional com todas as APIs
// ============================================================================

let chartsFinanceira = {};
let analiseAtual = {};
let filtrosAtivos = {
    periodo: 180,
    cliente: null,
    dataInicio: null,
    dataFim: null
};

const chartColorsFinanceira = {
    primary: '#28a745',
    secondary: '#20c997',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    receita_faturada: '#6f42c1',
    receita_faturas: '#fd7e14',
    receita_media: '#e83e8c'
};

// ============================================================================
// INICIALIZAÇÃO COMPLETA
// ============================================================================

function inicializarDashboardCompleto() {
    console.log('🚀 Inicializando Dashboard Financeiro Completo...');
    
    if (!window.location.pathname.includes('analise-financeira')) {
        console.warn('Não estamos na página de análise financeira');
        return;
    }
    
    // Aguardar elementos DOM
    if ($('#filtroPeriodo').length === 0) {
        console.log('⏳ Aguardando elementos DOM...');
        setTimeout(inicializarDashboardCompleto, 1000);
        return;
    }
    
    configurarEventos();
    carregarListaClientes();
    
    // Carregar todas as métricas em sequência
    setTimeout(() => {
        console.log('📊 Iniciando carregamento das métricas...');
        carregarTodasAsMetricas();
    }, 1000);
}

// ===================================================================
// INICIALIZAÇÃO SEGURA - SUBSTITUIR na função inicializarAnaliseFinanceira
// ===================================================================

// Na função inicializarAnaliseFinanceira(), SUBSTITUIR o início por:
function inicializarAnaliseFinanceiraSegura() {
    console.log('🚀 Inicializando análise financeira (versão segura)...');
    
    // Resetar flags de controle
    window.eventosConfigurados = false;
    window.carregandoFiltros = false;
    window.limpandoFiltros = false;
    
    // Verificar se estamos na página correta
    if (!window.location.pathname.includes('analise-financeira')) {
        console.warn('⚠️ Não estamos na página de análise financeira');
        return;
    }
    
    // Garantir que elementos existem
    if ($('#filtroPeriodo').length === 0) {
        console.warn('⚠️ Elementos não encontrados, tentando novamente...');
        setTimeout(inicializarAnaliseFinanceiraSegura, 1000);
        return;
    }
    
    // Inicializar filtros de forma segura
    filtrosAtivos = {
        periodo: 180,
        cliente: null,
        dataInicio: null,
        dataFim: null
    };
    
    // Configurar eventos seguros
    setTimeout(() => {
        configurarEventos();
        carregarListaClientes();
        configurarBotoesExportacao();
        
        // Carregar dados após tudo configurado
        setTimeout(() => {
            aplicarFiltrosSemLoop();
        }, 500);
        
    }, 200);
}

console.log('✅ Código seguro carregado - sem loops!');

// LOCALIZAR e SUBSTITUIR a função configurarEventos() por esta versão:

function configurarEventos() {
    console.log('⚙️ Configurando eventos dos filtros (versão segura)...');
    
    // Remover eventos existentes para evitar duplicação
    $('#filtroPeriodo, #filtroCliente, #dataInicio, #dataFim, #btnAplicarFiltros').off();
    
    // Mudança nos filtros - SEM aplicar automaticamente
    $('#filtroPeriodo').on('change', function() {
        filtrosAtivos.periodo = parseInt($(this).val());
        console.log('📅 Período alterado:', filtrosAtivos.periodo);
        atualizarStatusFiltro();
        // Não chama carregarAnaliseCompleta() automaticamente
    });
    
    $('#filtroCliente').on('change', function() {
        filtrosAtivos.cliente = $(this).val() || null;
        console.log('👥 Cliente alterado:', filtrosAtivos.cliente);
        atualizarStatusFiltro();
        // Não chama carregarAnaliseCompleta() automaticamente
    });
    
    // NOVOS: Filtros de data - SEM aplicar automaticamente
    $('#dataInicio').on('change', function() {
        filtrosAtivos.dataInicio = $(this).val();
        console.log('📅 Data início:', filtrosAtivos.dataInicio);
        atualizarStatusFiltro();
        // Não aplica filtros automaticamente
    });

    $('#dataFim').on('change', function() {
        filtrosAtivos.dataFim = $(this).val();
        console.log('📅 Data fim:', filtrosAtivos.dataFim);
        atualizarStatusFiltro();
        // Não aplica filtros automaticamente
    });

    // BOTÃO APLICAR FILTROS - único que carrega dados
    $('#btnAplicarFiltros').on('click', function() {
        console.log('🔄 Aplicando filtros manualmente:', filtrosAtivos);
        
        // Evitar cliques múltiplos
        if ($(this).prop('disabled')) {
            console.log('⚠️ Botão já processando...');
            return;
        }
        
        // Desabilitar botão temporariamente
        $(this).prop('disabled', true).text('Aplicando...');
        
        // Chamar função existente
        carregarAnaliseCompleta();
        
        // Reabilitar botão após delay
        setTimeout(() => {
            $(this).prop('disabled', false).text('Aplicar Filtros');
        }, 2000);
    });
    
    // Filtro de inclusão (se existir)
    $('#filtroInclusao').on('change', function() {
        carregarFaturamentoInclusao();
    });
    
    console.log('✅ Eventos configurados com segurança');
}

// ===================================================================
// FUNÇÕES SEGURAS ANTI-LOOP
// ===================================================================

function aplicarFiltrosSemLoop() {
    // Evitar chamadas múltiplas
    if (window.carregandoFiltros) {
        console.log('⚠️ Já aplicando filtros - ignorando');
        return;
    }
    
    window.carregandoFiltros = true;
    console.log('🔄 Iniciando aplicação de filtros...');
    
    // Delay para evitar conflitos
    setTimeout(() => {
        try {
            carregarAnaliseCompleta();
        } catch (error) {
            console.error('❌ Erro ao aplicar filtros:', error);
        } finally {
            // Sempre liberar o flag
            setTimeout(() => {
                window.carregandoFiltros = false;
            }, 1000);
        }
    }, 100);
}

function limparFiltrosSemLoop() {
    console.log('🧹 Limpando filtros...');
    
    // Evitar loops durante a limpeza
    window.limpandoFiltros = true;
    
    // Limpar interface sem disparar eventos
    $('#filtroPeriodo').val('180');
    $('#filtroCliente').val('');  
    $('#dataInicio').val('');
    $('#dataFim').val('');
    
    // Resetar variável
    filtrosAtivos = {
        periodo: 180,
        cliente: null,
        dataInicio: null,
        dataFim: null
    };
    
    atualizarStatusFiltro();
    
    // Aplicar após limpar
    setTimeout(() => {
        window.limpandoFiltros = false;
        aplicarFiltrosSemLoop();
    }, 200);
}


function atualizarStatusFiltro() {
    let status = `Período: ${filtrosAtivos.periodo} dias`;
    
    if (filtrosAtivos.cliente) {
        status += ` | Cliente: ${filtrosAtivos.cliente}`;
    }
    
    if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
        status += ` | ${filtrosAtivos.dataInicio} a ${filtrosAtivos.dataFim}`;
    }
    
    $('#statusFiltro').text(status);
    
    // Atualizar badge de filtros ativos
    const filtrosAtivosCount = [
        filtrosAtivos.cliente,
        filtrosAtivos.dataInicio && filtrosAtivos.dataFim,
        filtrosAtivos.periodo !== 180
    ].filter(Boolean).length;
    
    if (filtrosAtivosCount > 0) {
        $('#badgeFiltros').text(filtrosAtivosCount).show();
    } else {
        $('#badgeFiltros').hide();
    }
}

// ============================================================================
// CARREGAMENTO DE TODAS AS MÉTRICAS
// ============================================================================

function carregarTodasAsMetricas() {
    console.log('📈 Carregando todas as métricas...');
    
    const promises = [
        carregarMetricasPrincipais(),
        carregarReceitaFaturada(),
        carregarReceitaComFaturas(),
        carregarReceitaMediaMensal(),
        carregarEvolucaoReceitaInclusaoFatura(),
        carregarTopClientes(),
        carregarStressTest(),
        carregarGraficos()
    ];
    
    Promise.allSettled(promises).then(results => {
        console.log('📊 Resultado do carregamento das métricas:');
        results.forEach((result, index) => {
            const nomes = [
                'Métricas Principais',
                'Receita Faturada', 
                'Receita c/ Faturas',
                'Receita Média Mensal',
                'Evolução Receita Inclusão Fatura',
                'Top Clientes',
                'Stress Test',
                'Gráficos'
            ];
            console.log(`  ${nomes[index]}: ${result.status}`);
            if (result.status === 'rejected') {
                console.error(`    Erro: ${result.reason}`);
            }
        });
        
        esconderLoading();
        atualizarUltimaAtualizacao();
        
        console.log('✅ Carregamento das métricas finalizado');
    });
}

function carregarTopClientes() {
    return new Promise((resolve, reject) => {
        console.log('👥 Carregando top clientes...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/top-clientes',
            method: 'GET',
            data: params,
            timeout: 15000,
            success: function(response) {
                if (response.success && response.top_clientes) {
                    atualizarTabelaTopClientes(response.top_clientes);
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro no top clientes:', error);
                mostrarTabelaTopClientesErro();
                reject(error);
            }
        });
    });
}

function carregarStressTest() {
    return new Promise((resolve, reject) => {
        console.log('⚠️ Carregando stress test...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/stress-test',
            method: 'GET',
            data: params,
            timeout: 15000,
            success: function(response) {
                if (response.success && response.cenarios) {
                    atualizarStressTest(response.cenarios, response.receita_total);
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro no stress test:', error);
                mostrarStressTestErro();
                reject(error);
            }
        });
    });
}

function carregarGraficos() {
    return new Promise((resolve, reject) => {
        console.log('📊 Carregando dados dos gráficos...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/graficos-dados',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                if (response.success && response.graficos) {
                    criarTodosGraficos(response.graficos);
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro nos gráficos:', error);
                mostrarErroTodosGraficos();
                reject(error);
            }
        });
    });
}

function atualizarTabelaTopClientes(topClientes) {
    console.log('👥 Atualizando tabela top clientes...');
    
    const tbody = $('#tabelaTopClientes tbody');
    tbody.empty();
    
    if (!Array.isArray(topClientes) || topClientes.length === 0) {
        tbody.append('<tr><td colspan="5" class="text-center text-muted">Nenhum cliente encontrado</td></tr>');
        return;
    }
    
    topClientes.forEach((cliente, index) => {
        if (!cliente) return;
        
        const percentual = parseFloat(cliente.percentual || 0);
        let classeRisco = 'text-success';
        let nivelRisco = cliente.risco || 'Baixo Risco';
        
        if (cliente.classe_risco === 'danger') {
            classeRisco = 'text-danger';
        } else if (cliente.classe_risco === 'warning') {
            classeRisco = 'text-warning';
        }
        
        tbody.append(`
            <tr>
                <td><strong>#${cliente.posicao || (index + 1)}</strong></td>
                <td title="${cliente.nome}">${cliente.nome.length > 30 ? cliente.nome.substring(0, 30) + '...' : cliente.nome}</td>
                <td><strong>${formatarMoeda(cliente.receita || 0)}</strong></td>
                <td class="d-none d-sm-table-cell"><span class="${classeRisco}">${percentual.toFixed(1)}%</span></td>
                <td><span class="${classeRisco}">${nivelRisco}</span></td>
            </tr>
        `);
    });
    
    console.log('✅ Tabela top clientes atualizada');
}

function mostrarTabelaTopClientesErro() {
    const tbody = $('#tabelaTopClientes tbody');
    tbody.empty();
    tbody.append('<tr><td colspan="5" class="text-center text-muted">Erro ao carregar clientes</td></tr>');
}

function atualizarStressTest(cenarios, receitaTotal) {
    console.log('⚠️ Atualizando stress test...');
    
    const container = $('#stressTestContainer');
    if (!container.length) return;
    
    if (!cenarios || cenarios.length === 0) {
        container.html('<p class="text-center text-muted">Dados insuficientes para stress test</p>');
        return;
    }
    
    let html = '';
    
    cenarios.forEach((cenario, index) => {
        if (!cenario) return;
        
        const nome = cenario.cenario || `Cenário ${index + 1}`;
        const impacto = parseFloat(cenario.percentual_impacto || 0);
        const receitaPerdida = parseFloat(cenario.receita_perdida || 0);
        const receitaRestante = parseFloat(cenario.receita_restante || 0);
        const icone = cenario.icon || '⚠️';
        
        let classeRisco = 'text-success';
        
        if (impacto >= 50) {
            classeRisco = 'text-danger';
        } else if (impacto >= 30) {
            classeRisco = 'text-warning';
        }
        
        html += `
            <div class="mb-3 p-3 border rounded">
                <h6 class="mb-2">${icone} <strong>${nome}</strong></h6>
                <div class="row">
                    <div class="col-6">
                        <small class="text-muted">Perda:</small><br>
                        <strong class="text-danger">${formatarMoeda(receitaPerdida)}</strong>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">Impacto:</small><br>
                        <strong class="${classeRisco}">${impacto.toFixed(1)}%</strong>
                    </div>
                </div>
                <hr class="my-2">
                <small class="text-muted">Restante:</small><br>
                <strong class="text-success">${formatarMoeda(receitaRestante)}</strong>
            </div>
        `;
    });
    
    container.html(html);
    
    // Atualizar impacto do top cliente no painel de status
    if (cenarios.length > 0) {
        const impactoTopCliente = cenarios[0].percentual_impacto || 0;
        $('#impactoTopCliente').text(`${impactoTopCliente.toFixed(1)}%`);
        atualizarStatusCard('#impactoTopCliente', impactoTopCliente, 'impacto');
    }
    
    console.log('✅ Stress test atualizado');
}

function mostrarStressTestErro() {
    const container = $('#stressTestContainer');
    if (container.length) {
        container.html('<p class="text-center text-muted">Erro ao carregar stress test</p>');
    }
}

function criarTodosGraficos(dadosGraficos) {
    console.log('📊 Criando todos os gráficos...');
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js não disponível');
        return;
    }
    
    try {
        // 1. Receita Mensal
        if (dadosGraficos.receita_mensal) {
            criarGraficoReceitaMensal(dadosGraficos.receita_mensal);
        }
        
        // 2. Concentração
        if (dadosGraficos.concentracao_clientes) {
            criarGraficoConcentracao(dadosGraficos.concentracao_clientes);
        }
        
        // 3. Tendência
        if (dadosGraficos.tendencia_linear) {
            criarGraficoTendencia(dadosGraficos.tendencia_linear);
        }
        
        // 4. Tempo Cobrança
        if (dadosGraficos.tempo_cobranca) {
            criarGraficoTempoCobranca(dadosGraficos.tempo_cobranca);
        }
        
        console.log('✅ Todos os gráficos processados');
        
    } catch (error) {
        console.error('❌ Erro ao criar gráficos:', error);
        mostrarErroTodosGraficos();
    }
}

function criarGraficoReceitaMensal(dados) {
    const canvas = document.getElementById('chartReceitaMensal');
    if (!canvas) {
        console.warn('Canvas chartReceitaMensal não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.receitaMensal) {
            chartsFinanceira.receitaMensal.destroy();
        }
        
        if (!dados.labels || dados.labels.length === 0) {
            mostrarMensagemGrafico('chartReceitaMensal', 'Dados insuficientes para receita mensal');
            return;
        }
        
        chartsFinanceira.receitaMensal = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Receita Mensal (R$)',
                    data: dados.valores,
                    backgroundColor: chartColorsFinanceira.primary,
                    borderColor: chartColorsFinanceira.primary,
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const qtd = dados.quantidades && dados.quantidades[context.dataIndex] ? dados.quantidades[context.dataIndex] : '';
                                return `Receita: ${formatarMoeda(context.parsed.y)}${qtd ? ` (${qtd} CTEs)` : ''}`;
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
        mostrarMensagemGrafico('chartReceitaMensal', 'Erro ao criar gráfico');
    }
}

function criarGraficoConcentracao(dados) {
    const canvas = document.getElementById('chartConcentracao');
    if (!canvas) {
        console.warn('Canvas chartConcentracao não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.concentracao) {
            chartsFinanceira.concentracao.destroy();
        }
        
        if (!dados || !dados.labels || dados.labels.length === 0) {
            mostrarMensagemGrafico('chartConcentracao', 'Dados insuficientes para concentração');
            return;
        }
        
        chartsFinanceira.concentracao = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: dados.labels.map(label => label.length > 20 ? label.substring(0, 20) + '...' : label),
                datasets: [{
                    data: dados.valores,
                    backgroundColor: [
                        '#28a745', '#20c997', '#17a2b8', 
                        '#ffc107', '#fd7e14', '#6c757d'
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
                        labels: { boxWidth: 12, padding: 15, font: { size: 11 } }
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
        mostrarMensagemGrafico('chartConcentracao', 'Erro ao criar gráfico');
    }
}

function criarGraficoTendencia(dados) {
    const canvas = document.getElementById('chartTendencia');
    if (!canvas) {
        console.warn('Canvas chartTendencia não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.tendencia) {
            chartsFinanceira.tendencia.destroy();
        }
        
        if (!dados || !dados.labels || dados.labels.length === 0) {
            mostrarMensagemGrafico('chartTendencia', 'Dados insuficientes para tendência');
            return;
        }
        
        const datasets = [];
        
        if (dados.valores_reais && dados.valores_reais.length > 0) {
            datasets.push({
                label: 'Receita Real',
                data: dados.valores_reais,
                borderColor: chartColorsFinanceira.primary,
                backgroundColor: chartColorsFinanceira.primary + '20',
                borderWidth: 3,
                pointRadius: 6,
                fill: false
            });
        }
        
        if (dados.valores_tendencia && dados.valores_tendencia.length > 0 && dados.valores_tendencia.length === dados.valores_reais.length) {
            datasets.push({
                label: 'Linha de Tendência',
                data: dados.valores_tendencia,
                borderColor: chartColorsFinanceira.danger,
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            });
        }
        
        if (datasets.length === 0) {
            mostrarMensagemGrafico('chartTendencia', 'Dados de tendência indisponíveis');
            return;
        }
        
        chartsFinanceira.tendencia = new Chart(canvas, {
            type: 'line',
            data: { labels: dados.labels, datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
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
        mostrarMensagemGrafico('chartTendencia', 'Erro ao criar gráfico');
    }
}

function criarGraficoTempoCobranca(dados) {
    const canvas = document.getElementById('chartTempoCobranca');
    if (!canvas) {
        console.warn('Canvas chartTempoCobranca não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.tempoCobranca) {
            chartsFinanceira.tempoCobranca.destroy();
        }
        
        if (!dados || !dados.labels || dados.labels.length === 0) {
            mostrarMensagemGrafico('chartTempoCobranca', 'Dados insuficientes para tempo de cobrança');
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
                    borderColor: chartColorsFinanceira.info,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.y} CTEs em ${context.label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico tempo cobrança criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico tempo cobrança:', error);
        mostrarMensagemGrafico('chartTempoCobranca', 'Erro ao criar gráfico');
    }
}

function mostrarErroTodosGraficos() {
    const graficos = ['chartReceitaMensal', 'chartConcentracao', 'chartTendencia', 'chartTempoCobranca'];
    
    graficos.forEach(grafico => {
        mostrarMensagemGrafico(grafico, 'Erro ao carregar dados do gráfico');
    });
}

function processarMetricasPrincipais(response) {
    console.log('📊 Processando métricas principais...');
    
    try {
        const basicas = response.metricas_basicas || {};
        const faturada = response.receita_faturada || {};
        const comFaturas = response.receita_com_faturas || {};
        
        // Atualizar cards principais
        $('#receitaMesAtual').text(formatarMoeda(basicas.receita_mes_atual || 0));
        $('#totalCtes').text((basicas.total_ctes || 0).toLocaleString('pt-BR'));
        $('#ticketMedio').text(formatarMoeda(basicas.ticket_medio || 0));
        
        // Percentual baixado
        const percentualBaixado = basicas.percentual_baixado || 0;
        $('#percentualBedado').text(`${percentualBaixado.toFixed(1)}%`);
        
        // ATUALIZAR PAINEL DE STATUS
        $('#totalRegistros').text((basicas.total_ctes || 0).toLocaleString('pt-BR'));
        
        const taxaFaturamento = faturada.percentual_total || 0;
        $('#taxaFaturamento').text(`${taxaFaturamento.toFixed(1)}%`);
        atualizarStatusCard('#taxaFaturamento', taxaFaturamento, 'faturamento');
        
        const taxaComFaturas = comFaturas.percentual_cobertura || 0;
        $('#taxaComFaturas').text(`${taxaComFaturas.toFixed(1)}%`);
        atualizarStatusCard('#taxaComFaturas', taxaComFaturas, 'cobertura');
        
        // Status cards com cores
        atualizarStatusCard('#percentualMedado', percentualBaixado, 'baixas');
        
        // Atualizar período de referência
        $('#periodoReferencia').text(response.periodo || 'N/A');
        $('#mesReferencia').text(response.mes_referencia || 'N/A');
        
        console.log('✅ Métricas principais processadas');
        
    } catch (error) {
        console.error('❌ Erro ao processar métricas principais:', error);
        mostrarErroCard('metricas-principais', 'Erro ao processar dados');
    }
}

function atualizarStatusCard(selector, valor, tipo) {
    const elemento = $(selector);
    if (!elemento.length) return;
    
    elemento.removeClass('text-success text-warning text-danger text-muted');
    
    let classe = 'text-muted';
    
    switch (tipo) {
        case 'baixas':
            if (valor >= 80) classe = 'text-success';
            else if (valor >= 60) classe = 'text-warning';
            else classe = 'text-danger';
            break;
            
        case 'faturamento':
            if (valor >= 90) classe = 'text-success';
            else if (valor >= 70) classe = 'text-warning';
            else classe = 'text-danger';
            break;
            
        case 'cobertura':
            if (valor >= 80) classe = 'text-success';
            else if (valor >= 60) classe = 'text-warning';
            else classe = 'text-danger';
            break;
            
        case 'impacto':
            if (valor >= 50) classe = 'text-danger';
            else if (valor >= 30) classe = 'text-warning';
            else classe = 'text-success';
            break;
    }
    
    elemento.addClass(classe);
}

function carregarMetricasPrincipais() {
    return new Promise((resolve, reject) => {
        console.log('📊 Carregando métricas principais...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/metricas-mes-corrente',
            method: 'GET',
            data: params,
            timeout: 30000,
            success: function(response) {
                if (response && response.success) {
                    processarMetricasPrincipais(response);
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Erro na API');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro nas métricas principais:', error);
                mostrarErroCard('metricas-principais', 'Erro ao carregar métricas principais');
                reject(error);
            }
        });
    });
}

function processarMetricasPrincipais(response) {
    console.log('📊 Processando métricas principais...');
    
    try {
        const basicas = response.metricas_basicas || {};
        const faturada = response.receita_faturada || {};
        const comFaturas = response.receita_com_faturas || {};
        
        // Atualizar cards principais
        $('#receitaMesAtual').text(formatarMoeda(basicas.receita_mes_atual || 0));
        $('#totalCtes').text((basicas.total_ctes || 0).toLocaleString('pt-BR'));
        $('#ticketMedio').text(formatarMoeda(basicas.ticket_medio || 0));
        
        // Percentual baixado
        const percentualBaixado = basicas.percentual_baixado || 0;
        $('#percentualBedado').text(`${percentualBaixado.toFixed(1)}%`);
        
        // Status cards com cores
        atualizarStatusCard('#statusConclusao', percentualBaixado, 'baixas');
        
        // Atualizar período de referência
        $('#periodoReferencia').text(response.periodo || 'N/A');
        $('#mesReferencia').text(response.mes_referencia || 'N/A');
        
        console.log('✅ Métricas principais processadas');
        
    } catch (error) {
        console.error('❌ Erro ao processar métricas principais:', error);
        mostrarErroCard('metricas-principais', 'Erro ao processar dados');
    }
}

function carregarReceitaFaturada() {
    return new Promise((resolve, reject) => {
        console.log('💰 Carregando receita faturada...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/receita-faturada',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                if (response.success && response.dados) {
                    atualizarCardReceitaFaturada(response.dados);
                    
                    // Criar gráfico de evolução se disponível
                    if (response.dados.evolucao_mensal) {
                        criarGraficoEvolucaoReceitaFaturada(response.dados.evolucao_mensal);
                    }
                    
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro na receita faturada:', error);
                mostrarReceitaFaturadaErro();
                reject(error);
            }
        });
    });
}

function atualizarCardReceitaFaturada(dados) {
    try {
        console.log('💰 Atualizando card receita faturada...');
        
        $('#receitaFaturada').text(formatarMoeda(dados.receita_total || 0));
        $('#qtdCtesFaturados').text(`${dados.quantidade_ctes || 0} CTEs`);
        $('#percentualFaturado').text(`${(dados.percentual_total || 0).toFixed(1)}% do total`);
        
        // Status com cor
        const percentual = dados.percentual_total || 0;
        atualizarStatusCard('#statusFaturamento', percentual, 'faturamento');
        
        // Campo usado (para debug)
        if (dados.campo_usado && dados.campo_usado.includes('fallback')) {
            $('#avisoFallbackFaturada').show().text(`Usando: ${dados.campo_usado}`);
        } else {
            $('#avisoFallbackFaturada').hide();
        }
        
        console.log('✅ Card receita faturada atualizado');
        
    } catch (error) {
        console.error('❌ Erro ao atualizar receita faturada:', error);
        mostrarReceitaFaturadaErro();
    }
}

function mostrarReceitaFaturadaErro() {
    $('#receitaFaturada').text('R$ 0,00');
    $('#qtdCtesFaturados').text('0 CTEs');
    $('#percentualFaturado').text('0% do total');
    $('#avisoFallbackFaturada').show().text('Dados indisponíveis').addClass('text-danger');
}

function carregarReceitaComFaturas() {
    return new Promise((resolve, reject) => {
        console.log('📋 Carregando receita com faturas...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/receita-com-faturas',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                if (response.success && response.dados) {
                    atualizarCardReceitaComFaturas(response.dados);
                    
                    // Criar gráfico se disponível
                    if (response.dados.grafico) {
                        criarGraficoReceitaComFaturas(response.dados.grafico);
                    }
                    
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro na receita com faturas:', error);
                mostrarReceitaComFaturasErro();
                reject(error);
            }
        });
    });
}

function atualizarCardReceitaComFaturas(dados) {
    try {
        console.log('📋 Atualizando card receita com faturas...');
        
        $('#receitaComFaturas').text(formatarMoeda(dados.receita_total || 0));
        $('#qtdCtesComFaturas').text(`${dados.quantidade_ctes || 0} CTEs`);
        $('#ticketMedioFaturas').text(formatarMoeda(dados.ticket_medio || 0));
        
        const cobertura = dados.percentual_cobertura || 0;
        $('#coberturaFaturas').text(`${cobertura.toFixed(1)}% de cobertura`);
        
        // Status com cor baseado na cobertura
        atualizarStatusCard('#statusCobertura', cobertura, 'cobertura');
        
        // Campo usado (para debug)
        if (dados.campo_usado && dados.campo_usado.includes('fallback')) {
            $('#avisoFallbackFaturas').show().text(`Usando: ${dados.campo_usado}`);
        } else {
            $('#avisoFallbackFaturas').hide();
        }
        
        console.log('✅ Card receita com faturas atualizado');
        
    } catch (error) {
        console.error('❌ Erro ao atualizar receita com faturas:', error);
        mostrarReceitaComFaturasErro();
    }
}

function mostrarReceitaComFaturasErro() {
    $('#receitaComFaturas').text('R$ 0,00');
    $('#qtdCtesComFaturas').text('0 CTEs');
    $('#ticketMedioFaturas').text('R$ 0,00');
    $('#coberturaFaturas').text('0% de cobertura');
    $('#avisoFallbackFaturas').show().text('Dados indisponíveis').addClass('text-danger');
}

function carregarReceitaMediaMensal() {
    return new Promise((resolve, reject) => {
        console.log('📈 Carregando receita média mensal...');
        
        const params = montarParametrosFiltros();
        // Usar período maior para média mensal
        params.filtro_dias = 365;
        
        $.ajax({
            url: '/analise-financeira/api/receita-media-mensal',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                if (response.success && response.dados) {
                    atualizarCardReceitaMediaMensal(response.dados);
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro na receita média mensal:', error);
                mostrarReceitaMediaMensalErro();
                reject(error);
            }
        });
    });
}

function atualizarCardReceitaMediaMensal(dados) {
    try {
        console.log('📈 Atualizando card receita média mensal...');
        
        $('#receitaMediaMensal').text(formatarMoeda(dados.receita_media_mensal || 0));
        $('#previsaoProximoMes').text(formatarMoeda(dados.receita_total_periodo / dados.meses_analisados || 0));
        
        // Tendência com ícone
        const tendencia = dados.tendencia || 'estável';
        let icone = '➡️';
        let classe = 'text-muted';
        
        if (tendencia === 'crescimento') {
            icone = '📈';
            classe = 'text-success';
        } else if (tendencia === 'decréscimo') {
            icone = '📉';
            classe = 'text-danger';
        }
        
        $('#tendenciaReceita').html(`${icone} ${tendencia}`).removeClass().addClass(classe);
        $('#mesesAnalisados').text(`${dados.meses_analisados || 0} meses analisados`);
        
        console.log('✅ Card receita média mensal atualizado');
        
    } catch (error) {
        console.error('❌ Erro ao atualizar receita média mensal:', error);
        mostrarReceitaMediaMensalErro();
    }
}

function mostrarReceitaMediaMensalErro() {
    $('#receitaMediaMensal').text('R$ 0,00');
    $('#previsaoProximoMes').text('R$ 0,00');
    $('#tendenciaReceita').text('➡️ estável').removeClass().addClass('text-muted');
    $('#mesesAnalisados').text('0 meses analisados');
}

function carregarEvolucaoReceitaInclusaoFatura() {
    return new Promise((resolve, reject) => {
        console.log('📊 Carregando evolução receita inclusão fatura...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/evolucao-receita-inclusao-fatura',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                if (response.success && response.dados) {
                    criarGraficoEvolucaoReceitaInclusaoFatura(response.dados);
                    resolve(response);
                } else {
                    throw new Error(response?.error || 'Dados não disponíveis');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro na evolução receita inclusão fatura:', error);
                mostrarMensagemGrafico('chartEvolucaoReceitaInclusaoFatura', 'Erro ao carregar evolução da receita por inclusão de fatura');
                reject(error);
            }
        });
    });
}

// ============================================================================
// GRÁFICOS - IMPLEMENTAÇÃO COMPLETA
// ============================================================================

function criarGraficoEvolucaoReceitaFaturada(dados) {
    const canvas = document.getElementById('chartEvolucaoReceitaFaturada');
    if (!canvas || !dados.labels || dados.labels.length === 0) {
        mostrarMensagemGrafico('chartEvolucaoReceitaFaturada', 'Dados insuficientes para evolução da receita faturada');
        return;
    }
    
    try {
        if (chartsFinanceira.evolucaoReceitaFaturada) {
            chartsFinanceira.evolucaoReceitaFaturada.destroy();
        }
        
        chartsFinanceira.evolucaoReceitaFaturada = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Receita Faturada (R$)',
                    data: dados.valores,
                    borderColor: chartColorsFinanceira.receita_faturada,
                    backgroundColor: chartColorsFinanceira.receita_faturada + '20',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointBackgroundColor: chartColorsFinanceira.receita_faturada,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
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
        
        console.log('✅ Gráfico evolução receita faturada criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico evolução receita faturada:', error);
        mostrarMensagemGrafico('chartEvolucaoReceitaFaturada', 'Erro ao criar gráfico');
    }
}

function criarGraficoReceitaComFaturas(dadosGrafico) {
    const canvas = document.getElementById('chartReceitaComFaturas');
    if (!canvas || !dadosGrafico.labels || dadosGrafico.labels.length === 0) {
        mostrarMensagemGrafico('chartReceitaComFaturas', 'Dados insuficientes para receita com faturas');
        return;
    }
    
    try {
        if (chartsFinanceira.receitaComFaturas) {
            chartsFinanceira.receitaComFaturas.destroy();
        }
        
        chartsFinanceira.receitaComFaturas = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dadosGrafico.labels,
                datasets: [{
                    label: 'Receita com Faturas (R$)',
                    data: dadosGrafico.valores,
                    backgroundColor: chartColorsFinanceira.receita_faturas,
                    borderColor: chartColorsFinanceira.receita_faturas,
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
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
        
        console.log('✅ Gráfico receita com faturas criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico receita com faturas:', error);
        mostrarMensagemGrafico('chartReceitaComFaturas', 'Erro ao criar gráfico');
    }
}

function criarGraficoEvolucaoReceitaInclusaoFatura(dados) {
    const canvas = document.getElementById('chartEvolucaoReceitaInclusaoFatura');
    if (!canvas) {
        console.warn('Canvas chartEvolucaoReceitaInclusaoFatura não encontrado');
        return;
    }
    
    if (!dados.labels || dados.labels.length === 0) {
        mostrarMensagemGrafico('chartEvolucaoReceitaInclusaoFatura', 'Nenhum dado encontrado para receita por inclusão de fatura');
        return;
    }
    
    try {
        if (chartsFinanceira.evolucaoReceitaInclusaoFatura) {
            chartsFinanceira.evolucaoReceitaInclusaoFatura.destroy();
        }
        
        const datasets = [];
        
        // Dataset principal - valores de receita
        if (dados.valores && dados.valores.length > 0) {
            datasets.push({
                label: 'Receita por Inclusão Fatura',
                data: dados.valores,
                borderColor: chartColorsFinanceira.receita_media,
                backgroundColor: chartColorsFinanceira.receita_media + '30',
                borderWidth: 3,
                pointRadius: 5,
                pointBackgroundColor: chartColorsFinanceira.receita_media,
                fill: true,
                tension: 0.3,
                yAxisID: 'y'
            });
        }
        
        // Dataset secundário - quantidade de CTEs (se disponível)
        if (dados.quantidades && dados.quantidades.length > 0) {
            datasets.push({
                label: 'Quantidade CTEs',
                data: dados.quantidades,
                borderColor: chartColorsFinanceira.info,
                backgroundColor: chartColorsFinanceira.info + '20',
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: chartColorsFinanceira.info,
                fill: false,
                type: 'line',
                yAxisID: 'y1'
            });
        }
        
        chartsFinanceira.evolucaoReceitaInclusaoFatura = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: dados.titulo || 'Evolução da Receita com Faturas (Data Inclusão)',
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: { 
                        display: datasets.length > 1,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.datasetIndex === 0) {
                                    return `Receita: ${formatarMoeda(context.parsed.y)}`;
                                } else {
                                    return `CTEs: ${context.parsed.y}`;
                                }
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Receita (R$)'
                        },
                        ticks: {
                            callback: function(value) {
                                return formatarMoedaCompacta(value);
                            }
                        }
                    },
                    y1: datasets.length > 1 ? {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade CTEs'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    } : undefined
                }
            }
        });
        
        console.log('✅ Gráfico evolução receita inclusão fatura criado');
        
        // Atualizar estatísticas se disponíveis
        if (dados.estatisticas) {
            const stats = dados.estatisticas;
            $('#totalPeriodoInclusao').text(formatarMoeda(stats.total_periodo || 0));
            $('#mediaMensalInclusao').text(formatarMoeda(stats.media_mensal || 0));
            $('#totalCtesInclusao').text((stats.total_ctes || 0).toLocaleString('pt-BR'));
            $('#mesesAnalisadosInclusao').text(stats.meses_analisados || 0);
        }
        
    } catch (error) {
        console.error('❌ Erro no gráfico evolução receita inclusão fatura:', error);
        mostrarMensagemGrafico('chartEvolucaoReceitaInclusaoFatura', 'Erro ao criar gráfico de evolução');
    }
}

// ============================================================================
// SISTEMA DE EXPORTAÇÃO FUNCIONAL
// ============================================================================

function exportarExcel() {
    console.log('📊 Iniciando exportação Excel...');
    
    if (!filtrosAtivos || typeof filtrosAtivos !== 'object') {
        console.error('Filtros não definidos');
        return;
    }
    
    mostrarLoading('Gerando arquivo Excel...');
    
     try {
        const params = montarParametrosFiltros();
        const url = `/analise-financeira/api/exportar/excel?${new URLSearchParams(params).toString()}`;
        
        console.log('🔗 URL de exportação Excel:', url);
        
        // Criar link de download
        const link = document.createElement('a');
        link.href = url;
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Configurar resposta
        link.addEventListener('click', function() {
            setTimeout(() => {
                esconderLoading();
                mostrarToast('✅ Solicitação de Excel enviada. Verifique o download.', 'success');
            }, 2000);
        });
        
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Download Excel solicitado');
        
    } catch (error) {
        console.error('❌ Erro na exportação Excel:', error);
        esconderLoading();
        mostrarToast('❌ Erro ao gerar arquivo Excel: ' + error.message, 'error');
    }
}

function exportarPDF() {
    console.log('📄 Iniciando exportação PDF...');
    
    // MESMA correção para PDF
    if (!filtrosAtivos || typeof filtrosAtivos !== 'object') {
        console.error('Filtros não definidos');
        return;
    }
    
    mostrarLoading('Gerando relatório PDF...');
    
    try {
        const params = montarParametrosFiltros();
        const url = `/analise-financeira/api/exportar/pdf?${new URLSearchParams(params).toString()}`;
        
        console.log('🔗 URL de exportação PDF:', url);
        
        // Criar link de download
        const link = document.createElement('a');
        link.href = url;
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Configurar resposta
        link.addEventListener('click', function() {
            setTimeout(() => {
                esconderLoading();
                mostrarToast('✅ Solicitação de PDF enviada. Verifique o download.', 'success');
            }, 3000);
        });
        
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Download PDF solicitado');
        
    } catch (error) {
        console.error('❌ Erro na exportação PDF:', error);
        esconderLoading();
        mostrarToast('❌ Erro ao gerar relatório PDF: ' + error.message, 'error');
    }
}

function exportarJSON() {
    console.log('📋 Iniciando exportação JSON...');
    
    // MESMA correção para JSON
    if (!filtrosAtivos || typeof filtrosAtivos !== 'object') {
        console.error('Filtros não definidos');
        return;
    }
    
    mostrarLoading('Gerando arquivo JSON...');
    
    try {
        const params = montarParametrosFiltros();
        const url = `/analise-financeira/api/exportar/json?${new URLSearchParams(params).toString()}`;
        
        // Fazer requisição para obter JSON
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ${response.status}: ${response.statusText}`);
                }
                return response.blob();
            })
            .then(blob => {
                // Criar download
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                const timestamp = new Date().toISOString().split('T')[0];
                link.download = `analise_financeira_${timestamp}.json`;
                link.style.display = 'none';
                
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                esconderLoading();
                mostrarToast('✅ Arquivo JSON gerado com sucesso!', 'success');
                console.log('✅ Download JSON concluído');
            })
            .catch(error => {
                console.error('❌ Erro no download JSON:', error);
                esconderLoading();
                mostrarToast('❌ Erro ao gerar arquivo JSON: ' + error.message, 'error');
            });
        
    } catch (error) {
        console.error('❌ Erro na exportação JSON:', error);
        esconderLoading();
        mostrarToast('❌ Erro ao preparar exportação JSON: ' + error.message, 'error');
    }
}


// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

function montarParametrosFiltros() {
    const params = {
        filtro_dias: filtrosAtivos.periodo || 180
    };
    
    if (filtrosAtivos.cliente) {
        params.filtro_cliente = filtrosAtivos.cliente;
    }
    
    if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
        params.data_inicio = filtrosAtivos.dataInicio;
        params.data_fim = filtrosAtivos.dataFim;
    }
    
    return params;
}

function mostrarMensagemGrafico(canvasId, mensagem) {
    const canvas = document.getElementById(canvasId);
    if (canvas && canvas.parentElement) {
        canvas.parentElement.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-chart-bar text-muted" style="font-size: 2rem;"></i>
                <p class="text-muted mt-2">${mensagem}</p>
                <button class="btn btn-outline-primary btn-sm" onclick="carregarTodasAsMetricas()">
                    <i class="fas fa-refresh"></i> Tentar Novamente
                </button>
            </div>
        `;
    }
}

function mostrarErroCard(cardId, mensagem) {
    $(`#${cardId}`).html(`
        <div class="alert alert-warning m-2">
            <i class="fas fa-exclamation-triangle"></i>
            <small>${mensagem}</small>
        </div>
    `);
}

function atualizarStatusCard(selector, valor, tipo) {
    const elemento = $(selector);
    if (!elemento.length) return;
    
    elemento.removeClass('text-success text-warning text-danger text-muted');
    
    let classe = 'text-muted';
    
    switch (tipo) {
        case 'baixas':
            if (valor >= 80) classe = 'text-success';
            else if (valor >= 60) classe = 'text-warning';
            else classe = 'text-danger';
            break;
            
        case 'faturamento':
            if (valor >= 90) classe = 'text-success';
            else if (valor >= 70) classe = 'text-warning';
            else classe = 'text-danger';
            break;
            
        case 'cobertura':
            if (valor >= 80) classe = 'text-success';
            else if (valor >= 60) classe = 'text-warning';
            else classe = 'text-danger';
            break;
    }
    
    elemento.addClass(classe);
}

function carregarListaClientes() {
    console.log('👥 Carregando lista de clientes...');
    
    $.ajax({
        url: '/analise-financeira/api/clientes',
        method: 'GET',
        timeout: 15000,
        success: function(response) {
            if (response.success && response.clientes) {
                const select = $('#filtroCliente');
                select.find('option:not(:first)').remove();
                
                response.clientes.forEach(cliente => {
                    select.append(`<option value="${cliente}">${cliente}</option>`);
                });
                
                console.log(`✅ ${response.clientes.length} clientes carregados`);
            }
        },
        error: function() {
            console.warn('⚠️ Não foi possível carregar lista de clientes');
        }
    });
}

function mostrarLoading(mensagem = 'Carregando...') {
    if ($('#loadingAnalise').length) {
        $('#loadingAnalise').html(`
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-2 text-muted">${mensagem}</p>
            </div>
        `).show();
    }
}

function esconderLoading() {
    $('#loadingAnalise').hide();
}

function atualizarUltimaAtualizacao() {
    const agora = new Date().toLocaleString('pt-BR');
    $('#ultimaAtualizacao').text(`Última atualização: ${agora}`);
}

// Função para mostrar toast melhorada
function mostrarToast(mensagem, tipo = 'info') {
    console.log(`🔔 ${tipo.toUpperCase()}: ${mensagem}`);
    
    // Se existir sistema de toast Bootstrap ou similar
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        // Implementar toast Bootstrap se disponível
        const toastElement = document.createElement('div');
        toastElement.className = `toast align-items-center text-bg-${tipo === 'success' ? 'success' : tipo === 'error' ? 'danger' : 'primary'} border-0`;
        toastElement.setAttribute('role', 'alert');
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${mensagem}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toastElement);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remover após 5 segundos
        setTimeout(() => {
            if (toastElement.parentNode) {
                toastElement.parentNode.removeChild(toastElement);
            }
        }, 5000);
    } else {
        // Fallback para alert simples apenas para erros críticos
        if (tipo === 'error') {
            alert(mensagem);
        }
    }
}

console.log('🔧 Correções de exportação aplicadas - sem verificações problemáticas');

function formatarMoeda(valor) {
    const numero = parseFloat(valor) || 0;
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(numero);
}

function formatarMoedaCompacta(valor) {
    const numero = parseFloat(valor) || 0;
    
    if (numero >= 1000000) {
        return 'R$ ' + (numero / 1000000).toFixed(1) + 'M';
    } else if (numero >= 1000) {
        return 'R$ ' + (numero / 1000).toFixed(1) + 'K';
    } else {
        return 'R$ ' + numero.toFixed(0);
    }
}

// ============================================================================
// INICIALIZAÇÃO AUTOMÁTICA
// ============================================================================

// Auto-inicialização quando DOM estiver pronto
$(document).ready(function() {
    console.log('🎯 DOM pronto - Verificando página...');
    
    // Verificar se estamos na página correta
    if (window.location.pathname.includes('analise-financeira')) {
        console.log('✅ Página de análise financeira detectada');
        
        // Aguardar um pouco para garantir que tudo foi carregado
        setTimeout(function() {
            inicializarDashboardCompleto();
        }, 500);
    } else {
        console.log('ℹ️ Não estamos na página de análise financeira');
    }
});

// Compatibilidade com carregamento via window.onload
window.addEventListener('load', function() {
    if (window.location.pathname.includes('analise-financeira')) {
        // Verificar se já foi inicializado
        if (Object.keys(chartsFinanceira).length === 0) {
            console.log('🔄 Inicializando via window.onload...');
            setTimeout(inicializarDashboardCompleto, 1000);
        }
    }
});

console.log('📊 Análise Financeira JS v2.0 carregado com sucesso!');

// ============================================================================
// SCRIPT DE CORREÇÃO FINAL - Análise Financeira
// Use este script TEMPORARIAMENTE para diagnosticar e corrigir problemas
// ============================================================================

// ADICIONE ESTAS FUNÇÕES AO SEU analise_financeira.js:

// Função principal de diagnóstico e correção
function diagnosticarECorrigir() {
    console.log('🔍 Iniciando diagnóstico completo...');
    
    mostrarLoading('Diagnosticando problemas...');
    
    // Primeiro: verificar a base de dados
    $.ajax({
        url: '/analise-financeira/api/debug/base-dados',
        method: 'GET',
        timeout: 15000,
        success: function(response) {
            console.log('📊 Diagnóstico da base:', response);
            
            if (response.success) {
                const diagnostico = response.diagnostico;
                mostrarResultadoDiagnostico(diagnostico);
                
                // Se tem dados, usar APIs corrigidas
                if (diagnostico.registros_ultimos_180_dias > 0) {
                    console.log('✅ Encontrados dados na base, carregando com APIs corrigidas...');
                    carregarComAPIsCorrigidas();
                } else {
                    console.log('⚠️ Nenhum dado encontrado, usando dados de exemplo...');
                    carregarDadosExemplo();
                }
            } else {
                console.error('❌ Erro no diagnóstico:', response.error);
                mostrarErroGeneral('Erro ao diagnosticar: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Erro na API de diagnóstico:', error);
            
            // Se a API de diagnóstico falhou, tentar APIs normais
            console.log('🔄 Tentando carregar com APIs normais...');
            carregarTodasAsMetricas();
        }
    });
}

function mostrarResultadoDiagnostico(diagnostico) {
    console.log('📋 Resultado do diagnóstico:');
    console.log('- Total registros na tabela:', diagnostico.total_registros_tabela);
    console.log('- Registros últimos 180 dias:', diagnostico.registros_ultimos_180_dias);
    console.log('- Campos preenchidos:', diagnostico.campos_preenchidos);
    
    if (diagnostico.problemas_identificados.length > 0) {
        console.log('⚠️ Problemas identificados:');
        diagnostico.problemas_identificados.forEach(problema => {
            console.log('  -', problema);
        });
        
        console.log('💡 Recomendações:');
        diagnostico.recomendacoes.forEach(recomendacao => {
            console.log('  -', recomendacao);
        });
    }
    
    // Mostrar aviso visual se necessário
    if (diagnostico.registros_ultimos_180_dias === 0) {
        mostrarAvisoSemDados();
    }
}

function carregarComAPIsCorrigidas() {
    console.log('🔧 Carregando com APIs corrigidas...');
    
    const promises = [
        carregarMetricasForcadas(),
        carregarGraficosSimples()
    ];
    
    Promise.allSettled(promises).then(results => {
        console.log('📊 Resultado das APIs corrigidas:');
        results.forEach((result, index) => {
            const nomes = ['Métricas Forçadas', 'Gráficos Simples'];
            console.log(`  ${nomes[index]}: ${result.status}`);
            if (result.status === 'rejected') {
                console.error(`    Erro: ${result.reason}`);
            }
        });
        
        esconderLoading();
        atualizarUltimaAtualizacao();
    });
}

function carregarMetricasForcadas() {
    return new Promise((resolve, reject) => {
        console.log('💪 Carregando métricas forçadas...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/metricas-forcadas',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                console.log('📊 Resposta métricas forçadas:', response);
                
                if (response.success) {
                    processarMetricasForcadas(response);
                    resolve(response);
                } else {
                    throw new Error(response.error || 'Erro desconhecido');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro nas métricas forçadas:', error);
                reject(error);
            }
        });
    });
}

function processarMetricasForcadas(response) {
    console.log('⚙️ Processando métricas forçadas...');
    
    try {
        const basicas = response.metricas_basicas || {};
        const faturada = response.receita_faturada || {};
        const comFaturas = response.receita_com_faturas || {};
        const status = response.status_sistema || {};
        const topClientes = response.top_clientes || [];
        
        // Atualizar cards principais
        $('#receitaMesAtual').text(formatarMoeda(basicas.receita_mes_atual || 0));
        $('#totalCtes').text((basicas.total_ctes || 0).toLocaleString('pt-BR'));
        $('#ticketMedio').text(formatarMoeda(basicas.ticket_medio || 0));
        
        // Receita Faturada
        $('#receitaFaturada').text(formatarMoeda(faturada.receita_total || 0));
        $('#qtdCtesFaturados').text(`${faturada.quantidade_ctes || 0} CTEs`);
        $('#percentualFaturado').text(`${(faturada.percentual_total || 0).toFixed(1)}% do total`);
        
        // Receita com Faturas  
        $('#receitaComFaturas').text(formatarMoeda(comFaturas.receita_total || 0));
        $('#qtdCtesComFaturas').text(`${comFaturas.quantidade_ctes || 0} CTEs`);
        $('#ticketMedioFaturas').text(formatarMoeda(comFaturas.receita_total / comFaturas.quantidade_ctes || 0));
        $('#coberturaFaturas').text(`${(comFaturas.percentual_cobertura || 0).toFixed(1)}% de cobertura`);
        
        // CORRIGIR STATUS DO SISTEMA (o que estava faltando!)
        $('#totalRegistros').text((status.total_registros || 0).toLocaleString('pt-BR'));
        $('#taxaFaturamento').text(`${(status.taxa_faturamento || 0).toFixed(1)}%`);
        $('#taxaComFaturas').text(`${(status.taxa_com_faturas || 0).toFixed(1)}%`);
        $('#tempoMedioCobranca').text(`${(status.tempo_medio_cobranca || 0).toFixed(0)} dias`);
        $('#concentracaoTop5').text(`${(status.concentracao_top5 || 0).toFixed(1)}%`);
        $('#impactoTopCliente').text(`${(status.impacto_top_cliente || 0).toFixed(1)}%`);
        
        // Atualizar cores dos status
        atualizarStatusCard('#taxaFaturamento', status.taxa_faturamento || 0, 'faturamento');
        atualizarStatusCard('#taxaComFaturas', status.taxa_com_faturas || 0, 'cobertura');
        atualizarStatusCard('#concentracaoTop5', status.concentracao_top5 || 0, 'concentracao');
        atualizarStatusCard('#impactoTopCliente', status.impacto_top_cliente || 0, 'impacto');
        
        // Atualizar tabela de clientes
        if (topClientes.length > 0) {
            atualizarTabelaTopClientes(topClientes);
        }
        
        // Mostrar informações de debug se necessário
        if (response.debug_info) {
            console.log('🔍 Info de debug:', response.debug_info);
            
            // Mostrar avisos de fallback
            if (response.debug_info.metodo_receita_faturada.includes('fallback')) {
                $('#avisoFallbackFaturada').show().text(`Usando: ${response.debug_info.metodo_receita_faturada}`);
            }
            
            if (response.debug_info.metodo_receita_faturas.includes('fallback')) {
                $('#avisoFallbackFaturas').show().text(`Usando: ${response.debug_info.metodo_receita_faturas}`);
            }
        }
        
        console.log('✅ Métricas forçadas processadas com sucesso');
        
    } catch (error) {
        console.error('❌ Erro ao processar métricas forçadas:', error);
        mostrarErroGeneral('Erro ao processar métricas: ' + error.message);
    }
}

function carregarGraficosSimples() {
    return new Promise((resolve, reject) => {
        console.log('📊 Carregando gráficos simples...');
        
        const params = montarParametrosFiltros();
        
        $.ajax({
            url: '/analise-financeira/api/graficos-simples',
            method: 'GET',
            data: params,
            timeout: 20000,
            success: function(response) {
                console.log('📈 Resposta gráficos simples:', response);
                
                if (response.success && response.graficos) {
                    criarGraficosSimples(response.graficos);
                    resolve(response);
                } else {
                    throw new Error(response.error || 'Erro desconhecido');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Erro nos gráficos simples:', error);
                reject(error);
            }
        });
    });
}

function criarGraficosSimples(graficos) {
    console.log('📊 Criando gráficos simples...');
    
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js não disponível');
        mostrarErroGeneral('Chart.js não carregado. Verifique se a biblioteca está incluída.');
        return;
    }
    
    try {
        // 1. Gráfico Receita Mensal
        if (graficos.receita_mensal) {
            criarGraficoReceitaMensalSimples(graficos.receita_mensal);
        }
        
        // 2. Gráfico Concentração
        if (graficos.concentracao_clientes) {
            criarGraficoConcentracaoSimples(graficos.concentracao_clientes);
        }
        
        // 3. Gráfico Tendência
        if (graficos.tendencia_linear) {
            criarGraficoTendenciaSimples(graficos.tendencia_linear);
        }
        
        // 4. Gráfico Tempo Cobrança
        if (graficos.tempo_cobranca) {
            criarGraficoTempoCobrancaSimples(graficos.tempo_cobranca);
        }
        
        console.log('✅ Gráficos simples criados');
        
    } catch (error) {
        console.error('❌ Erro ao criar gráficos simples:', error);
        mostrarErroGeneral('Erro ao criar gráficos: ' + error.message);
    }
}

function criarGraficoReceitaMensalSimples(dados) {
    const canvas = document.getElementById('chartReceitaMensal');
    if (!canvas) {
        console.warn('⚠️ Canvas chartReceitaMensal não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.receitaMensal) {
            chartsFinanceira.receitaMensal.destroy();
        }
        
        chartsFinanceira.receitaMensal = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dados.labels || ['Sem dados'],
                datasets: [{
                    label: 'Receita Mensal (R$)',
                    data: dados.valores || [0],
                    backgroundColor: chartColorsFinanceira.primary,
                    borderColor: chartColorsFinanceira.primary,
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const qtd = dados.quantidades && dados.quantidades[context.dataIndex] ? 
                                          ` (${dados.quantidades[context.dataIndex]} CTEs)` : '';
                                return `Receita: ${formatarMoeda(context.parsed.y)}${qtd}`;
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
        
        console.log('✅ Gráfico receita mensal simples criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico receita mensal simples:', error);
        mostrarMensagemGrafico('chartReceitaMensal', 'Erro ao criar gráfico de receita mensal');
    }
}

function criarGraficoConcentracaoSimples(dados) {
    const canvas = document.getElementById('chartConcentracao');
    if (!canvas) {
        console.warn('⚠️ Canvas chartConcentracao não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.concentracao) {
            chartsFinanceira.concentracao.destroy();
        }
        
        chartsFinanceira.concentracao = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: dados.labels || ['Sem dados'],
                datasets: [{
                    data: dados.valores || [1],
                    backgroundColor: [
                        '#28a745', '#20c997', '#17a2b8', 
                        '#ffc107', '#fd7e14', '#6c757d'
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
                            padding: 15,
                            font: { size: window.innerWidth < 768 ? 10 : 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (dados.valores && dados.valores.length > 1) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((context.raw / total) * 100).toFixed(1);
                                    return `${context.label}: ${formatarMoeda(context.raw)} (${percentage}%)`;
                                } else {
                                    return 'Aguardando dados reais';
                                }
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico concentração simples criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico concentração simples:', error);
        mostrarMensagemGrafico('chartConcentracao', 'Erro ao criar gráfico de concentração');
    }
}

function criarGraficoTendenciaSimples(dados) {
    const canvas = document.getElementById('chartTendencia');
    if (!canvas) {
        console.warn('⚠️ Canvas chartTendencia não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.tendencia) {
            chartsFinanceira.tendencia.destroy();
        }
        
        chartsFinanceira.tendencia = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dados.labels || ['Sem dados'],
                datasets: [{
                    label: 'Receita Real',
                    data: dados.valores_reais || [0],
                    borderColor: chartColorsFinanceira.primary,
                    backgroundColor: chartColorsFinanceira.primary + '20',
                    borderWidth: 3,
                    pointRadius: 6,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
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
        
        console.log('✅ Gráfico tendência simples criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico tendência simples:', error);
        mostrarMensagemGrafico('chartTendencia', 'Erro ao criar gráfico de tendência');
    }
}

function criarGraficoTempoCobrancaSimples(dados) {
    const canvas = document.getElementById('chartTempoCobranca');
    if (!canvas) {
        console.warn('⚠️ Canvas chartTempoCobranca não encontrado');
        return;
    }
    
    try {
        if (chartsFinanceira.tempoCobranca) {
            chartsFinanceira.tempoCobranca.destroy();
        }
        
        chartsFinanceira.tempoCobranca = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: dados.labels || ['Sem dados'],
                datasets: [{
                    label: 'Quantidade de CTEs',
                    data: dados.valores || [0],
                    backgroundColor: chartColorsFinanceira.info,
                    borderColor: chartColorsFinanceira.info,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
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
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico tempo cobrança simples criado');
        
    } catch (error) {
        console.error('❌ Erro no gráfico tempo cobrança simples:', error);
        mostrarMensagemGrafico('chartTempoCobranca', 'Erro ao criar gráfico de tempo cobrança');
    }
}

function carregarDadosExemplo() {
    console.log('📝 Carregando dados de exemplo...');
    
    // Dados de exemplo para quando não há dados reais
    const dadosExemplo = {
        metricas_basicas: {
            receita_mes_atual: 0,
            total_ctes: 0,
            ticket_medio: 0
        },
        receita_faturada: {
            receita_total: 0,
            quantidade_ctes: 0,
            percentual_total: 0
        },
        receita_com_faturas: {
            receita_total: 0,
            quantidade_ctes: 0,
            percentual_cobertura: 0
        },
        status_sistema: {
            total_registros: 0,
            taxa_faturamento: 0,
            taxa_com_faturas: 0,
            tempo_medio_cobranca: 0,
            concentracao_top5: 0,
            impacto_top_cliente: 0
        }
    };
    
    processarMetricasForcadas({success: true, ...dadosExemplo});
    
    // Gráficos de exemplo
    const graficosExemplo = {
        receita_mensal: {
            labels: ['Jan/2024', 'Fev/2024', 'Mar/2024', 'Abr/2024', 'Mai/2024', 'Jun/2024'],
            valores: [0, 0, 0, 0, 0, 0],
            quantidades: [0, 0, 0, 0, 0, 0]
        },
        concentracao_clientes: {
            labels: ['Aguardando dados'],
            valores: [1]
        },
        tempo_cobranca: {
            labels: ['0-30 dias', '31-60 dias', '61-90 dias', '90+ dias'],
            valores: [0, 0, 0, 0]
        },
        tendencia_linear: {
            labels: ['Jan/2024', 'Fev/2024', 'Mar/2024', 'Abr/2024', 'Mai/2024', 'Jun/2024'],
            valores_reais: [0, 0, 0, 0, 0, 0]
        }
    };
    
    criarGraficosSimples(graficosExemplo);
    
    // Mostrar aviso
    mostrarAvisoSemDados();
    
    esconderLoading();
}

function mostrarAvisoSemDados() {
    console.log('⚠️ Exibindo aviso de dados insuficientes');
    
    const aviso = `
        <div class="alert alert-warning m-3" role="alert">
            <h5><i class="fas fa-exclamation-triangle"></i> Dados Insuficientes</h5>
            <p><strong>Não foram encontrados dados suficientes para análise.</strong></p>
            <ul>
                <li>Verifique se há CTEs cadastrados nos últimos 180 dias</li>
                <li>Confirme se o campo <code>valor_total</code> está preenchido</li>
                <li>Verifique se o campo <code>destinatario_nome</code> tem valores</li>
            </ul>
            <button class="btn btn-primary btn-sm" onclick="diagnosticarECorrigir()">
                <i class="fas fa-refresh"></i> Tentar Novamente
            </button>
        </div>
    `;
    
    if ($('#loadingAnalise').length) {
        $('#loadingAnalise').html(aviso).show();
    } else {
        $('body').prepend(`<div style="position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;">${aviso}</div>`);
    }
}

function mostrarErroGeneral(mensagem) {
    console.error('❌ Erro geral:', mensagem);
    
    const erro = `
        <div class="alert alert-danger m-3" role="alert">
            <h5><i class="fas fa-exclamation-triangle"></i> Erro no Sistema</h5>
            <p>${mensagem}</p>
            <button class="btn btn-primary btn-sm" onclick="diagnosticarECorrigir()">
                <i class="fas fa-refresh"></i> Tentar Novamente
            </button>
        </div>
    `;
    
    if ($('#loadingAnalise').length) {
        $('#loadingAnalise').html(erro).show();
    }
}

// SISTEMA DE EXPORTAÇÃO CORRIGIDO
function exportarExcelCorrigido() {
    console.log('📊 Iniciando exportação Excel corrigida...');
    
    mostrarLoading('Gerando arquivo Excel...');
    
    try {
        const params = montarParametrosFiltros();
        
        // Usar método de POST para enviar mais dados
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = '/analise-financeira/api/exportar/excel';
        form.style.display = 'none';
        
        Object.keys(params).forEach(key => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = params[key];
            form.appendChild(input);
        });
        
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
        
        // Feedback visual
        setTimeout(() => {
            esconderLoading();
            mostrarToast('Arquivo Excel foi solicitado. Se não baixou automaticamente, verifique se há dados suficientes.', 'info');
        }, 3000);
        
    } catch (error) {
        console.error('❌ Erro na exportação Excel:', error);
        esconderLoading();
        mostrarToast('Erro ao exportar Excel: ' + error.message, 'error');
    }
}

/// ============================================================================
// CORREÇÃO DEFINITIVA - ADICIONAR AO FINAL DO ARQUIVO analise_financeira.js
// NÃO SUBSTITUIR O ARQUIVO INTEIRO, APENAS ADICIONAR ESTAS FUNÇÕES
// ============================================================================

// Sobrescrever a função de inicialização principal
function inicializarDashboardCompleto() {
    console.log('🚀 Dashboard Financeiro - Versão Corrigida Iniciando...');
    
    if (!window.location.pathname.includes('analise-financeira')) {
        return;
    }
    
    // Aguardar DOM
    if ($('#filtroPeriodo').length === 0) {
        setTimeout(inicializarDashboardCompleto, 500);
        return;
    }
    
    // Configurar eventos básicos
    configurarEventosBasicos();
    
    // Carregar dados com delay
    setTimeout(function() {
        carregarDadosCorrigidos();
    }, 1000);
}

function configurarEventosBasicos() {
    // Filtros
    $('#filtroPeriodo').off('change').on('change', function() {
        filtrosAtivos.periodo = parseInt($(this).val());
        carregarDadosCorrigidos();
    });
    
    $('#filtroCliente').off('change').on('change', function() {
        const valor = $(this).val();
        filtrosAtivos.cliente = (valor && valor !== 'todos') ? valor : null;
        carregarDadosCorrigidos();
    });

    // ADICIONAR estas linhas na função configurarEventosBasicos(), 
// DEPOIS das linhas do filtroCliente:

    // Filtros de data - ADICIONAR
    $('#dataInicio').off('change').on('change', function() {
        filtrosAtivos.dataInicio = $(this).val();
        console.log('Data início alterada:', filtrosAtivos.dataInicio);
        if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
            carregarDadosCorrigidos();
        }
    });
    
    $('#dataFim').off('change').on('change', function() {
        filtrosAtivos.dataFim = $(this).val();
        console.log('Data fim alterada:', filtrosAtivos.dataFim);
        if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
            carregarDadosCorrigidos();
        }
    });
    
    // Botão aplicar filtros
    $('#btnAplicarFiltros').off('click').on('click', function() {
        console.log('Aplicando filtros:', filtrosAtivos);
        carregarDadosCorrigidos();
    });
    
    // Botão limpar filtros  
    $('#btnLimparFiltros').off('click').on('click', function() {
        $('#filtroPeriodo').val('180');
        $('#filtroCliente').val('');
        $('#dataInicio').val('');
        $('#dataFim').val('');
        
        filtrosAtivos = { 
            periodo: 180, 
            cliente: null,
            dataInicio: null,
            dataFim: null 
        };
        
        console.log('Filtros limpos');
        carregarDadosCorrigidos();
    });
    
    // Botões de exportação
    $('.btn-export-excel, .btn-exportar-excel').off('click').on('click', function() {
        const params = new URLSearchParams({
            filtro_dias: filtrosAtivos.periodo || 180
        });
        if (filtrosAtivos.cliente) params.set('filtro_cliente', filtrosAtivos.cliente);
        
        window.open('/analise-financeira/api/exportar/excel?' + params.toString(), '_blank');
    });
    
    $('.btn-export-pdf, .btn-exportar-pdf').off('click').on('click', function() {
        const params = new URLSearchParams({
            filtro_dias: filtrosAtivos.periodo || 180
        });
        if (filtrosAtivos.cliente) params.set('filtro_cliente', filtrosAtivos.cliente);
        
        window.open('/analise-financeira/api/exportar/pdf?' + params.toString(), '_blank');
    });
}

function carregarDadosCorrigidos() {
    console.log('📊 Carregando dados corrigidos...');
    
    mostrarLoadingSimples();
    
   const params = {
    filtro_dias: filtrosAtivos.periodo || 180
};

if (filtrosAtivos.cliente) {
    params.filtro_cliente = filtrosAtivos.cliente;
}

// ✨ ADICIONAR ESTAS LINHAS - NOVO
if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
    params.data_inicio = filtrosAtivos.dataInicio;
    params.data_fim = filtrosAtivos.dataFim;
    console.log('📅 Enviando datas para API:', params.data_inicio, 'até', params.data_fim);
}
    
    // Carregar métricas
    $.ajax({
        url: '/analise-financeira/api/metricas-forcadas',
        method: 'GET',
        data: params,
        timeout: 20000,
        success: function(response) {
            if (response.success) {
                atualizarCardsCorrigidos(response);
            } else {
                console.error('Erro nas métricas:', response.error);
                zerarCards();
            }
        },
        error: function() {
            console.error('Erro na requisição de métricas');
            zerarCards();
        }
    });
    
    // Carregar gráficos
    $.ajax({
        url: '/analise-financeira/api/graficos-simples',
        method: 'GET',
        data: params,
        timeout: 20000,
        success: function(response) {
            if (response.success && response.graficos) {
                criarGraficosCorrigidos(response.graficos);
            } else {
                criarGraficosVazios();
            }
        },
        error: function() {
            console.error('Erro nos gráficos');
            criarGraficosVazios();
        }
    });
    
    // Carregar top clientes
    $.ajax({
        url: '/analise-financeira/api/top-clientes',
        method: 'GET',
        data: params,
        timeout: 15000,
        success: function(response) {
            if (response.success && response.top_clientes) {
                atualizarTabelaClientes(response.top_clientes);
            }
        },
        error: function() {
            console.error('Erro no top clientes');
        }
    });
    
    esconderLoadingSimples();
    setTimeout(function() {
    carregarGraficosEvolucao();
}, 500);
}

function atualizarCardsCorrigidos(response) {
    const basicas = response.metricas_basicas || {};
    const faturada = response.receita_faturada || {};
    const comFaturas = response.receita_com_faturas || {};
    const status = response.status_sistema || {};
    
    // Cards principais
    $('#receitaMesAtual').text(formatarMoedaSimples(basicas.receita_mes_atual || 0));
    $('#totalCtes').text((basicas.total_ctes || 0).toLocaleString('pt-BR'));
    $('#ticketMedio').text(formatarMoedaSimples(basicas.ticket_medio || 0));
    
    // Receita Faturada
    $('#receitaFaturada').text(formatarMoedaSimples(faturada.receita_total || 0));
    $('#qtdCtesFaturados').text(`${faturada.quantidade_ctes || 0} CTEs`);
    $('#percentualFaturado').text(`${(faturada.percentual_total || 0).toFixed(1)}% do total`);
    
    // Receita com Faturas
    $('#receitaComFaturas').text(formatarMoedaSimples(comFaturas.receita_total || 0));
    $('#qtdCtesComFaturas').text(`${comFaturas.quantidade_ctes || 0} CTEs`);
    $('#coberturaFaturas').text(`${(comFaturas.percentual_cobertura || 0).toFixed(1)}% de cobertura`);
    
    // Status do Sistema
    $('#totalRegistros').text((status.total_registros || 0).toLocaleString('pt-BR'));
    $('#taxaFaturamento').text(`${(status.taxa_faturamento || 0).toFixed(1)}%`);
    $('#taxaComFaturas').text(`${(status.taxa_com_faturas || 0).toFixed(1)}%`);
    $('#tempoMedioCobranca').text(`${(status.tempo_medio_cobranca || 0).toFixed(0)} dias`);
    $('#concentracaoTop5').text(`${(status.concentracao_top5 || 0).toFixed(1)}%`);
    $('#impactoTopCliente').text(`${(status.impacto_top_cliente || 0).toFixed(1)}%`);
    // Cards que estavam faltando
   // SUBSTITUIR as linhas que você adicionou na função atualizarCardsCorrigidos por estas:

// Carregar dados corretos para receita média mensal
$.ajax({
    url: '/analise-financeira/api/receita-media-mensal',
    method: 'GET',
    data: { filtro_dias: 365 }, // Últimos 12 meses para média
    success: function(responseMedia) {
        if (responseMedia.success && responseMedia.dados) {
            const dadosMedia = responseMedia.dados;
            
            // Receita Média Mensal correta
            $('#receitaMediaMensal').text(formatarMoedaSimples(dadosMedia.receita_media_mensal || 0));
            
            // Previsão baseada na média real
            const previsao = dadosMedia.receita_media_mensal * 1.05; // 5% de crescimento conservador
            $('#previsaoProximoMes').text(formatarMoedaSimples(previsao || 0));
            
            // Tendência baseada nos dados reais
            let tendencia = dadosMedia.tendencia || 'estável';
            let icone = '➡️';
            let classe = 'text-muted';
            
            if (tendencia === 'crescimento') {
                icone = '📈';
                classe = 'text-success';
            } else if (tendencia === 'decréscimo') {
                icone = '📉'; 
                classe = 'text-danger';
            }
            
            $('#tendenciaReceita').html(icone + ' ' + tendencia).removeClass().addClass(classe);
            $('#mesesAnalisados').text(`${dadosMedia.meses_analisados || 6} meses analisados`);
        }
    },
    error: function() {
        // Fallback com cálculo simples se a API falhar
        const valorTotal = basicas.receita_mes_atual || 0;
        const mediaEstimada = valorTotal / 6; // Dividir por 6 meses como estimativa
        
        $('#receitaMediaMensal').text(formatarMoedaSimples(mediaEstimada));
        $('#previsaoProximoMes').text(formatarMoedaSimples(mediaEstimada));
        $('#tendenciaReceita').html('➡️ estimado').removeClass().addClass('text-warning');
        $('#mesesAnalisados').text('6 meses (estimado)');
    }
});
    
    console.log('✅ Cards atualizados com sucesso');
}

function zerarCards() {
    $('#receitaMesAtual').text('R$ 0,00');
    $('#totalCtes').text('0');
    $('#ticketMedio').text('R$ 0,00');
    $('#receitaFaturada').text('R$ 0,00');
    $('#qtdCtesFaturados').text('0 CTEs');
    $('#percentualFaturado').text('0% do total');
    $('#receitaComFaturas').text('R$ 0,00');
    $('#qtdCtesComFaturas').text('0 CTEs');
    $('#coberturaFaturas').text('0% de cobertura');
    $('#totalRegistros').text('0');
    $('#taxaFaturamento').text('0%');
    $('#taxaComFaturas').text('0%');
    $('#tempoMedioCobranca').text('0 dias');
    $('#concentracaoTop5').text('0%');
    $('#impactoTopCliente').text('0%');
}

// SUBSTITUIR APENAS A FUNÇÃO criarGraficosCorrigidos no arquivo analise_financeira.js

function criarGraficosCorrigidos(graficos) {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js não disponível');
        return;
    }
    
    // Gráfico Receita Mensal
    const canvasReceita = document.getElementById('chartReceitaMensal');
    if (canvasReceita) {
        try {
            // Verificar se existe E se tem o método destroy
            if (window.chartReceitaMensal && typeof window.chartReceitaMensal.destroy === 'function') {
                window.chartReceitaMensal.destroy();
            }
            
            const ctx = canvasReceita.getContext('2d');
            window.chartReceitaMensal = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: graficos.receita_mensal?.labels || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                    datasets: [{
                        label: 'Receita Mensal',
                        data: graficos.receita_mensal?.valores || [0, 0, 0, 0, 0, 0],
                        backgroundColor: '#28a745',
                        borderColor: '#28a745',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erro no gráfico receita mensal:', error);
        }
    }
    
    // Gráfico Concentração
    const canvasConcentracao = document.getElementById('chartConcentracao');
    if (canvasConcentracao) {
        try {
            // Verificar se existe E se tem o método destroy
            if (window.chartConcentracao && typeof window.chartConcentracao.destroy === 'function') {
                window.chartConcentracao.destroy();
            }
            
            const ctx = canvasConcentracao.getContext('2d');
            window.chartConcentracao = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: graficos.concentracao_clientes?.labels || ['Sem dados'],
                    datasets: [{
                        data: graficos.concentracao_clientes?.valores || [1],
                        backgroundColor: ['#28a745', '#20c997', '#17a2b8', '#ffc107', '#fd7e14', '#6c757d']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { boxWidth: 12 }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erro no gráfico concentração:', error);
        }
    }
    
    // Gráfico Tendência
    const canvasTendencia = document.getElementById('chartTendencia');
    if (canvasTendencia) {
        try {
            // Verificar se existe E se tem o método destroy
            if (window.chartTendencia && typeof window.chartTendencia.destroy === 'function') {
                window.chartTendencia.destroy();
            }
            
            const ctx = canvasTendencia.getContext('2d');
            window.chartTendencia = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: graficos.tendencia_linear?.labels || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                    datasets: [{
                        label: 'Tendência',
                        data: graficos.tendencia_linear?.valores_reais || [0, 0, 0, 0, 0, 0],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        } catch (error) {
            console.error('Erro no gráfico tendência:', error);
        }
    }
    
    // Gráfico Tempo Cobrança
    const canvasTempo = document.getElementById('chartTempoCobranca');
    if (canvasTempo) {
        try {
            // Verificar se existe E se tem o método destroy
            if (window.chartTempoCobranca && typeof window.chartTempoCobranca.destroy === 'function') {
                window.chartTempoCobranca.destroy();
            }
            
            const ctx = canvasTempo.getContext('2d');
            window.chartTempoCobranca = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: graficos.tempo_cobranca?.labels || ['0-30 dias', '31-60 dias', '61-90 dias', '90+ dias'],
                    datasets: [{
                        label: 'CTEs',
                        data: graficos.tempo_cobranca?.valores || [0, 0, 0, 0],
                        backgroundColor: '#17a2b8',
                        borderColor: '#17a2b8',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        } catch (error) {
            console.error('Erro no gráfico tempo cobrança:', error);
        }
    }
    
    console.log('✅ Gráficos criados com sucesso');
}

function criarGraficosVazios() {
    const graficosVazios = {
        receita_mensal: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            valores: [0, 0, 0, 0, 0, 0]
        },
        concentracao_clientes: {
            labels: ['Aguardando dados'],
            valores: [1]
        },
        tendencia_linear: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            valores_reais: [0, 0, 0, 0, 0, 0]
        },
        tempo_cobranca: {
            labels: ['0-30 dias', '31-60 dias', '61-90 dias', '90+ dias'],
            valores: [0, 0, 0, 0]
        }
    };
    
    criarGraficosCorrigidos(graficosVazios);
}

// ============================================================================
// GRÁFICOS DE EVOLUÇÃO - ADICIONAR AO FINAL DO ARQUIVO
// ============================================================================

// Função para carregar gráficos de evolução específicos
function carregarGraficosEvolucao() {
    console.log('📈 Carregando gráficos de evolução com canvas corretos...');
    
    const params = {
        filtro_dias: filtrosAtivos.periodo || 180
    };
    
    if (filtrosAtivos.cliente) {
        params.filtro_cliente = filtrosAtivos.cliente;
    }
    
    if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
        params.data_inicio = filtrosAtivos.dataInicio;
        params.data_fim = filtrosAtivos.dataFim;
    }
    
    // 1. Gráfico no canvas chartEvolucaoReceitaInclusaoFatura (que existe!)
    $.ajax({
        url: '/analise-financeira/api/evolucao-receita-inclusao-fatura',
        method: 'GET',
        data: params,
        success: function(response) {
            if (response.success && response.dados) {
                criarGraficoEvolucaoReceitaInclusaoFatura(response.dados);
            }
        },
        error: function() {
            console.log('⚠️ API evolução receita inclusão não disponível');
            // Criar gráfico vazio
            criarGraficoEvolucaoReceitaInclusaoFatura({
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                valores: [0, 0, 0, 0, 0, 0]
            });
        }
    });
    
    // 2. Gráfico no canvas chartReceitaComFaturas (que existe!)
    $.ajax({
        url: '/analise-financeira/api/receita-com-faturas',
        method: 'GET',
        data: params,
        success: function(response) {
            if (response.success && response.dados) {
                // Usar os dados diretos ou o campo grafico
                const dadosGrafico = response.dados.grafico || response.dados;
                criarGraficoReceitaComFaturasMensal(dadosGrafico);
            }
        },
        error: function() {
            console.log('⚠️ API receita com faturas não disponível');
            // Criar gráfico vazio
            criarGraficoReceitaComFaturasMensal({
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                valores: [0, 0, 0, 0, 0, 0]
            });
        }
    });
}

console.log('🔧 Correção aplicada - usando canvas que realmente existem');

// Gráfico: Evolução da Receita Faturada
function criarGraficoEvolucaoReceitaFaturada(dados) {
    const canvas = document.getElementById('chartEvolucaoReceitaFaturada');
    if (!canvas) {
        console.warn('Canvas chartEvolucaoReceitaFaturada não encontrado');
        return;
    }
    
    try {
        if (window.chartEvolucaoReceitaFaturada && typeof window.chartEvolucaoReceitaFaturada.destroy === 'function') {
            window.chartEvolucaoReceitaFaturada.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        window.chartEvolucaoReceitaFaturada = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dados.labels || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                datasets: [{
                    label: 'Receita Faturada',
                    data: dados.valores || [0, 0, 0, 0, 0, 0],
                    borderColor: '#6f42c1',
                    backgroundColor: 'rgba(111, 66, 193, 0.1)',
                    borderWidth: 3,
                    pointRadius: 5,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Evolução da Receita Faturada'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico evolução receita faturada criado');
    } catch (error) {
        console.error('❌ Erro no gráfico evolução receita faturada:', error);
    }
}

// Gráfico: Evolução Receita com Faturas (Data Inclusão)
function criarGraficoEvolucaoReceitaInclusaoFatura(dados) {
    const canvas = document.getElementById('chartEvolucaoReceitaInclusaoFatura');
    if (!canvas) {
        console.warn('Canvas chartEvolucaoReceitaInclusaoFatura não encontrado');
        return;
    }
    
    try {
        if (window.chartEvolucaoReceitaInclusaoFatura && typeof window.chartEvolucaoReceitaInclusaoFatura.destroy === 'function') {
            window.chartEvolucaoReceitaInclusaoFatura.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        window.chartEvolucaoReceitaInclusaoFatura = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dados.labels || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                datasets: [{
                    label: 'Receita por Data Inclusão',
                    data: dados.valores || [0, 0, 0, 0, 0, 0],
                    borderColor: '#e83e8c',
                    backgroundColor: 'rgba(232, 62, 140, 0.1)',
                    borderWidth: 3,
                    pointRadius: 5,
                    fill: true,
                    yAxisID: 'y'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Evolução Receita com Faturas (Data Inclusão)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        position: 'left',
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico evolução receita inclusão fatura criado');
    } catch (error) {
        console.error('❌ Erro no gráfico evolução receita inclusão fatura:', error);
    }
}

// LOCALIZAR e SUBSTITUIR a função criarGraficoReceitaComFaturasMensal por esta:

function criarGraficoReceitaComFaturasMensal(dados) {
    // Usar o canvas que realmente existe: chartReceitaComFaturas
    const canvas = document.getElementById('chartReceitaComFaturas');
    if (!canvas) {
        console.warn('Canvas chartReceitaComFaturas não encontrado');
        return;
    }
    
    try {
        // Destruir gráfico existente se houver
        if (window.chartReceitaComFaturas && typeof window.chartReceitaComFaturas.destroy === 'function') {
            window.chartReceitaComFaturas.destroy();
        }
        
        console.log('Criando gráfico mensal com dados:', dados);
        
        // Preparar dados com fallbacks
        let labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
        let valores = [0, 0, 0, 0, 0, 0];
        
        if (dados) {
            if (dados.labels && dados.valores) {
                labels = dados.labels;
                valores = dados.valores;
            } else if (dados.grafico && dados.grafico.labels) {
                labels = dados.grafico.labels;
                valores = dados.grafico.valores || valores;
            } else if (typeof dados === 'object' && !Array.isArray(dados)) {
                // Se dados é um objeto, tentar extrair valores
                const keys = Object.keys(dados);
                const vals = Object.values(dados);
                if (keys.length > 0 && vals.length > 0) {
                    labels = keys.slice(0, 6);
                    valores = vals.slice(0, 6).map(v => parseFloat(v) || 0);
                }
            }
        }
        
        const ctx = canvas.getContext('2d');
        window.chartReceitaComFaturas = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Receita com Faturas Mensal',
                    data: valores,
                    backgroundColor: '#fd7e14',
                    borderColor: '#fd7e14',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Evolução Receita com Faturas (Mensal)',
                        font: { size: 14, weight: 'bold' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Receita: R$ ${context.parsed.y.toLocaleString('pt-BR', { 
                                    minimumFractionDigits: 2, 
                                    maximumFractionDigits: 2 
                                })}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return 'R$ ' + (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return 'R$ ' + (value / 1000).toFixed(1) + 'K';
                                } else {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Gráfico receita com faturas mensal criado no canvas correto');
        
    } catch (error) {
        console.error('❌ Erro no gráfico receita com faturas mensal:', error);
    }
}


function atualizarTabelaClientes(topClientes) {
    const tbody = $('#tabelaTopClientes tbody');
    if (!tbody.length) return;
    
    tbody.empty();
    
    if (!topClientes || topClientes.length === 0) {
        tbody.append('<tr><td colspan="5" class="text-center text-muted">Nenhum cliente encontrado</td></tr>');
        return;
    }
    
    topClientes.forEach((cliente, index) => {
        const percentual = parseFloat(cliente.percentual || 0);
        let classeRisco = 'text-success';
        
        if (percentual >= 40) classeRisco = 'text-danger';
        else if (percentual >= 25) classeRisco = 'text-warning';
        
        tbody.append(`
            <tr>
                <td><strong>#${cliente.posicao || (index + 1)}</strong></td>
                <td>${cliente.nome.length > 30 ? cliente.nome.substring(0, 30) + '...' : cliente.nome}</td>
                <td><strong>${formatarMoedaSimples(cliente.receita || 0)}</strong></td>
                <td class="d-none d-sm-table-cell"><span class="${classeRisco}">${percentual.toFixed(1)}%</span></td>
                <td><span class="${classeRisco}">${cliente.risco || 'Baixo Risco'}</span></td>
            </tr>
        `);
    });
    
    console.log('✅ Tabela de clientes atualizada');
}

function configurarFiltrosData() {
    console.log('📅 Configurando filtros de data...');
    
    // Remover eventos existentes para evitar duplicação
    $('#dataInicio, #dataFim').off('change.filtroData');
    
    // Data Início
    $('#dataInicio').on('change.filtroData', function() {
        const valor = $(this).val();
        filtrosAtivos.dataInicio = valor || null;
        console.log('📅 Data início alterada para:', filtrosAtivos.dataInicio);
        
        // Atualizar status imediatamente
        atualizarStatusFiltroComDatas();
        
        // Se ambas as datas estão preenchidas, aplicar filtros
        if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
            console.log('🔄 Ambas as datas preenchidas - aplicando filtros automaticamente');
            carregarAnaliseCompleta();
        }
    });
    
    // Data Fim
    $('#dataFim').on('change.filtroData', function() {
        const valor = $(this).val();
        filtrosAtivos.dataFim = valor || null;
        console.log('📅 Data fim alterada para:', filtrosAtivos.dataFim);
        
        // Atualizar status imediatamente
        atualizarStatusFiltroComDatas();
        
        // Se ambas as datas estão preenchidas, aplicar filtros
        if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
            console.log('🔄 Ambas as datas preenchidas - aplicando filtros automaticamente');
            carregarAnaliseCompleta();
        }
    });
    
    // Botão Aplicar (se não estiver funcionando)
    $('#btnAplicarFiltros').off('click.filtroData').on('click.filtroData', function() {
        console.log('🔄 Aplicando filtros manualmente via botão');
        carregarAnaliseCompleta();
    });
    
    console.log('✅ Filtros de data configurados');
}

// Função para atualizar status incluindo datas
function atualizarStatusFiltroComDatas() {
    let status = `Período: ${filtrosAtivos.periodo || 180} dias`;
    
    if (filtrosAtivos.cliente) {
        status += ` | Cliente: ${filtrosAtivos.cliente}`;
    }
    
    if (filtrosAtivos.dataInicio && filtrosAtivos.dataFim) {
        status += ` | Período: ${filtrosAtivos.dataInicio} até ${filtrosAtivos.dataFim}`;
    } else if (filtrosAtivos.dataInicio) {
        status += ` | Início: ${filtrosAtivos.dataInicio}`;
    } else if (filtrosAtivos.dataFim) {
        status += ` | Fim: ${filtrosAtivos.dataFim}`;
    }
    
    $('#statusFiltro').text(status);
    console.log('🏷️ Status atualizado:', status);
}

function mostrarLoadingSimples() {
    if ($('#loadingAnalise').length) {
        $('#loadingAnalise').html(`
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-2">Carregando dados...</p>
            </div>
        `).show();
    }
}

function esconderLoadingSimples() {
    setTimeout(function() {
        $('#loadingAnalise').hide();
        const agora = new Date().toLocaleString('pt-BR');
        $('#ultimaAtualizacao').text(`Última atualização: ${agora}`);
    }, 1000);
}

function formatarMoedaSimples(valor) {
    const numero = parseFloat(valor) || 0;
    return numero.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

// Garantir que as variáveis existem
if (typeof filtrosAtivos === 'undefined') {
    window.filtrosAtivos = { 
        periodo: 180, 
        cliente: null 
    };
}

// Função de compatibilidade
function carregarTodasAsMetricas() {
    carregarDadosCorrigidos();
}

function aplicarFiltros() {
    carregarDadosCorrigidos();
}

// Função de debug simples
window.debugDashboard = function() {
    console.log('🔍 Debug Dashboard:');
    console.log('- jQuery:', typeof $ !== 'undefined');
    console.log('- Chart.js:', typeof Chart !== 'undefined');
    console.log('- Filtros:', filtrosAtivos);
    console.log('- Canvas encontrados:', ['chartReceitaMensal', 'chartConcentracao', 'chartTendencia', 'chartTempoCobranca'].map(id => document.getElementById(id) ? '✅' : '❌'));
    
    carregarDadosCorrigidos();
};

console.log('✅ Sistema corrigido carregado! Execute: debugDashboard() para testar');
console.log('🔧 Script de correção final carregado! Execute: debugSistemaCompleto() ou diagnosticarSistemaCompleto()');

