// Dashboard Baker - Sistema de Métricas Avançadas
window.dashboardCharts = window.dashboardCharts || {};
window.dashboardMetricas = window.dashboardMetricas || {};
window.dashboardAlertas = window.dashboardAlertas || {};
window.dashboardVariacoes = window.dashboardVariacoes || {};

// Variáveis globais para armazenar dados
let metricas = {};
let alertas = {};
let variacoes = {};
let charts = {};

// Configurações dos gráficos
const chartColors = {
    primary: '#0f4c75',
    secondary: '#3282b8',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8'
};

// Função principal de inicialização
function inicializarDashboard() {
    console.log('[INIT] Inicializando Dashboard Baker...');
    carregarDashboard();
}

$(document).ready(function() {
    console.log('[INIT] Dashboard Baker carregado...');
    inicializarDashboard();
    
    // Auto-refresh a cada 5 minutos
    setInterval(carregarDashboard, 300000);
});

function carregarDashboard() {
    console.log('[DATA] Carregando dados do dashboard...');
    
    Promise.all([
        carregarMetricas(),
        carregarDadosGraficos()
    ]).then(() => {
        console.log('[OK] Dashboard carregado com sucesso!');
    }).catch(error => {
        console.error('❌ Erro ao carregar dashboard:', error);
        mostrarErro('Erro ao carregar dados do dashboard');
    });
}

// Adicionar no início do arquivo após as configurações
function testarDebug() {
    console.log('🐛 Testando API de debug...');
    
    $.ajax({
        url: '/dashboard/api/debug',
        method: 'GET',
        timeout: 10000
    }).done(function(response) {
        console.log('✅ Debug Response:', response);
        
        if (response.success) {
            alert(`
Debug Info:
- Total CTEs no DB: ${response.debug.total_ctes_db}
- Exemplos encontrados: ${response.debug.exemplos.length}
- Timestamp: ${response.debug.timestamp}
            `);
        } else {
            alert('❌ Erro no debug: ' + response.error);
        }
    }).fail(function(xhr) {
        console.error('❌ Erro AJAX Debug:', xhr);
        alert('❌ Erro na requisição de debug');
    });
}

// Atualizar a função carregarMetricas para mostrar mais debug
function carregarMetricas() {
    console.log('[DATA] Carregando métricas...');
    
    return $.ajax({
        url: '/dashboard/api/dashboard/metricas',
        method: 'GET',
        timeout: 30000
    }).done(function(response) {
        console.log('✅ Resposta das métricas:', response);
        
        if (response.success) {
            metricas = response.metricas;
            alertas = response.alertas;
            variacoes = response.variacoes;
            
            console.log('📈 Métricas carregadas:', metricas);
            console.log('🚨 Alertas carregados:', alertas);
            
            atualizarCardsMetricas();
            atualizarAlertas();
            atualizarVariacoes();
            atualizarTimestamp(response.timestamp);
            
            if (response.fallback) {
                console.log('⚠️ Usando fallback manual');
                mostrarAviso('Sistema em modo fallback - funcionalidade limitada');
            }
        } else {
            throw new Error(response.error);
        }
    }).fail(function(xhr) {
        console.error('❌ Erro ao carregar métricas:', xhr);
        mostrarErro('Erro ao carregar métricas: ' + (xhr.responseJSON?.error || xhr.statusText));
    });
}

function mostrarAviso(mensagem) {
    console.log('⚠️', mensagem);
    
    const toast = $(`
        <div class="toast align-items-center text-white bg-warning border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle"></i> ${mensagem}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    const bsToast = new bootstrap.Toast(toast[0], {delay: 5000});
    bsToast.show();
    
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function carregarDadosGraficos() {
    return $.ajax({
        url: '/dashboard/api/graficos',
        method: 'GET',
        timeout: 30000
    }).done(function(response) {
        if (response.success) {
            criarGraficos(response.graficos);
        } else {
            throw new Error(response.error);
        }
    });
}

function atualizarCardsMetricas() {
    // Verificar se métricas estão disponíveis
    if (!metricas) {
        console.warn('[WARN] Métricas não disponíveis');
        return;
    }

    // Cards principais
    $('#valorTotal').text(formatarMoeda(metricas.valor_total || 0));
    $('#totalCtes').text(formatarNumero(metricas.total_ctes || 0));
    $('#processosCompletos').text(formatarNumero(metricas.processos_completos || 0));

    // Calcular total de alertas com verificação
    let totalAlertas = 0;
    let valorRisco = 0;

    if (alertas && typeof alertas === 'object') {
        totalAlertas = Object.values(alertas).reduce((sum, alerta) => sum + (alerta.qtd || 0), 0);
        valorRisco = Object.values(alertas).reduce((sum, alerta) => sum + (alerta.valor || 0), 0);
    }

    $('#alertasAtivos').text(formatarNumero(totalAlertas));
    $('#valorRisco').text(formatarMoeda(valorRisco) + ' em risco');
    
    // Cards financeiros detalhados
    $('#receitaRealizada').text(formatarMoeda(metricas.valor_pago));
    $('#valorPendente').text(formatarMoeda(metricas.valor_pendente));
    $('#clientesAtivos').text(formatarNumero(metricas.clientes_unicos));
    $('#receitaMediaMensal').text(formatarMoeda(metricas.receita_mensal_media));
    
    // Subtítulos
    $('#crescimentoMensal').text(formatarPorcentagem(metricas.crescimento_mensal) + '% vs mês anterior');
    $('#ticketMedio').text('Ticket médio: ' + formatarMoeda(metricas.ticket_medio));
    $('#taxaConclusao').text(formatarPorcentagem(metricas.taxa_conclusao) + '% do total');
    $('#taxaPagamento').text(formatarPorcentagem(metricas.taxa_pagamento) + '% das faturas');
    $('#faturasPendentes').text(formatarNumero(metricas.faturas_pendentes) + ' faturas pendentes');
    $('#veiculosAtivos').text(formatarNumero(metricas.veiculos_ativos) + ' veículos');
}

function atualizarAlertas() {
    console.log('[ALERT] Atualizando sistema de alertas...');

    if (!alertas) {
        console.warn('[WARN] Alertas não disponíveis');
        return;
    }

    // Primeiro envio pendente
    const primeiroEnvio = alertas.primeiro_envio_pendente || {qtd: 0, valor: 0};
    $('#qtdPrimeiroEnvio').text(primeiroEnvio.qtd);
    $('#valorPrimeiroEnvio').text(formatarMoeda(primeiroEnvio.valor) + ' em risco');
    
    const cardPrimeiro = $('#alertaPrimeiroEnvio');
    if (primeiroEnvio.qtd > 0) {
        cardPrimeiro.removeClass('alert-success').addClass('alert-danger');
    } else {
        cardPrimeiro.removeClass('alert-danger').addClass('alert-success');
    }
    
    // Envio final pendente
    const envioFinal = alertas.envio_final_pendente || {qtd: 0, valor: 0};
    $('#qtdEnvioFinal').text(envioFinal.qtd);
    $('#valorEnvioFinal').text(formatarMoeda(envioFinal.valor) + ' pendentes');
    
    const cardEnvio = $('#alertaEnvioFinal');
    if (envioFinal.qtd > 0) {
        cardEnvio.removeClass('alert-success').addClass('alert-warning');
    } else {
        cardEnvio.removeClass('alert-warning').addClass('alert-success');
    }
    
    // Faturas vencidas - 🔧 FUNÇÃO COMPLETADA
    const faturasVencidas = alertas.faturas_vencidas || {qtd: 0, valor: 0};
    $('#qtdFaturasVencidas').text(faturasVencidas.qtd);
    $('#valorFaturasVencidas').text(formatarMoeda(faturasVencidas.valor) + ' inadimplentes');
    
    const cardVencidas = $('#alertaFaturasVencidas');
    if (faturasVencidas.qtd > 0) {
        cardVencidas.removeClass('alert-success').addClass('alert-danger');
    } else {
        cardVencidas.removeClass('alert-danger').addClass('alert-success');
    }
    
    // CTEs sem faturas (opcional - se houver card no HTML)
    const ctesSemFaturas = alertas.ctes_sem_faturas || {qtd: 0, valor: 0};
    if ($('#qtdCtesSemFaturas').length > 0) {
        $('#qtdCtesSemFaturas').text(ctesSemFaturas.qtd);
        $('#valorCtesSemFaturas').text(formatarMoeda(ctesSemFaturas.valor) + ' sem fatura');
        
        const cardSemFaturas = $('#alertaCtesSemFaturas');
        if (ctesSemFaturas.qtd > 0) {
            cardSemFaturas.removeClass('alert-success').addClass('alert-warning');
        } else {
            cardSemFaturas.removeClass('alert-warning').addClass('alert-success');
        }
    }
    
    // Log para debugging
    console.log('📊 Alertas atualizados:', {
        'primeiro_envio': primeiroEnvio.qtd,
        'envio_final': envioFinal.qtd,
        'faturas_vencidas': faturasVencidas.qtd,
        'ctes_sem_faturas': ctesSemFaturas.qtd
    });
    
    // Atualizar contador total de alertas
    const totalAlertas = primeiroEnvio.qtd + envioFinal.qtd + faturasVencidas.qtd + ctesSemFaturas.qtd;
    const valorTotalRisco = primeiroEnvio.valor + envioFinal.valor + faturasVencidas.valor + ctesSemFaturas.valor;
    
    // Atualizar cards de resumo se existirem
    if ($('#alertasAtivos').length > 0) {
        $('#alertasAtivos').text(formatarNumero(totalAlertas));
    }
    if ($('#valorRisco').length > 0) {
        $('#valorRisco').text(formatarMoeda(valorTotalRisco) + ' em risco');
    }
}

function atualizarVariacoes() {
    const container = $('#variacoesContainer');

    if (!variacoes || Object.keys(variacoes).length === 0) {
        container.html(`
            <div class="col-12 text-center">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    <strong>Dados insuficientes</strong><br>
                    Preencha as datas dos processos para calcular variações temporais
                </div>
            </div>
        `);
        return;
    }
    
    let html = '<div class="row">';
    
    Object.entries(variacoes).forEach(([codigo, dados]) => {
        const performanceClass = `performance-${dados.performance}`;
        const emoji = {
            'excelente': '🟢',
            'bom': '🔵',
            'atencao': '🟡',
            'critico': '🔴'
        }[dados.performance] || '⚪';
        
        html += `
            <div class="col-md-4 mb-3">
                <div class="variacao-card ${performanceClass}">
                    <h6 class="mb-2">${emoji} ${dados.nome}</h6>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="h4 mb-1">${dados.media} dias</div>
                            <small class="text-muted">Meta: ${dados.meta_dias} dias</small>
                        </div>
                        <div class="text-end">
                            <div class="badge bg-${dados.performance === 'excelente' ? 'success' : dados.performance === 'critico' ? 'danger' : 'warning'}">
                                ${dados.performance.toUpperCase()}
                            </div>
                            <div><small class="text-muted">${dados.qtd} registros</small></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.html(html);
}

function criarGraficos(dadosGraficos) {
    console.log('📈 Criando gráficos...', dadosGraficos);

    if (!dadosGraficos) {
        console.warn('[WARN] Dados dos gráficos não disponíveis');
        return;
    }

    if (dadosGraficos.erro) {
        console.error('Erro nos dados dos gráficos:', dadosGraficos.erro);
        return;
    }
    
    // 1. Evolução da receita mensal
    criarGraficoEvolucaoMensal(dadosGraficos.evolucao_mensal);
    
    // 2. Top clientes
    criarGraficoTopClientes(dadosGraficos.top_clientes);
    
    // 3. Distribuição de status
    criarGraficoStatusBaixas(dadosGraficos.distribuicao_status);
    
    // 4. Performance de veículos
    criarGraficoPerformanceVeiculos(dadosGraficos.performance_veiculos);
}

function criarGraficoEvolucaoMensal(dados) {
    console.log('📈 Criando gráfico evolução com dados:', dados);
    
    const canvas = document.getElementById('chartEvolucaoMensal');
    if (!canvas) {
        console.error('[ERROR] Canvas chartEvolucaoMensal não encontrado');
        return;
    }
    
    // VERIFICAÇÃO CRÍTICA DO CHART.JS
    if (typeof Chart === 'undefined') {
        console.error('[ERROR] ERRO: Chart.js não disponível ao criar gráfico');
        canvas.parentElement.innerHTML = `
            <div class="alert alert-danger text-center p-4">
                <h5>❌ Chart.js não carregado</h5>
                <p>Recarregue a página para tentar novamente</p>
                <button class="btn btn-primary" onclick="location.reload()">🔄 Recarregar</button>
            </div>
        `;
        return;
    }
    
    if (!dados || !dados.labels || dados.labels.length === 0) {
        console.warn('[WARN] Dados de evolução vazios ou inválidos');
        canvas.parentElement.innerHTML = '<p class="text-center text-muted p-4">Dados insuficientes para evolução mensal</p>';
        return;
    }
    
    try {
        console.log('[OK] Iniciando criação do gráfico com Chart.js');
        
        // Destruir gráfico anterior se existir
        if (charts.evolucaoMensal) {
            charts.evolucaoMensal.destroy();
        }
        
        charts.evolucaoMensal = new Chart(canvas, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Receita Mensal (R$)',
                    data: dados.valores,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
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
                                return 'Receita: R$ ' + context.parsed.y.toLocaleString('pt-BR');
                            }
                        }
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
        
        console.log('[OK] Gráfico evolução criado com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao criar gráfico evolução:', error);
        canvas.parentElement.innerHTML = `
            <div class="alert alert-danger text-center p-4">
                <h5>❌ Erro ao criar gráfico</h5>
                <p>Erro: ${error.message}</p>
                <button class="btn btn-primary" onclick="location.reload()">🔄 Tentar Novamente</button>
            </div>
        `;
    }
}

function criarGraficoTopClientes(dados) {
    console.log('👥 Criando gráfico clientes com dados:', dados);
    
    const canvas = document.getElementById('chartTopClientes');
    if (!canvas) {
        console.error('[ERROR] Canvas chartTopClientes não encontrado');
        return;
    }
    
    // VERIFICAÇÃO CRÍTICA DO CHART.JS
    if (typeof Chart === 'undefined') {
        console.error('[ERROR] ERRO: Chart.js não disponível ao criar gráfico');
        canvas.parentElement.innerHTML = `
            <div class="alert alert-danger text-center p-4">
                <h5>❌ Chart.js não carregado</h5>
                <p>Recarregue a página para tentar novamente</p>
                <button class="btn btn-primary" onclick="location.reload()">🔄 Recarregar</button>
            </div>
        `;
        return;
    }
    
    if (!dados || !dados.labels || dados.labels.length === 0) {
        console.warn('[WARN] Dados de clientes vazios ou inválidos');
        canvas.parentElement.innerHTML = '<p class="text-center text-muted p-4">Dados insuficientes para top clientes</p>';
        return;
    }
    
    try {
        console.log('[OK] Iniciando criação do gráfico clientes com Chart.js');
        
        // Destruir gráfico anterior se existir
        if (charts.topClientes) {
            charts.topClientes.destroy();
        }
        
        // Truncar nomes para display
        const labelsFormatados = dados.labels.map(label => 
            label.length > 30 ? label.substring(0, 30) + '...' : label
        );
        
        charts.topClientes = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labelsFormatados,
                datasets: [{
                    label: 'Receita por Cliente (R$)',
                    data: dados.valores,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: '#667eea',
                    borderWidth: 2,
                    borderRadius: 4
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
                            title: function(context) {
                                return dados.labels[context[0].dataIndex];
                            },
                            label: function(context) {
                                return 'Receita: R$ ' + context.parsed.y.toLocaleString('pt-BR');
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45
                        }
                    },
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
        
        console.log('[OK] Gráfico clientes criado com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao criar gráfico clientes:', error);
        canvas.parentElement.innerHTML = `
            <div class="alert alert-danger text-center p-4">
                <h5>❌ Erro ao criar gráfico</h5>
                <p>Erro: ${error.message}</p>
                <button class="btn btn-primary" onclick="location.reload()">🔄 Tentar Novamente</button>
            </div>
        `;
    }
}

function criarGraficoStatusBaixas(dados) {
    const ctx = document.getElementById('chartStatusBaixas');
    if (!ctx) return;
    
    if (charts.statusBaixas) {
        charts.statusBaixas.destroy();
    }
    
    const dadosBaixas = dados.baixas || {labels: [], valores: []};
    
    charts.statusBaixas = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: dadosBaixas.labels,
            datasets: [{
                data: dadosBaixas.valores,
                backgroundColor: [chartColors.success, chartColors.warning],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function criarGraficoPerformanceVeiculos(dados) {
    const ctx = document.getElementById('chartPerformanceVeiculos');
    if (!ctx) return;
    
    if (charts.performanceVeiculos) {
        charts.performanceVeiculos.destroy();
    }
    
    charts.performanceVeiculos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dados.labels || [],
            datasets: [{
                label: 'Receita (R$)',
                data: dados.valores || [],
                backgroundColor: chartColors.info,
                borderColor: chartColors.primary,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function atualizarDashboard() {
    console.log('🔄 Atualizando dashboard...');
    
    // Mostrar indicador de carregamento
    $('#ultimaAtualizacao').html('<i class="fas fa-sync-alt fa-spin"></i> Atualizando...');
    
    carregarDashboard();
}

function atualizarTimestamp(timestamp) {
    const data = new Date(timestamp);
    const dataFormatada = data.toLocaleString('pt-BR');
    $('#ultimaAtualizacao').text(`Última atualização: ${dataFormatada}`);
}

function mostrarErro(mensagem) {
    console.error('❌', mensagem);
    
    // Criar toast de erro
    const toast = $(`
        <div class="toast align-items-center text-white bg-danger border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle"></i> ${mensagem}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    // Adicionar ao body e mostrar
    $('body').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remover após fechar
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Funções utilitárias
function formatarMoeda(valor) {
    if (typeof valor !== 'number') valor = 0;
    return 'R$ ' + valor.toLocaleString('pt-BR', {minimumFractionDigits: 2});
}

function formatarNumero(valor) {
    if (typeof valor !== 'number') valor = 0;
    return valor.toLocaleString('pt-BR');
}

function formatarPorcentagem(valor) {
    if (typeof valor !== 'number') valor = 0;
    return valor.toFixed(1);
}