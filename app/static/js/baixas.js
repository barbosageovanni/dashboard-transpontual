// static/js/baixas.js - VERSÃO ATUALIZADA COM SUPORTE CSV E EXCEL

$(document).ready(function() {
    carregarEstatisticasBaixas();
    configurarEventos();
});

function configurarEventos() {
    // Form de baixa individual
    $('#formBaixaIndividual').on('submit', function(e) {
        e.preventDefault();
        registrarBaixaIndividual();
    });

    // Upload de arquivo com suporte a múltiplos formatos
    $('#fileInput').on('change', function() {
        const file = this.files[0];
        if (file) {
            validarArquivoAntesPorcessamento(file);
        }
    });

    // Drag and drop melhorado
    configurarDragAndDrop();

    // Definir data padrão como hoje
    $('#data_baixa').val(new Date().toISOString().split('T')[0]);
}

function configurarDragAndDrop() {
    const uploadArea = $('#uploadArea');
    
    uploadArea.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover border-success bg-light');
        $(this).find('i').removeClass('text-success').addClass('text-primary');
    });

    uploadArea.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover border-success bg-light');
        $(this).find('i').removeClass('text-primary').addClass('text-success');
    });

    uploadArea.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover border-success bg-light');
        $(this).find('i').removeClass('text-primary').addClass('text-success');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            $('#fileInput')[0].files = files;
            validarArquivoAntesPorcessamento(files[0]);
        }
    });
}

function validarArquivoAntesPorcessamento(file) {
    // Mostrar informações do arquivo
    mostrarInfoArquivo(file);
    
    // Validações básicas
    const extensoesPermitidas = ['.csv', '.xlsx', '.xls'];
    const extensao = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!extensoesPermitidas.includes(extensao)) {
        mostrarErro('❌ Formato não suportado. Use: CSV (.csv), Excel (.xlsx, .xls)');
        return false;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        mostrarErro('❌ Arquivo muito grande. Máximo: 50MB');
        return false;
    }
    
    // Se passou na validação, habilitar processamento
    $('#btnProcessarLote').prop('disabled', false).removeClass('btn-secondary').addClass('btn-primary');
    
    return true;
}

function mostrarInfoArquivo(file) {
    const tamanhoMB = (file.size / (1024 * 1024)).toFixed(2);
    const tipoArquivo = detectarTipoArquivo(file.name);
    
    const infoHtml = `
        <div class="alert alert-info mt-3" id="infoArquivo">
            <h6><i class="fas fa-file-alt"></i> Arquivo Selecionado</h6>
            <div class="row">
                <div class="col-md-6">
                    <strong>Nome:</strong> ${file.name}<br>
                    <strong>Tipo:</strong> ${tipoArquivo}
                </div>
                <div class="col-md-6">
                    <strong>Tamanho:</strong> ${tamanhoMB} MB<br>
                    <strong>Modificado:</strong> ${new Date(file.lastModified).toLocaleDateString('pt-BR')}
                </div>
            </div>
        </div>
    `;
    
    $('#infoArquivo').remove();
    $('#uploadArea').after(infoHtml);
}

function detectarTipoArquivo(nomeArquivo) {
    const extensao = nomeArquivo.split('.').pop().toLowerCase();
    
    switch(extensao) {
        case 'csv':
            return '📄 CSV (Comma Separated Values)';
        case 'xlsx':
            return '📊 Excel 2007+ (.xlsx)';
        case 'xls':
            return '📊 Excel 97-2003 (.xls)';
        default:
            return '❓ Formato desconhecido';
    }
}

function processarArquivoLote() {
    const file = $('#fileInput')[0].files[0];
    
    if (!file) {
        mostrarErro('⚠️ Selecione um arquivo primeiro');
        return;
    }
    
    // Validar novamente antes do processamento
    if (!validarArquivoAntesPorcessamento(file)) {
        return;
    }
    
    const formData = new FormData();
    formData.append('arquivo', file);

    // Esconder resultados anteriores e mostrar loading
    $('#resultadosLote').hide();
    mostrarLoadingProcessamento(file);
    
    // Desabilitar botão durante processamento
    $('#btnProcessarLote').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Processando...');

    $.ajax({
        url: '/baixas/api/lote',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        timeout: 300000, // 5 minutos
        success: function(response) {
            esconderLoading();
            
            if (response.sucesso) {
                mostrarResultadosLote(response.resultados);
                carregarEstatisticasBaixas(); // Atualizar estatísticas
                
                // Limpar formulário
                $('#fileInput').val('');
                $('#infoArquivo').remove();
                $('#btnProcessarLote').prop('disabled', true).removeClass('btn-primary').addClass('btn-secondary').html('<i class="fas fa-cogs"></i> Processar Arquivo');
                
            } else {
                mostrarErro('❌ ' + response.erro);
            }
        },
        error: function(xhr) {
            esconderLoading();
            const response = xhr.responseJSON;
            mostrarErro('❌ ' + (response ? response.erro : 'Erro ao processar arquivo'));
        }
    });
}

function mostrarLoadingProcessamento(file) {
    const tipoArquivo = detectarTipoArquivo(file.name);
    
    const loadingHtml = `
        <div class="text-center py-4" id="loadingProcessamento">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Processando...</span>
            </div>
            <h5><i class="fas fa-cogs"></i> Processando ${tipoArquivo}...</h5>
            <div class="progress mb-3" style="height: 6px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 100%"></div>
            </div>
            <p class="text-muted">
                📋 Validando estrutura do arquivo<br>
                🔍 Identificando CTEs no sistema<br>
                💾 Registrando baixas no banco de dados<br>
                <small class="text-warning">⏱️ Isso pode levar alguns minutos...</small>
            </p>
        </div>
    `;
    
    $('#resultadosLote').html(loadingHtml).show();
}

function esconderLoading() {
    $('#loadingProcessamento').remove();
    $('#btnProcessarLote').prop('disabled', false).html('<i class="fas fa-cogs"></i> Processar Arquivo');
}

function mostrarResultadosLote(resultados) {
    const arquivoInfo = resultados.arquivo_info;
    const detalhesProcessamento = arquivoInfo.detalhes_processamento;
    
    // Estatísticas principais
    const alertClass = resultados.erros > 0 ? 'alert-warning' : 'alert-success';
    const iconClass = resultados.erros > 0 ? 'fas fa-exclamation-triangle' : 'fas fa-check-circle';
    
    let resultadosHtml = `
        <div class="card mt-4">
            <div class="card-header bg-primary text-white">
                <h6><i class="fas fa-chart-line"></i> Resultados do Processamento</h6>
            </div>
            <div class="card-body">
                <!-- Informações do Arquivo -->
                <div class="alert alert-info">
                    <h6><i class="fas fa-file-alt"></i> Arquivo Processado</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Nome:</strong> ${arquivoInfo.nome}<br>
                            <strong>Tipo:</strong> ${arquivoInfo.tipo}
                        </div>
                        <div class="col-md-6">
                            <strong>Tamanho:</strong> ${arquivoInfo.tamanho_mb} MB<br>
                            <strong>Processado em:</strong> ${resultados.timestamp}
                        </div>
                    </div>
    `;
    
    // Detalhes específicos do tipo de arquivo
    if (detalhesProcessamento) {
        resultadosHtml += `<div class="mt-2"><small class="text-muted">`;
        
        if (arquivoInfo.tipo.includes('CSV')) {
            resultadosHtml += `Encoding: ${detalhesProcessamento.encoding_usado}, Separador: "${detalhesProcessamento.separador_usado}"`;
        } else if (arquivoInfo.tipo.includes('Excel')) {
            resultadosHtml += `Planilha: ${detalhesProcessamento.planilha_processada}`;
            if (detalhesProcessamento.planilhas_encontradas.length > 1) {
                resultadosHtml += ` (${detalhesProcessamento.planilhas_encontradas.length} planilhas encontradas)`;
            }
        }
        
        resultadosHtml += `</small></div>`;
    }
    
    resultadosHtml += `</div>`;
    
    // Estatísticas do processamento
    resultadosHtml += `
                <div class="${alertClass}">
                    <h6><i class="${iconClass}"></i> Estatísticas do Processamento</h6>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="mb-0">${resultados.processadas}</h4>
                                <small>Processadas</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center text-success">
                                <h4 class="mb-0">${resultados.sucessos}</h4>
                                <small>✅ Sucessos</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center text-danger">
                                <h4 class="mb-0">${resultados.erros}</h4>
                                <small>❌ Erros</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="mb-0">${Math.round((resultados.sucessos / resultados.processadas) * 100)}%</h4>
                                <small>Taxa de Sucesso</small>
                            </div>
                        </div>
                    </div>
                </div>
    `;
    
    // Detalhes por linha (limitado aos primeiros 50)
    if (resultados.detalhes && resultados.detalhes.length > 0) {
        resultadosHtml += `
                <div class="mt-3">
                    <h6><i class="fas fa-list"></i> Detalhes por Linha</h6>
                    <div class="table-responsive" style="max-height: 400px;">
                        <table class="table table-sm table-striped">
                            <thead class="table-dark">
                                <tr>
                                    <th width="80">Linha</th>
                                    <th width="100">CTE</th>
                                    <th width="80">Status</th>
                                    <th>Mensagem</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        // Mostrar apenas os primeiros 50 detalhes para não sobrecarregar a interface
        const detalhesLimitados = resultados.detalhes.slice(0, 50);
        
        detalhesLimitados.forEach(detalhe => {
            const statusIcon = detalhe.sucesso ? '✅' : '❌';
            const rowClass = detalhe.sucesso ? '' : 'table-warning';
            
            resultadosHtml += `
                <tr class="${rowClass}">
                    <td>${detalhe.linha}</td>
                    <td>${detalhe.cte}</td>
                    <td class="text-center">${statusIcon}</td>
                    <td>${detalhe.mensagem}</td>
                </tr>
            `;
        });
        
        resultadosHtml += `</tbody></table>`;
        
        if (resultados.detalhes.length > 50) {
            resultadosHtml += `
                <div class="alert alert-info mt-2">
                    <small><i class="fas fa-info-circle"></i> 
                    Mostrando primeiros 50 registros de ${resultados.detalhes.length} total.
                    </small>
                </div>
            `;
        }
        
        resultadosHtml += `</div></div>`;
    }
    
    resultadosHtml += `
            </div>
        </div>
    `;

    $('#resultadosLote').html(resultadosHtml).show();
    
    // Scroll suave para os resultados
    $('html, body').animate({
        scrollTop: $('#resultadosLote').offset().top - 20
    }, 500);
}

function mostrarErro(mensagem) {
    const erroHtml = `
        <div class="alert alert-danger mt-3" id="erroProcessamento">
            <h6><i class="fas fa-exclamation-circle"></i> Erro</h6>
            <p class="mb-0">${mensagem}</p>
        </div>
    `;
    
    $('#erroProcessamento').remove();
    $('#uploadArea').after(erroHtml);
    
    // Reabilitar botão
    $('#btnProcessarLote').prop('disabled', false).html('<i class="fas fa-cogs"></i> Processar Arquivo');
    
    // Remover erro após 5 segundos
    setTimeout(() => {
        $('#erroProcessamento').fadeOut();
    }, 5000);
}

// Funções para download de templates
function baixarTemplate(tipo) {
    const url = `/baixas/api/template/${tipo}`;
    
    // Criar link temporário para download
    const link = document.createElement('a');
    link.href = url;
    link.download = `template_baixas.${tipo === 'excel' ? 'xlsx' : 'csv'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Mostrar mensagem de sucesso
    const tipoNome = tipo === 'excel' ? 'Excel' : 'CSV';
    mostrarSucesso(`📥 Template ${tipoNome} baixado com sucesso!`);
}

function mostrarSucesso(mensagem) {
    const sucessoHtml = `
        <div class="alert alert-success mt-3" id="sucessoTemplate">
            <p class="mb-0">${mensagem}</p>
        </div>
    `;
    
    $('#sucessoTemplate').remove();
    $('#uploadArea').after(sucessoHtml);
    
    // Remover após 3 segundos
    setTimeout(() => {
        $('#sucessoTemplate').fadeOut();
    }, 3000);
}

// Funções existentes mantidas
function buscarCTE() {
    const numeroCte = $('#numero_cte').val();
    
    if (!numeroCte) {
        alert('Digite o número do CTE');
        return;
    }

    $.ajax({
        url: `/baixas/api/buscar-cte/${numeroCte}`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                mostrarInfoCTE(response.cte);
            } else {
                mostrarErroInfoCTE(response.message);
            }
        },
        error: function() {
            mostrarErroInfoCTE('Erro ao buscar CTE');
        }
    });
}

function mostrarInfoCTE(cte) {
    const html = `
        <div class="cte-info">
            <h6><i class="fas fa-info-circle"></i> Informações do CTE ${cte.numero_cte}</h6>
            <div class="row">
                <div class="col-md-6">
                    <strong>Cliente:</strong> ${cte.destinatario_nome || 'N/A'}
                </div>
                <div class="col-md-6">
                    <strong>Valor:</strong> R$ ${cte.valor_total.toFixed(2)}
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-6">
                    <strong>Data Emissão:</strong> ${cte.data_emissao ? new Date(cte.data_emissao).toLocaleDateString('pt-BR') : 'N/A'}
                </div>
                <div class="col-md-6">
                    <strong>Status:</strong> ${cte.has_baixa ? 'Baixado' : 'Pendente'}
                </div>
            </div>
        </div>
    `;
    
    $('#cteInfo').html(html).show();
}

function mostrarErroInfoCTE(mensagem) {
    const html = `
        <div class="cte-info error">
            <h6><i class="fas fa-exclamation-triangle"></i> Erro</h6>
            <p>${mensagem}</p>
        </div>
    `;
    
    $('#cteInfo').html(html).show();
}

function registrarBaixaIndividual() {
    const formData = {
        numero_cte: $('#numero_cte').val(),
        data_baixa: $('#data_baixa').val(),
        valor_baixa: $('#valor_baixa').val() || null,
        observacao: $('#observacao').val()
    };

    $.ajax({
        url: '/baixas/api/individual',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                alert('✅ ' + response.message);
                $('#formBaixaIndividual')[0].reset();
                $('#cteInfo').hide();
                carregarEstatisticasBaixas();
            } else {
                alert('❌ ' + response.message);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            alert('❌ ' + (response ? response.message : 'Erro ao registrar baixa'));
        }
    });
}

function carregarEstatisticasBaixas() {
    $.ajax({
        url: '/baixas/api/estatisticas',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                const stats = response.data;
                
                $('#totalBaixas').text(stats.total_baixas.toLocaleString());
                $('#valorBaixado').text('R$ ' + stats.valor_baixado.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }));
                $('#baixasPendentes').text(stats.baixas_pendentes.toLocaleString());
                $('#valorPendente').text('R$ ' + stats.valor_pendente.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }));
            }
        },
        error: function() {
            console.log('Erro ao carregar estatísticas');
        }
    });
}