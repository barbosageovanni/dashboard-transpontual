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

// SUBSTITUIR FUNÇÃO PRINCIPAL DE INICIALIZAÇÃO
function inicializarDashboardCompletoCorrigido() {
    console.log('🚀 Inicializando Dashboard Financeiro com Correção...');
    
    if (!window.location.pathname.includes('analise-financeira')) {
        console.warn('Não estamos na página de análise financeira');
        return;
    }
    
    // Aguardar elementos DOM
    if ($('#filtroPeriodo').length === 0) {
        console.log('⏳ Aguardando elementos DOM...');
        setTimeout(inicializarDashboardCompletoCorrigido, 1000);
        return;
    }
    
    configurarEventos();
    carregarListaClientes();
    
    // Iniciar diagnóstico e correção
    setTimeout(() => {
        diagnosticarECorrigir();
    }, 1000);
}

// COMPATIBILIDADE COM FUNÇÃO EXISTENTE
function inicializarDashboardCompleto() {
    inicializarDashboardCompletoCorrigido();
}

function inicializarAnaliseFinanceira() {
    inicializarDashboardCompletoCorrigido();
}

// FUNÇÃO DE DEBUG AVANÇADO
window.debugSistemaCompleto = function() {
    console.log('🔍 === DEBUG SISTEMA COMPLETO ===');
    
    // Verificar bibliotecas
    console.log('jQuery:', typeof $ !== 'undefined' ? '✅' : '❌');
    console.log('Chart.js:', typeof Chart !== 'undefined' ? '✅' : '❌');
    
    // Verificar elementos DOM
    console.log('Filtro Período:', $('#filtroPeriodo').length > 0 ? '✅' : '❌');
    console.log('Canvas Gráficos:', [
        'chartReceitaMensal',
        'chartConcentracao', 
        'chartTendencia',
        'chartTempoCobranca'
    ].map(id => `${id}: ${document.getElementById(id) ? '✅' : '❌'}`));
    
    // Testar APIs
    console.log('🔍 Testando APIs...');
    const apis = [
        '/analise-financeira/api/test-conexao',
        '/analise-financeira/api/debug/base-dados',
        '/analise-financeira/api/metricas-forcadas',
        '/analise-financeira/api/graficos-simples'
    ];
    
    apis.forEach(api => {
        fetch(api)
            .then(r => r.json())
            .then(data => console.log(`${api}:`, data.success ? '✅' : '❌', data))
            .catch(err => console.log(`${api}:`, '❌', err.message));
    });
    
    // Executar diagnóstico
    setTimeout(() => {
        console.log('🔧 Executando diagnóstico automático...');
        diagnosticarECorrigir();
    }, 2000);
};

console.log('🔧 Script de correção final carregado! Execute: debugSistemaCompleto()');