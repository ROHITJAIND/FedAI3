// ===== HOSPITAL INTERFACE APP =====

let autoScroll = true;
let chart = null;
let eventSource = null;
let hospitalState = {};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    loadInitialState();
    setupEventSource();
    checkServerStatus();
    
    // Periodic server check
    setInterval(checkServerStatus, 5000);
});

// ===== LOAD INITIAL STATE =====
async function loadInitialState() {
    try {
        const response = await fetch('/api/state');
        const state = await response.json();
        hospitalState = state;
        updateUIFromState(state);
    } catch (error) {
        console.error('Error loading state:', error);
    }
}

// ===== SERVER STATUS CHECK =====
async function checkServerStatus() {
    const statusElement = document.getElementById('serverStatus');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('.status-text');
    
    try {
        const response = await fetch('http://localhost:8000/health', {
            method: 'GET',
            timeout: 2000
        });
        
        if (response.ok) {
            statusElement.classList.add('connected');
            statusElement.classList.remove('disconnected');
            statusText.textContent = 'Server Connected';
        } else {
            throw new Error('Server not responding');
        }
    } catch (error) {
        statusElement.classList.add('disconnected');
        statusElement.classList.remove('connected');
        statusText.textContent = 'Server Offline';
    }
}

// ===== ACTION FUNCTIONS =====
async function downloadGlobal() {
    const btn = document.getElementById('downloadBtn');
    const progressWrapper = document.getElementById('downloadProgressWrapper');
    const progressBar = document.getElementById('downloadProgress');
    const progressText = document.getElementById('downloadProgressText');
    
    btn.disabled = true;
    btn.style.display = 'none';
    progressWrapper.style.display = 'block';
    
    // Start progress animation
    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
            progressText.textContent = Math.round(progress) + '%';
        }
    }, 200);
    
    // Store interval ID globally so we can complete it later
    window.downloadProgressInterval = progressInterval;
    
    try {
        const response = await fetch('/api/download-global', {
            method: 'POST'
        });
        
        if (response.ok) {
            addLog('Download started...', 'info');
        } else {
            const data = await response.json();
            addLog(`Error: ${data.error}`, 'error');
            completeDownloadProgress(false);
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
        completeDownloadProgress(false);
    }
}

function completeDownloadProgress(success = true) {
    const btn = document.getElementById('downloadBtn');
    const progressWrapper = document.getElementById('downloadProgressWrapper');
    const progressBar = document.getElementById('downloadProgress');
    const progressText = document.getElementById('downloadProgressText');
    
    if (window.downloadProgressInterval) {
        clearInterval(window.downloadProgressInterval);
    }
    
    if (success) {
        // Complete the progress
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        setTimeout(() => {
            progressWrapper.style.display = 'none';
            progressBar.style.width = '0%';
            progressText.textContent = '0%';
            btn.style.display = 'flex';
            btn.disabled = false;
        }, 1000);
    } else {
        // Reset on error
        setTimeout(() => {
            progressWrapper.style.display = 'none';
            progressBar.style.width = '0%';
            progressText.textContent = '0%';
            btn.style.display = 'flex';
            btn.disabled = false;
        }, 500);
    }
}

async function startTraining() {
    const btn = document.getElementById('trainBtn');
    const epochs = parseInt(document.getElementById('epochs').value);
    
    if (epochs < 1) {
        addLog('Please enter valid number of epochs', 'error');
        return;
    }
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Training...';
    
    try {
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ epochs })
        });
        
        if (response.ok) {
            addLog(`Training started for ${epochs} epochs`, 'info');
        } else {
            const data = await response.json();
            addLog(`Error: ${data.error}`, 'error');
            btn.disabled = false;
            btn.innerHTML = 'Start Training';
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
        btn.disabled = false;
        btn.innerHTML = 'Start Training';
    }
}

async function pushToGlobal() {
    const btn = document.getElementById('pushBtn');
    const progressWrapper = document.getElementById('pushProgressWrapper');
    const progressBar = document.getElementById('pushProgress');
    const progressText = document.getElementById('pushProgressText');
    
    btn.disabled = true;
    btn.style.display = 'none';
    progressWrapper.style.display = 'block';
    
    // Start progress animation
    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 12;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
            progressText.textContent = Math.round(progress) + '%';
        }
    }, 250);
    
    // Store interval ID globally so we can complete it later
    window.pushProgressInterval = progressInterval;
    
    try {
        const response = await fetch('/api/push-global', {
            method: 'POST'
        });
        
        if (response.ok) {
            addLog('Pushing weights to global model...', 'info');
        } else {
            const data = await response.json();
            addLog(`Error: ${data.error}`, 'error');
            completePushProgress(false);
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
        completePushProgress(false);
    }
}

function completePushProgress(success = true) {
    const btn = document.getElementById('pushBtn');
    const progressWrapper = document.getElementById('pushProgressWrapper');
    const progressBar = document.getElementById('pushProgress');
    const progressText = document.getElementById('pushProgressText');
    
    if (window.pushProgressInterval) {
        clearInterval(window.pushProgressInterval);
    }
    
    if (success) {
        // Complete the progress
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        setTimeout(() => {
            progressWrapper.style.display = 'none';
            progressBar.style.width = '0%';
            progressText.textContent = '0%';
            btn.style.display = 'flex';
            btn.disabled = false;
        }, 1000);
    } else {
        // Reset on error
        setTimeout(() => {
            progressWrapper.style.display = 'none';
            progressBar.style.width = '0%';
            progressText.textContent = '0%';
            btn.style.display = 'flex';
            btn.disabled = false;
        }, 500);
    }
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
                hospitalState = data.data;
                updateUIFromState(data.data);
            }
        } catch (error) {
            console.error('Error parsing SSE data:', error);
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
    };
}

// ===== UPDATE UI FROM STATE =====
function updateUIFromState(state) {
    // Training status
    const trainingStatus = document.getElementById('trainingStatus');
    const trainBtn = document.getElementById('trainBtn');
    
    if (state.is_training) {
        trainingStatus.classList.add('training');
        trainingStatus.querySelector('.status-icon').textContent = '⚙️';
        trainingStatus.querySelector('.status-label').textContent = 'Training';
        trainBtn.disabled = true;
        trainBtn.innerHTML = '<span class="spinner"></span> Training...';
    } else {
        trainingStatus.classList.remove('training');
        trainingStatus.querySelector('.status-icon').textContent = '⏸';
        trainingStatus.querySelector('.status-label').textContent = 'Idle';
        trainBtn.disabled = false;
        trainBtn.innerHTML = 'Start Training';
    }
    
    // Model status
    const modelStatus = document.getElementById('modelStatus');
    if (state.model_exists) {
        modelStatus.textContent = '✓ Trained';
        modelStatus.style.color = 'var(--success)';
    } else {
        modelStatus.textContent = 'Not Trained';
        modelStatus.style.color = 'var(--text-muted)';
    }
    
    // Global model status
    const globalStatus = document.getElementById('globalStatus');
    if (state.global_model_downloaded) {
        globalStatus.textContent = '✓ Downloaded';
        globalStatus.style.color = 'var(--success)';
    } else {
        globalStatus.textContent = 'Not Downloaded';
        globalStatus.style.color = 'var(--text-muted)';
    }
    
    // Metrics
    if (state.latest_metrics) {
        const loss = state.latest_metrics.loss;
        const acc = state.latest_metrics.accuracy;
        
        if (loss > 0) {
            document.getElementById('currentLoss').textContent = loss.toFixed(4);
            const lossPercent = Math.max(0, Math.min(100, (1 - loss) * 100));
            document.getElementById('lossFill').style.width = `${lossPercent}%`;
        }
        
        if (acc > 0) {
            document.getElementById('currentAcc').textContent = (acc * 100).toFixed(1) + '%';
            document.getElementById('accFill').style.width = `${acc * 100}%`;
        }
    }
    
    // Progress
    const current = state.current_epoch || 0;
    const total = state.total_epochs || 0;
    document.getElementById('epochProgress').textContent = `${current} / ${total}`;
    
    if (total > 0) {
        const progress = (current / total) * 100;
        document.getElementById('trainingProgress').style.width = `${progress}%`;
    } else {
        document.getElementById('trainingProgress').style.width = '0%';
    }
    
    // Update chart
    if (state.training_history && state.training_history.loss) {
        updateChart(state.training_history);
    }
}

// ===== CHART MANAGEMENT =====
function initializeChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Loss',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Accuracy',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
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
                            family: 'Inter'
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(51, 65, 85, 0.5)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Loss',
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(51, 65, 85, 0.5)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Accuracy',
                        color: '#cbd5e1'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            }
        }
    });
}

function updateChart(history) {
    const epochs = history.loss.length;
    chart.data.labels = Array.from({length: epochs}, (_, i) => `Epoch ${i + 1}`);
    chart.data.datasets[0].data = history.loss;
    chart.data.datasets[1].data = history.accuracy;
    chart.update('none');
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
    
    if (autoScroll) {
        logContainer.scrollTop = logContainer.scrollHeight;
    }
    
    // Check for completion messages
    if (message.includes('Global model downloaded successfully')) {
        completeDownloadProgress(true);
    } else if (message.includes('No global model available yet')) {
        completeDownloadProgress(false);
    } else if (message.includes('Cannot download global model')) {
        completeDownloadProgress(false);
    } else if (message.includes('Global model updated successfully')) {
        completePushProgress(true);
    } else if (message.includes('Failed to update global model')) {
        completePushProgress(false);
    } else if (message.includes('Failed to upload weights')) {
        completePushProgress(false);
    }
    
    // Limit log entries
    while (logContainer.children.length > 200) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

function clearLogs() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '';
    addLog(`Hospital ${HOSPITAL_ID} logs cleared`, 'info');
}

function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const btn = document.getElementById('autoScrollBtn');
    btn.textContent = `Auto-scroll: ${autoScroll ? 'ON' : 'OFF'}`;
}

// ===== PDF UPLOAD AND ANALYSIS =====
async function uploadPDF() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];
    const statusDiv = document.getElementById('uploadStatus');
    
    if (!file) {
        statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ No file selected</span>';
        return;
    }
    
    if (file.type !== 'application/pdf') {
        statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Please select a PDF file</span>';
        return;
    }
    
    statusDiv.innerHTML = '<span style="color: #3498db;">⏳ Uploading and analyzing...</span>';
    addLog(`Uploading PDF: ${file.name}`, 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload-pdf', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            statusDiv.innerHTML = '<span style="color: #27ae60;">✅ Upload successful! AI is analyzing...</span>';
            addLog(`PDF uploaded successfully: ${file.name}`, 'success');
            addLog('Gemini AI is analyzing the report...', 'info');
            
            // Reset file input
            fileInput.value = '';
            
            // Show success message
            setTimeout(() => {
                statusDiv.innerHTML = '<span style="color: #27ae60;">✅ Analysis complete! Check reports below.</span>';
            }, 2000);
        } else {
            const error = await response.json();
            statusDiv.innerHTML = `<span style="color: #e74c3c;">❌ Error: ${error.error}</span>`;
            addLog(`PDF upload failed: ${error.error}`, 'error');
        }
    } catch (error) {
        statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Upload failed. Check connection.</span>';
        addLog(`PDF upload error: ${error.message}`, 'error');
    }
}

async function viewReports() {
    const reportsDiv = document.getElementById('reportsList');
    reportsDiv.innerHTML = '<p style="color: #95a5a6;">Loading reports...</p>';
    
    try {
        const response = await fetch('/api/reports');
        const data = await response.json();
        
        if (data.reports && data.reports.length > 0) {
            // Sort by creation time (newest first) and show only the most recent
            const sortedReports = data.reports.sort((a, b) => b.created - a.created);
            const latestReport = sortedReports[0];
            
            const date = new Date(latestReport.created * 1000).toLocaleString();
            const sizeKB = (latestReport.size / 1024).toFixed(1);
            
            reportsDiv.innerHTML = `
                <div style="font-size: 12px;">
                    <div style="padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; border-left: 3px solid #667eea;">
                        <strong>${latestReport.filename}</strong><br>
                        <small style="color: #666;">📅 ${date} | 📊 ${sizeKB} KB</small><br>
                        <a href="/api/download-report/${latestReport.filename}" 
                           style="color: #667eea; text-decoration: none; font-weight: 500;"
                           download>
                           ⬇️ Download Latest Report
                        </a>
                    </div>
                </div>
            `;
            addLog(`Latest analysis report ready`, 'success');
        } else {
            reportsDiv.innerHTML = '<p style="color: #95a5a6; font-size: 12px;">No reports yet. Upload a PDF to generate one!</p>';
        }
    } catch (error) {
        reportsDiv.innerHTML = '<p style="color: #e74c3c; font-size: 12px;">❌ Failed to load reports</p>';
        addLog(`Error loading reports: ${error.message}`, 'error');
    }
}
