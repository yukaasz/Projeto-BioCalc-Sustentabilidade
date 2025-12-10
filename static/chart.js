/**
 * Configurações e funções para gráficos do BioCalc
 */

// Cores padrão para os gráficos
const CORES_BIO = {
    primaria: '#2e7d32',
    secundaria: '#4caf50',
    acento: '#8bc34a',
    referencia: '#757575',
    alerta: '#ff9800',
    perigo: '#f44336'
};

/**
 * Cria gráfico de intensidade de carbono
 * @param {HTMLElement} canvasElement - Elemento canvas
 * @param {number} intensidade - Intensidade calculada
 * @param {string} metodo - Método ACV usado
 */
function criarGraficoIntensidade(canvasElement, intensidade, metodo) {
    const referencia = 83.8; // Intensidade de referência fóssil
    const ctx = canvasElement.getContext('2d');
    
    // Determina cor baseada no resultado
    let corBiocombustivel = intensidade < referencia ? CORES_BIO.primaria : CORES_BIO.perigo;
    
    // Se for método não reconhecido, usa cor de alerta
    if (metodo === 'CFF' || metodo === 'Zero-Burden') {
        corBiocombustivel = CORES_BIO.alerta;
    }
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Seu Biocombustível', 'Referência Fóssil'],
            datasets: [{
                label: 'Intensidade de Carbono',
                data: [intensidade, referencia],
                backgroundColor: [corBiocombustivel, CORES_BIO.referencia],
                borderColor: [corBiocombustivel + 'CC', CORES_BIO.referencia + 'CC'],
                borderWidth: 1,
                borderRadius: 5,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} gCO₂eq/MJ`;
                        },
                        afterLabel: function(context) {
                            if (context.dataIndex === 0 && metodo === 'CFF') {
                                return '⚠️ Método CFF não reconhecido pelo RenovaBio';
                            }
                            if (context.dataIndex === 0 && metodo === 'Zero-Burden') {
                                return '⚠️ Método Zero-Burden não reconhecido pelo RenovaBio';
                            }
                            return '';
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Comparação de Intensidade de Carbono',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'gCO₂eq/MJ',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Cria gráfico de pizza para distribuição das emissões
 * @param {HTMLElement} canvasElement - Elemento canvas
 * @param {Object} distribuicao - Objeto com distribuição das emissões
 */
function criarGraficoDistribuicao(canvasElement, distribuicao) {
    const ctx = canvasElement.getContext('2d');
    
    // Dados padrão se não for fornecido
    const dados = distribuicao || {
        biomassa: 40,
        transporte: 25,
        energia: 20,
        agua: 10,
        outros: 5
    };
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Biomassa', 'Transporte', 'Energia', 'Água', 'Outros'],
            datasets: [{
                data: [
                    dados.biomassa || 0,
                    dados.transporte || 0,
                    dados.energia || 0,
                    dados.agua || 0,
                    dados.outros || 0
                ],
                backgroundColor: [
                    CORES_BIO.primaria,
                    CORES_BIO.secundaria,
                    CORES_BIO.acento,
                    '#2196f3',
                    '#9c27b0'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Distribuição das Emissões',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

/**
 * Cria gráfico de linha para histórico de cálculos
 * @param {HTMLElement} canvasElement - Elemento canvas
 * @param {Array} historico - Array de cálculos históricos
 */
function criarGraficoHistorico(canvasElement, historico) {
    const ctx = canvasElement.getContext('2d');
    
    // Ordena por data
    const historicoOrdenado = historico.sort((a, b) => 
        new Date(a.data) - new Date(b.data)
    );
    
    const labels = historicoOrdenado.map(item => {
        const date = new Date(item.data);
        return date.toLocaleDateString('pt-BR');
    });
    
    const dados = historicoOrdenado.map(item => item.intensidade_carbono);
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Intensidade de Carbono (gCO₂eq/MJ)',
                data: dados,
                borderColor: CORES_BIO.primaria,
                backgroundColor: CORES_BIO.primaria + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: CORES_BIO.primaria,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
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
                title: {
                    display: true,
                    text: 'Evolução dos Cálculos',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'gCO₂eq/MJ'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            }
        }
    });
}


/**
 * Exporta gráfico como imagem PNG
 * @param {string} elementoId - ID do elemento canvas
 * @param {string} nomeArquivo - Nome do arquivo a ser baixado
 */
function exportarGraficoComoImagem(elementoId, nomeArquivo = 'grafico-biocalc') {
    const canvas = document.getElementById(elementoId);
    if (!canvas) {
        alert('Gráfico não encontrado!');
        return;
    }
    
    // Cria link para download
    const link = document.createElement('a');
    link.download = `${nomeArquivo}-${new Date().toISOString().slice(0,10)}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    
    // Feedback visual
    const botao = event?.target;
    if (botao) {
        const textoOriginal = botao.innerHTML;
        botao.innerHTML = '✅ Exportado!';
        botao.classList.add('btn-success');
        botao.classList.remove('btn-outline-secondary');
        
        setTimeout(() => {
            botao.innerHTML = textoOriginal;
            botao.classList.remove('btn-success');
            botao.classList.add('btn-outline-secondary');
        }, 2000);
    }
}

// Inicializa gráficos quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Procura por elementos canvas com data-attributes específicos
    document.querySelectorAll('[data-grafico="intensidade"]').forEach(canvas => {
        const intensidade = parseFloat(canvas.dataset.intensidade);
        const metodo = canvas.dataset.metodo;
        criarGraficoIntensidade(canvas, intensidade, metodo);
    });
    
    document.querySelectorAll('[data-grafico="distribuicao"]').forEach(canvas => {
        try {
            const distribuicao = JSON.parse(canvas.dataset.distribuicao);
            criarGraficoDistribuicao(canvas, distribuicao);
        } catch (e) {
            console.warn('Dados de distribuição inválidos:', e);
        }
    });
    
    document.querySelectorAll('[data-grafico="historico"]').forEach(canvas => {
        try {
            const historico = JSON.parse(canvas.dataset.historico);
            criarGraficoHistorico(canvas, historico);
        } catch (e) {
            console.warn('Dados históricos inválidos:', e);
        }
    });
});