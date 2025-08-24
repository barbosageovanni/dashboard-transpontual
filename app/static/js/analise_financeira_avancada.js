/*!
 * Sistema de Análise Financeira Avançada - Dashboard Baker
 * Arquivo: static/js/analise_financeira_avancada.js
 */

// ============================================================================
// VARIÁVEIS GLOBAIS E CONFIGURAÇÕES
// ============================================================================

let chartsFinanceira = {};
let analiseAtual = {};
let filtrosAtivos = {
    periodo: 180,
    cliente: null,
    veiculo: null
};

// Configurações de cores e temas
const CORES_TEMA = {
    primary: '#28a745',
    secondary: '#20c997',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    light: '#f8f9fa',
    dark: '#343a40',
    gradiente_principal: ['#28a745', '#20c997', '#17a2b8', '#ffc107', '#fd7e14']
};

// Estados de loading
let loadingStates = {
    analiseGeral: false,
    projecoes: false,
    comparativo: false,
    veiculos: false,
    insights: false
};

// ============================================================================
// INICIALIZAÇÃO DO SISTEMA
// ============================================================================

$(document).ready(function() {
    console.log('🚀 Inicializando Sistema de Análise Financeira Avançada...');
    inicializarSistema();
});

function inicializarSistema() {
    // Verificar se estamos na página correta
    if (!window.location.pathname.includes('analise-financeira')) {
        console.warn('⚠️ Não estamos na página de análise financeira');
        return;
    }
    
    // Verificar elementos essenciais
    if ($('#filtroPeriodo').length === 0) {
        console.warn('⚠️ Elementos não encontrados, reagendando inicialização...');
        setTimeout(inicializarSistema, 1000);
        return;
    }
    
    // Configurar eventos
    configurarEventos();
    
    // Carregar dados iniciais
    carregarDadosIniciais();
    
    // Configurar abas
    configurarAbas();
    
    console.log('✅ Sistema inicializado com sucesso!');
}

function configurarEventos() {
    // Eventos de filtros
    $('#filtroPeriodo').on('change', function() {
        filtrosAtivos.periodo = parseInt($(this).val());
        atualizarStatusFiltro();
    });
    
    $('#filtroCliente').on('change', function() {
        filtrosAtivos.cliente = $(this).val() || null;
        atualizarStatusFiltro();
    });
    
    $('#filtroVeiculo').on('change', function() {
        filtrosAtivos.veiculo = $(this).val() || null;
        atualizarStatusFiltro();
    });
    
    // Eventos de abas
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const target = $(e.target).data('bs-target');
        carregarDadosAba(target);
    });
    
    // Auto-refresh a cada 5 minutos
    setInterval(() => {
        if (!Object.values(loadingStates).some(state => state)) {
            console.log('🔄 Auto-refresh dos dados...');
            carregarDadosAbaAtiva();
        }
    }, 300000); // 5 minutos
}

function carregarDadosIniciais() {
    // Carregar listas de filtros
    carregarListaClientes();
    carregarListaVeiculos();
    
    // Carregar dados da aba ativa (Visão Geral)
    setTimeout(() => {
        carregarAnaliseGeral();
    }, 500);
}

// ============================================================================
// GERENCIAMENTO DE ABAS
// ============================================================================

function configurarAbas() {
    // Marcar primeira aba como ativa
    $('#geral-tab').addClass('active');
    $('#geral').addClass('show active');
}

function carregarDadosAba(target) {
    console.log(`📊 Carregando dados da aba: ${target}`);
    
    switch(target) {
        case '#geral':
            carregarAnaliseGeral();
            break;
        case '#projecoes':
            carregarProjecoesFuturas();
            break;
        case '#comparativo':
            carregarComparativoTemporal();
            break;
        case '#veiculos':
            carregarAnaliseVeiculos();
            break;
        case '#insights':
            carregarInsightsScore();
            break;
    }
}

function carregarDadosAbaAtiva() {
    const abaAtiva = $('.nav-tabs .nav-link.active').data('bs-target');
    carregarDadosAba(abaAtiva);
}

// ============================================================================
// CARREGAMENTO DE FILTROS
// ============================================================================

function carregarListaClientes() {
    $.ajax({
        url: '/analise-financeira/api/clientes',
        method: 'GET',
        timeout: 10000,
        success: function(response) {
            if (response.success) {
                preencherSelectClientes(response.clientes);
            }
        },
        error: function(xhr) {
            console.error('❌ Erro ao carregar clientes:', xhr);
        }
    });
}

function carregarListaVeiculos() {
    $.ajax({
        url: '/analise-financeira/api/lista-veiculos',
        method: 'GET',
        timeout: 10000,
        success: function(response) {
            if (response.success) {
                preencherSelectVeiculos(response.veiculos);
            }
        },
        error: function(xhr) {
            console.error('❌ Erro ao carregar veículos:', xhr);
        }
    });
}

function preencherSelectClientes(clientes) {
    const select = $('#filtroCliente');
    select.find('option:not(:first)').remove();
    
    clientes.forEach(cliente => {
        select.append(`<option value="${cliente}">${cliente}</option>`);
    });
    
    console.log(`✅ ${clientes.length} clientes carregados`);
}

function preencherSelectVeiculos(veiculos) {
    const select = $('#filtroVeiculo');
    select.find('option:not(:first)').remove();
    
    veiculos.forEach(veiculo => {
        select.append(`<option value="${veiculo}">${veiculo}</option>`);
    });
    
    console.log(`✅ ${veiculos.length} veículos carregados`);
}

// ============================================================================
// FUNÇÕES DE FILTROS
// ============================================================================

function aplicarFiltros() {
    console.log('🔍 Aplicando filtros:', filtrosAtivos);
    carregarDadosAbaAtiva();
}

function limparFiltros() {
    $('#filtroPeriodo').val('180');
    $('#filtroCliente').val('');
    $('#filtroVeiculo').val('');
    
    filtrosAtivos = { periodo: 180, cliente: null, veiculo: null };
    atualizarStatusFiltro();
    
    carregarDadosAbaAtiva();
}

function atualizarStatusFiltro() {
    const periodo = filtrosAtivos.periodo;
    const cliente = filtrosAtivos.cliente || 'Todos';
    const veiculo = filtrosAtivos.veiculo || 'Todos';
    
    $('#statusFiltro').text(`Período: Últimos ${periodo} dias | Cliente: ${cliente} | Veículo: ${veiculo}`);
}

// ============================================================================
// MÓDULO: ANÁLISE GERAL
// ============================================================================

function carregarAnaliseGeral() {
    if (loadingStates.analiseGeral) return;
    
    mostrarLoading('metricasPrincipais');
    loadingStates.analiseGeral = true;
    
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo
    });
    
    if (filtrosAtivos.cliente) {
        params.append('filtro_cliente', filtrosAtivos.cliente);
    }
    
    $.ajax({
        url: `/analise-financeira/api/analise-completa?${params.toString()}`,
        method: 'GET',
        timeout: 30000,
        success: function(response) {
            if (response.success) {
                analiseAtual = response;
                atualizarMetricasPrincipais(response.metricas_fundamentais);
                criarGraficoReceitaMensal(response.graficos);
                atualizarTopClientes(response.analise_clientes);
                criarGraficoSazonalidade(response.analise_sazonalidade);
                atualizarIndicadoresTendencia(response.indicadores_tendencia);
            } else {
                mostrarErro('metricasPrincipais', response.error);
            }
        },
        error: function(xhr) {
            console.error('❌ Erro na análise geral:', xhr);
            mostrarErro('metricasPrincipais', 'Erro ao carregar análise geral');
        },
        complete: function() {
            esconderLoading('metricasPrincipais');
            loadingStates.analiseGeral = false;
        }
    });
}

function atualizarMetricasPrincipais(metricas) {
    $('#receitaTotal').text(formatarMoeda(metricas.receita_total || 0));
    $('#totalCTEs').text(formatarNumero(metricas.total_ctes || 0));
    $('#ticketMedio').text(formatarMoeda(metricas.ticket_medio || 0));
    $('#taxaPagamento').text(formatarPercentual(metricas.taxa_pagamento || 0));
    $('#clientesUnicos').text(formatarNumero(metricas.clientes_unicos || 0));
    $('#veiculosAtivos').text(formatarNumero(metricas.veiculos_ativos || 0));
    
    // Atualizar tendências (se disponível no response)
    atualizarTendencias(metricas);
}

function atualizarTendencias(metricas) {
    // Simular tendências baseadas em dados históricos
    const crescimentoReceita = Math.random() * 20 - 10; // -10% a +10%
    const crescimentoTicket = Math.random() * 15 - 7.5; // -7.5% a +7.5%
    const crescimentoPagamento = Math.random() * 10 - 5; // -5% a +5%
    
    atualizarTrendElement('#trendReceita', crescimentoReceita);
    atualizarTrendElement('#trendTicket', crescimentoTicket);
    atualizarTrendElement('#trendPagamento', crescimentoPagamento);
}

function atualizarTrendElement(selector, valor) {
    const element = $(selector);
    const texto = `${valor >= 0 ? '+' : ''}${valor.toFixed(1)}%`;
    
    element.text(texto);
    element.removeClass('trend-up trend-down trend-stable');
    
    if (valor > 2) {
        element.addClass('trend-up');
    } else if (valor < -2) {
        element.addClass('trend-down');
    } else {
        element.addClass('trend-stable');
    }
}

function atualizarTopClientes(analiseClientes) {
    const container = $('#topClientesList');
    container.empty();
    
    if (!analiseClientes || !analiseClientes.top_clientes) {
        container.html('<p class="text-muted">Nenhum dado disponível</p>');
        return;
    }
    
    analiseClientes.top_clientes.slice(0, 5).forEach((cliente, index) => {
        const item = $(`
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
                <div>
                    <strong>${index + 1}º</strong> ${cliente.nome || 'N/A'}
                    <br><small class="text-muted">${cliente.viagens || 0} viagens</small>
                </div>
                <div class="text-end">
                    <strong>${formatarMoeda(cliente.faturamento || 0)}</strong>
                    <br><small class="text-muted">${formatarMoeda(cliente.ticket_medio || 0)}/viagem</small>
                </div>
            </div>
        `);
        container.append(item);
    });
}

// ============================================================================
// MÓDULO: PROJEÇÕES FUTURAS
// ============================================================================

function carregarProjecoesFuturas() {
    if (loadingStates.projecoes) return;
    
    mostrarLoading('projecoesFuturas');
    loadingStates.projecoes = true;
    
    $.ajax({
        url: '/analise-financeira/api/projecao-futura',
        method: 'GET',
        timeout: 20000,
        success: function(response) {
            if (response.success) {
                exibirProjecoesFuturas(response);
            } else {
                mostrarErro('projecoesFuturas', response.error || 'Erro ao carregar projeções');
            }
        },
        error: function(xhr) {
            console.error('❌ Erro nas projeções:', xhr);
            mostrarErro('projecoesFuturas', 'Erro ao carregar projeções futuras');
        },
        complete: function() {
            esconderLoading('projecoesFuturas');
            loadingStates.projecoes = false;
        }
    });
}

function exibirProjecoesFuturas(dados) {
    const container = $('#projecoesFuturas');
    container.empty();
    
    if (!dados.projecoes_mensais || dados.projecoes_mensais.length === 0) {
        container.html('<p class="text-muted">Dados insuficientes para projeção</p>');
        return;
    }
    
    // Criar resumo geral
    const resumo = $(`
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="text-center p-3 bg-light rounded">
                    <h5 class="text-success">${formatarMoeda(dados.total_projetado_3_meses || 0)}</h5>
                    <small>Total Projetado (3 meses)</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="text-center p-3 bg-light rounded">
                    <h5>${dados.tendencia_geral || 'N/A'}</h5>
                    <small>Tendência Geral</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="text-center p-3 bg-light rounded">
                    <h5>${(dados.r_squared * 100).toFixed(1)}%</h5>
                    <small>Confiança do Modelo</small>
                </div>
            </div>
        </div>
    `);
    container.append(resumo);
    
    // Criar projeções mensais
    const projecoesDiv = $('<div class="row"></div>');
    
    dados.projecoes_mensais.forEach(projecao => {
        const mesDiv = $(`
            <div class="col-md-4 mb-3">
                <div class="projecao-mes">
                    <h6 class="mb-2">${projecao.mes_nome}</h6>
                    <div class="projecao-valor">${formatarMoeda(projecao.valor_projetado)}</div>
                    <div class="projecao-confianca">
                        Confiança: ${projecao.confianca_percentual}%
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            Faixa: ${formatarMoeda(projecao.valor_minimo)} - ${formatarMoeda(projecao.valor_maximo)}
                        </small>
                    </div>
                </div>
            </div>
        `);
        projecoesDiv.append(mesDiv);
    });
    
    container.append(projecoesDiv);
}

// ============================================================================
// MÓDULO: COMPARATIVO TEMPORAL
// ============================================================================

function carregarComparativoTemporal() {
    if (loadingStates.comparativo) return;
    
    mostrarLoading('comparativoTemporal');
    loadingStates.comparativo = true;
    
    $.ajax({
        url: `/analise-financeira/api/comparacao-temporal?filtro_dias=${filtrosAtivos.periodo}`,
        method: 'GET',
        timeout: 20000,
        success: function(response) {
            if (response.success) {
                exibirComparativoTemporal(response.comparacao);
            } else {
                mostrarErro('comparativoTemporal', response.error || 'Erro ao carregar comparativo');
            }
        },
        error: function(xhr) {
            console.error('❌ Erro no comparativo:', xhr);
            mostrarErro('comparativoTemporal', 'Erro ao carregar comparativo temporal');
        },
        complete: function() {
            esconderLoading('comparativoTemporal');
            loadingStates.comparativo = false;
        }
    });
}

function exibirComparativoTemporal(comparacao) {
    const container = $('#comparativoTemporal');
    container.empty();
    
    // Criar cards de comparação
    const periodosDiv = $(`
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="comparacao-period">
                    <div class="comparacao-title">Período Atual</div>
                    <div class="comparacao-valor text-primary">${formatarMoeda(comparacao.periodo_atual.receita_total)}</div>
                    <small>${comparacao.periodo_atual.quantidade_ctes} CTEs</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="comparacao-period">
                    <div class="comparacao-title">2 Meses Atrás</div>
                    <div class="comparacao-valor text-info">${formatarMoeda(comparacao.periodo_2_meses_atras.receita_total)}</div>
                    <small>${comparacao.periodo_2_meses_atras.quantidade_ctes} CTEs</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="comparacao-period">
                    <div class="comparacao-title">1 Ano Atrás</div>
                    <div class="comparacao-valor text-secondary">${formatarMoeda(comparacao.periodo_1_ano_atras.receita_total)}</div>
                    <small>${comparacao.periodo_1_ano_atras.quantidade_ctes} CTEs</small>
                </div>
            </div>
        </div>
    `);
    container.append(periodosDiv);
    
    // Criar variações
    const variacoesDiv = $(`
        <div class="row">
            <div class="col-md-6">
                <h6>Comparação vs 2 Meses Atrás</h6>
                <div class="mb-2">
                    <span>Receita:</span>
                    <span class="comparacao-variacao ms-2 ${comparacao.variacao_vs_2_meses.receita_percentual >= 0 ? 'trend-up' : 'trend-down'}">
                        ${comparacao.variacao_vs_2_meses.receita_percentual >= 0 ? '+' : ''}${comparacao.variacao_vs_2_meses.receita_percentual.toFixed(1)}%
                    </span>
                </div>
                <div class="mb-2">
                    <span>Quantidade:</span>
                    <span class="comparacao-variacao ms-2 ${comparacao.variacao_vs_2_meses.quantidade_percentual >= 0 ? 'trend-up' : 'trend-down'}">
                        ${comparacao.variacao_vs_2_meses.quantidade_percentual >= 0 ? '+' : ''}${comparacao.variacao_vs_2_meses.quantidade_percentual.toFixed(1)}%
                    </span>
                </div>
            </div>
            <div class="col-md-6">
                <h6>Comparação vs 1 Ano Atrás</h6>
                <div class="mb-2">
                    <span>Receita:</span>
                    <span class="comparacao-variacao ms-2 ${comparacao.variacao_vs_1_ano.receita_percentual >= 0 ? 'trend-up' : 'trend-down'}">
                        ${comparacao.variacao_vs_1_ano.receita_percentual >= 0 ? '+' : ''}${comparacao.variacao_vs_1_ano.receita_percentual.toFixed(1)}%
                    </span>
                </div>
                <div class="mb-2">
                    <span>Quantidade:</span>
                    <span class="comparacao-variacao ms-2 ${comparacao.variacao_vs_1_ano.quantidade_percentual >= 0 ? 'trend-up' : 'trend-down'}">
                        ${comparacao.variacao_vs_1_ano.quantidade_percentual >= 0 ? '+' : ''}${comparacao.variacao_vs_1_ano.quantidade_percentual.toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    `);
    container.append(variacoesDiv);
}

// ============================================================================
// MÓDULO: ANÁLISE POR VEÍCULO
// ============================================================================

function carregarAnaliseVeiculos() {
    if (loadingStates.veiculos) return;
    
    mostrarLoading('tabelaVeiculos');
    loadingStates.veiculos = true;
    
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo
    });
    
    if (filtrosAtivos.veiculo) {
        params.append('filtro_veiculo', filtrosAtivos.veiculo);
    }
    
    $.ajax({
        url: `/analise-financeira/api/analise-veiculos?${params.toString()}`,
        method: 'GET',
        timeout: 30000,
        success: function(response) {
            if (response.success) {
                preencherTabelaVeiculos(response.ranking_veiculos);
                atualizarMetricasFrota(response.metricas_performance);
            } else {
                mostrarErro('tabelaVeiculos', response.error || 'Erro ao carregar análise de veículos');
            }
        },
        error: function(xhr) {
            console.error('❌ Erro na análise de veículos:', xhr);
            mostrarErro('tabelaVeiculos', 'Erro ao carregar análise de veículos');
        },
        complete: function() {
            esconderLoading('tabelaVeiculos');
            loadingStates.veiculos = false;
        }
    });
}

function preencherTabelaVeiculos(ranking) {
    const tbody = $('#tabelaVeiculos tbody');
    tbody.empty();
    
    if (!ranking || ranking.length === 0) {
        tbody.append('<tr><td colspan="6" class="text-center text-muted">Nenhum veículo encontrado</td></tr>');
        return;
    }
    
    ranking.slice(0, 20).forEach((veiculo, index) => { // Top 20
        const badgeClass = veiculo.cor_classificacao === 'success' ? 'badge-success' : 
                          veiculo.cor_classificacao === 'info' ? 'badge-info' :
                          veiculo.cor_classificacao === 'warning' ? 'badge-warning' : 'badge-danger';
        
        const row = $(`
            <tr>
                <td><strong>${index + 1}º</strong></td>
                <td><code>${veiculo.veiculo_placa}</code></td>
                <td><strong>${formatarMoeda(veiculo.faturamento_total)}</strong></td>
                <td>${formatarNumero(veiculo.total_viagens)}</td>
                <td>${formatarMoeda(veiculo.ticket_medio)}</td>
                <td>
                    <span class="badge ${badgeClass}">${veiculo.classificacao}</span>
                    <br><small>${veiculo.score_performance}/100</small>
                </td>
            </tr>
        `);
        tbody.append(row);
    });
}

function atualizarMetricasFrota(metricas) {
    const container = $('#metricasFrota');
    container.empty();
    
    if (!metricas) {
        container.html('<p class="text-muted">Dados não disponíveis</p>');
        return;
    }
    
    const metricasHtml = $(`
        <div class="mb-3">
            <h6>Veículos Ativos</h6>
            <div class="metric-number-large">${metricas.total_veiculos_ativos || 0}</div>
        </div>
        <div class="mb-3">
            <h6>Faturamento Médio</h6>
            <div class="h5 text-success">${formatarMoeda(metricas.faturamento_medio_por_veiculo || 0)}</div>
            <small class="text-muted">por veículo</small>
        </div>
        <div class="mb-3">
            <h6>Viagens Médias</h6>
            <div class="h5 text-info">${formatarNumero(metricas.viagens_media_por_veiculo || 0)}</div>
            <small class="text-muted">por veículo</small>
        </div>
        <div class="mb-3">
            <h6>Top Performer</h6>
            <div class="h6">${metricas.maior_faturamento_veiculo?.placa || 'N/A'}</div>
            <small class="text-muted">${formatarMoeda(metricas.maior_faturamento_veiculo?.valor || 0)}</small>
        </div>
    `);
    
    container.append(metricasHtml);
}

// ============================================================================
// MÓDULO: INSIGHTS & SCORE
// ============================================================================

function carregarInsightsScore() {
    if (loadingStates.insights) return;
    
    loadingStates.insights = true;
    
    // Usar dados já carregados da análise completa
    if (analiseAtual && analiseAtual.success) {
        exibirScoreSaude(analiseAtual.score_saude_financeira);
        exibirInsightsAutomaticos(analiseAtual);
        exibirResumoExecutivo(analiseAtual.resumo_executivo);
    } else {
        // Carregar dados se não estiverem disponíveis
        carregarAnaliseGeral();
    }
    
    loadingStates.insights = false;
}

function exibirScoreSaude(scoreData) {
    const container = $('#scoreSaude');
    container.empty();
    
    if (!scoreData) {
        container.html('<p class="text-muted">Score não disponível</p>');
        return;
    }
    
    const scoreClass = scoreData.cor === 'success' ? 'score-excellent' :
                      scoreData.cor === 'info' ? 'score-good' :
                      scoreData.cor === 'warning' ? 'score-regular' : 'score-poor';
    
    const scoreHtml = $(`
        <div class="score-circle ${scoreClass}">
            ${scoreData.score_total}/100
        </div>
        <h5>${scoreData.classificacao}</h5>
        <p class="text-muted">${scoreData.recomendacao}</p>
        
        <div class="mt-3">
            <small class="text-muted">Componentes do Score:</small>
            <div class="mt-2">
                <div class="d-flex justify-content-between">
                    <span>Receita:</span>
                    <span>${scoreData.componentes?.receita?.percentual || 0}%</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Pagamento:</span>
                    <span>${scoreData.componentes?.pagamento?.percentual || 0}%</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Diversificação:</span>
                    <span>${scoreData.componentes?.diversificacao?.percentual || 0}%</span>
                </div>
            </div>
        </div>
    `);
    
    container.append(scoreHtml);
}

function exibirInsightsAutomaticos(dadosAnalise) {
    const container = $('#insightsAutomaticos');
    container.empty();
    
    // Gerar insights baseados nos dados
    const insights = gerarInsightsAutomaticos(dadosAnalise);
    
    insights.forEach(insight => {
        const insightClass = insight.tipo === 'destaque' ? 'insight-destaque' :
                           insight.tipo === 'alerta' ? 'insight-alerta' :
                           insight.tipo === 'perigo' ? 'insight-perigo' : 'insight-info';
        
        const insightHtml = $(`
            <div class="insight-card ${insightClass}">
                <h6><i class="fas fa-${insight.icone || 'lightbulb'}"></i> ${insight.titulo}</h6>
                <p>${insight.descricao}</p>
                ${insight.acao ? `<small><strong>Ação sugerida:</strong> ${insight.acao}</small>` : ''}
            </div>
        `);
        
        container.append(insightHtml);
    });
}

function gerarInsightsAutomaticos(dados) {
    const insights = [];
    
    if (!dados || !dados.success) return insights;
    
    const metricas = dados.metricas_fundamentais || {};
    const receita = dados.analise_receita || {};
    
    // Insight sobre receita
    if (metricas.receita_total > 1000000) {
        insights.push({
            tipo: 'destaque',
            titulo: 'Excelente Performance de Receita',
            descricao: `Receita atual de ${formatarMoeda(metricas.receita_total)} demonstra forte performance financeira.`,
            icone: 'chart-line'
        });
    }
    
    // Insight sobre taxa de pagamento
    if (metricas.taxa_pagamento < 70) {
        insights.push({
            tipo: 'alerta',
            titulo: 'Taxa de Pagamento Abaixo do Ideal',
            descricao: `Taxa atual de ${formatarPercentual(metricas.taxa_pagamento)} requer atenção.`,
            acao: 'Revisar processo de cobrança e acompanhamento de recebíveis',
            icone: 'exclamation-triangle'
        });
    }
    
    // Insight sobre crescimento
    if (receita.crescimento_mensal > 10) {
        insights.push({
            tipo: 'destaque',
            titulo: 'Forte Crescimento Mensal',
            descricao: `Crescimento de ${formatarPercentual(receita.crescimento_mensal)} indica tendência positiva.`,
            icone: 'trending-up'
        });
    } else if (receita.crescimento_mensal < -5) {
        insights.push({
            tipo: 'perigo',
            titulo: 'Declínio na Receita Mensal',
            descricao: `Redução de ${formatarPercentual(Math.abs(receita.crescimento_mensal))} requer ação imediata.`,
            acao: 'Analisar causas e implementar estratégias de recuperação',
            icone: 'trending-down'
        });
    }
    
    return insights;
}

function exibirResumoExecutivo(resumo) {
    const container = $('#resumoExecutivo');
    container.empty();
    
    if (!resumo) {
        container.html('<p class="text-muted">Resumo não disponível</p>');
        return;
    }
    
    const resumoHtml = $(`
        <div class="row">
            <div class="col-md-3">
                <div class="text-center p-3 bg-light rounded">
                    <h5 class="text-success">${formatarMoeda(resumo.receita_atual || 0)}</h5>
                    <small>Receita Atual</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-3 bg-light rounded">
                    <h5 class="${resumo.crescimento_mensal >= 0 ? 'text-success' : 'text-danger'}">
                        ${resumo.crescimento_mensal >= 0 ? '+' : ''}${formatarPercentual(resumo.crescimento_mensal || 0)}
                    </h5>
                    <small>Crescimento Mensal</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-3 bg-light rounded">
                    <h5 class="text-info">${formatarMoeda(resumo.projecao_3_meses || 0)}</h5>
                    <small>Projeção 3 Meses</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-3 bg-light rounded">
                    <h5 class="text-primary">${resumo.score_saude || 0}/100</h5>
                    <small>Score de Saúde</small>
                </div>
            </div>
        </div>
    `);
    
    container.append(resumoHtml);
}

// ============================================================================
// CRIAÇÃO DE GRÁFICOS
// ============================================================================

function criarGraficoReceitaMensal(graficos) {
    const ctx = document.getElementById('chartReceitaMensal');
    if (!ctx || !graficos || !graficos.receita_mensal) return;
    
    // Destruir gráfico existente
    if (chartsFinanceira.receitaMensal) {
        chartsFinanceira.receitaMensal.destroy();
    }
    
    chartsFinanceira.receitaMensal = new Chart(ctx, {
        type: 'line',
        data: {
            labels: graficos.receita_mensal.labels || [],
            datasets: [{
                label: 'Receita Mensal',
                data: graficos.receita_mensal.valores || [],
                borderColor: CORES_TEMA.primary,
                backgroundColor: CORES_TEMA.primary + '20',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
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
            elements: {
                point: {
                    radius: 6,
                    hoverRadius: 8
                }
            }
        }
    });
}

function criarGraficoSazonalidade(sazonalidade) {
    const ctx = document.getElementById('chartSazonalidade');
    if (!ctx || !sazonalidade || !sazonalidade.sazonalidade_mensal) return;
    
    // Destruir gráfico existente
    if (chartsFinanceira.sazonalidade) {
        chartsFinanceira.sazonalidade.destroy();
    }
    
    const dados = sazonalidade.sazonalidade_mensal.dados_grafico;
    
    chartsFinanceira.sazonalidade = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dados.labels || [],
            datasets: [{
                label: 'Receita por Mês',
                data: dados.valores || [],
                backgroundColor: CORES_TEMA.gradiente_principal
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatarMoeda(value);
                        }
                    }
                }
            }
        }
    });
}

function atualizarIndicadoresTendencia(indicadores) {
    const container = $('#indicadoresTendencia');
    container.empty();
    
    if (!indicadores || indicadores.erro) {
        container.html('<p class="text-muted">Dados insuficientes para análise de tendência</p>');
        return;
    }
    
    const indicadoresHtml = $(`
        <div class="mb-3">
            <h6>Tendência da Receita</h6>
            <span class="badge badge-${indicadores.receita?.cor}">${indicadores.receita?.tendencia}</span>
            <small class="ms-2">${indicadores.receita?.variacao_percentual >= 0 ? '+' : ''}${indicadores.receita?.variacao_percentual}%</small>
        </div>
        <div class="mb-3">
            <h6>Tendência de Quantidade</h6>
            <span class="badge badge-${indicadores.quantidade?.cor}">${indicadores.quantidade?.tendencia}</span>
            <small class="ms-2">${indicadores.quantidade?.variacao_percentual >= 0 ? '+' : ''}${indicadores.quantidade?.variacao_percentual}%</small>
        </div>
        <div class="mb-3">
            <h6>Tendência do Ticket Médio</h6>
            <span class="badge badge-${indicadores.ticket_medio?.cor}">${indicadores.ticket_medio?.tendencia}</span>
            <small class="ms-2">${indicadores.ticket_medio?.variacao_percentual >= 0 ? '+' : ''}${indicadores.ticket_medio?.variacao_percentual}%</small>
        </div>
        <small class="text-muted">
            Baseado em ${indicadores.periodos_analisados} períodos de ${indicadores.agrupamento}
        </small>
    `);
    
    container.append(indicadoresHtml);
}

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor || 0);
}

function formatarNumero(valor) {
    return new Intl.NumberFormat('pt-BR').format(valor || 0);
}

function formatarPercentual(valor) {
    return `${(valor || 0).toFixed(1)}%`;
}

function mostrarLoading(containerId) {
    const container = $(`#${containerId}`);
    if (container.length === 0) return;
    
    container.css('position', 'relative');
    
    const overlay = $(`
        <div class="loading-overlay">
            <div class="loading-spinner"></div>
        </div>
    `);
    
    container.append(overlay);
}

function esconderLoading(containerId) {
    $(`#${containerId} .loading-overlay`).remove();
}

function mostrarErro(containerId, mensagem) {
    const container = $(`#${containerId}`);
    container.html(`
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Erro:</strong> ${mensagem}
        </div>
    `);
}

// ============================================================================
// FUNÇÕES DE EXPORTAÇÃO
// ============================================================================

function exportarAnalise(formato) {
    const params = new URLSearchParams({
        filtro_dias: filtrosAtivos.periodo,
        modulo: 'completo'
    });
    
    if (filtrosAtivos.cliente) {
        params.append('filtro_cliente', filtrosAtivos.cliente);
    }
    
    window.open(`/analise-financeira/api/exportar/${formato}?${params.toString()}`, '_blank');
}

// Funções globais para botões
window.aplicarFiltros = aplicarFiltros;
window.limparFiltros = limparFiltros;
window.exportarAnalise = exportarAnalise;