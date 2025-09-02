// Teste de sintaxe
const chartColorsFinanceira = {
    primary: '#28a745'
};

function formatarMoeda(valor) {
    return 'R$ ' + valor.toFixed(2);
}

function formatarMoedaCompacta(valor) {
    return 'R$ ' + valor.toFixed(0);
}

function criarGraficoReceitaMensal(dados) {
    const canvas = document.getElementById('chartReceitaMensal');
    if (!canvas) return;
    
    try {
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
