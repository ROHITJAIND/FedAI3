// ===== STATE MANAGEMENT =====
let autoScroll = true;
let chart = null;
let eventSource = null;

// Chart data
const chartData = {
    rounds: [],
    hospitalA_loss: [],
    hospitalA_acc: [],
    hospitalB_loss: [],
    hospitalB_acc: []
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    checkServerStatus();
    setupEventSource();
    
    // Check server status periodically
    setInterval(checkServerStatus, 5000);
});

// ===== SERVER STATUS =====
async function checkServerStatus() {
    const statusBadge = document.getElementById('serverStatus');
    const statusDot = statusBadge.querySelector('.status-dot');
    const statusText = statusBadge.querySelector('.status-text');
    
    try {
        const response = await fetch('http://localhost:8000/health', {
            method: 'GET',
            timeout: 2000
        });
        
        if (response.ok) {
            statusBadge.classList.add('connected');
            statusBadge.classList.remove('disconnected');
            statusText.textContent = 'Server Connected';
        } else {
            throw new Error('Server not responding');
        }
    } catch (error) {
        statusBadge.classList.add('disconnected');
        statusBadge.classList.remove('connected');
        statusText.textContent = 'Server Offline';
    }
}

// ===== TRAINING CONTROL =====
async function startTraining() {
    const startBtn = document.getElementById('startBtn');
    const rounds = parseInt(document.getElementById('rounds').value);
    const epochs = parseInt(document.getElementById('epochs').value);
    
    // Validate inputs
    if (rounds < 1 || epochs < 1) {
        addLog('Please enter valid configuration values', 'error');
        return;
    }
    
    // Disable button
    startBtn.disabled = true;
    startBtn.innerHTML = `
        <svg class="spinner" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="50" stroke-dashoffset="25"/>
        </svg>
        Training...
    `;
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rounds, epochs })
        });
        
        if (response.ok) {
            addLog('Training started successfully!', 'success');
            resetChartData();
        } else {
            const data = await response.json();
            addLog(`Failed to start training: ${data.error}`, 'error');
            resetStartButton();
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
        resetStartButton();
    }
}

function resetStartButton() {
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = false;
    startBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M5 3l12 7-12 7V3z"/>
        </svg>
        Start Training
    `;
}

// ===== SERVER-SENT EVENTS =====
function setupEventSource() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/api/events');
    
    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'log') {
                addLog(data.data.message, data.data.type);
            } else if (data.type === 'state') {
                updateState(data.data);
            }
        } catch (error) {
            console.error('Error parsing SSE data:', error);
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        // Will automatically reconnect
    };
}

// ===== STATE UPDATES =====
function updateState(state) {
    // Update progress
    const currentRound = state.current_round || 0;
    const totalRounds = state.total_rounds || 0;
    const progress = totalRounds > 0 ? (currentRound / totalRounds) * 100 : 0;
    
    document.getElementById('currentRound').textContent = `${currentRound} / ${totalRounds}`;
    document.querySelector('.progress-fill').style.width = `${progress}%`;
    document.getElementById('progressPercent').textContent = `${Math.round(progress)}%`;
    
    // Update active hospital
    const activeHospital = state.current_hospital || '-';
    document.getElementById('activeHospital').textContent = activeHospital === '-' ? '-' : `Hospital ${activeHospital}`;
    
    // Update hospital cards
    updateHospitalStatus('A', state.current_hospital === 'A');
    updateHospitalStatus('B', state.current_hospital === 'B');
    
    // Update metrics from history
    if (state.history && state.history.length > 0) {
        const latestA = state.history.filter(h => h.hospital === 'A').slice(-1)[0];
        const latestB = state.history.filter(h => h.hospital === 'B').slice(-1)[0];
        
        if (latestA) {
            document.getElementById('lossA').textContent = latestA.loss.toFixed(4);
            document.getElementById('accA').textContent = (latestA.accuracy * 100).toFixed(1) + '%';
        }
        
        if (latestB) {
            document.getElementById('lossB').textContent = latestB.loss.toFixed(4);
            document.getElementById('accB').textContent = (latestB.accuracy * 100).toFixed(1) + '%';
        }
        
        // Update chart
        updateChartFromHistory(state.history);
    }
    
    // Check if training is complete
    if (!state.is_running && state.current_round > 0) {
        resetStartButton();
    }
}

function updateHospitalStatus(hospital, isActive) {
    const statusElement = document.getElementById(`status${hospital}`);
    const cardElement = document.querySelector(`.hospital-${hospital.toLowerCase()}`);
    
    if (isActive) {
        statusElement.classList.add('training');
        statusElement.innerHTML = `
            <span class="status-indicator">●</span>
            <span>Training...</span>
        `;
        cardElement.classList.add('active');
    } else {
        statusElement.classList.remove('training');
        statusElement.innerHTML = `
            <span class="status-indicator">●</span>
            <span>Idle</span>
        `;
        cardElement.classList.remove('active');
    }
}

// ===== CHART MANAGEMENT =====
function initializeChart() {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Hospital A - Loss',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Hospital B - Loss',
                    data: [],
                    borderColor: '#ec4899',
                    backgroundColor: 'rgba(236, 72, 153, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Hospital A - Accuracy',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    yAxisID: 'y1'
                },
                {
                    label: 'Hospital B - Accuracy',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#cbd5e1',
                        font: {
                            size: 12,
                            family: 'Inter'
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                if (label.includes('Accuracy')) {
                                    label += (context.parsed.y * 100).toFixed(1) + '%';
                                } else {
                                    label += context.parsed.y.toFixed(4);
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(51, 65, 85, 0.5)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Inter'
                        }
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Loss',
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter',
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(51, 65, 85, 0.5)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Inter'
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Accuracy',
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter',
                            size: 12
                        }
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Inter'
                        },
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            }
        }
    });
}

function updateChartFromHistory(history) {
    const rounds = new Set();
    const dataByRound = {};
    
    history.forEach(entry => {
        rounds.add(entry.round);
        if (!dataByRound[entry.round]) {
            dataByRound[entry.round] = {};
        }
        dataByRound[entry.round][entry.hospital] = entry;
    });
    
    const sortedRounds = Array.from(rounds).sort((a, b) => a - b);
    
    chart.data.labels = sortedRounds.map(r => `Round ${r}`);
    chart.data.datasets[0].data = sortedRounds.map(r => dataByRound[r].A?.loss || null);
    chart.data.datasets[1].data = sortedRounds.map(r => dataByRound[r].B?.loss || null);
    chart.data.datasets[2].data = sortedRounds.map(r => dataByRound[r].A?.accuracy || null);
    chart.data.datasets[3].data = sortedRounds.map(r => dataByRound[r].B?.accuracy || null);
    
    chart.update('none');
}

function resetChartData() {
    chart.data.labels = [];
    chart.data.datasets.forEach(dataset => {
        dataset.data = [];
    });
    chart.update();
}

// ===== LOGGING =====
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('logContainer');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    
    logEntry.innerHTML = `
        <span class="log-time">${timestamp}</span>
        <span class="log-message">${message}</span>
    `;
    
    logContainer.appendChild(logEntry);
    
    // Auto-scroll to bottom if enabled
    if (autoScroll) {
        logContainer.scrollTop = logContainer.scrollHeight;
    }
    
    // Limit log entries to prevent memory issues
    while (logContainer.children.length > 200) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

function clearLogs() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '';
    addLog('Logs cleared', 'info');
}

function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const btn = document.getElementById('autoScrollBtn');
    btn.textContent = `Auto-scroll: ${autoScroll ? 'ON' : 'OFF'}`;
}

// ===== SPINNER ANIMATION =====
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinner {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
