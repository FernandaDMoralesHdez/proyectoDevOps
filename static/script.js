// Global variables
let isRunning = true;
let interval;
let temperatures = [];
let timestamps = [];
let chart;
let alertList = [];
let hasNewAlert = false;
let metricsChart;

// Chart initialization function
function initializeCharts() {
    const ctx = document.getElementById("temperatureChart").getContext("2d");
    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: timestamps,
            datasets: [{
                label: "Temperatura (°C)",
                data: temperatures,
                borderColor: "rgb(226, 105, 172)",
                backgroundColor: "rgba(236, 143, 213, 0.66)",
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointBackgroundColor: temperatures.map(temp => getPointColor(temp)),
                pointRadius: temperatures.map(temp => temp >= 37 || temp <= 24 ? 7 : 3),
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750
            },
            scales: {
                x: { 
                    title: { display: true, text: "Tiempo" },
                    ticks: { maxTicksLimit: 10 }
                },
                y: { 
                    title: { display: true, text: "Temperatura (°C)" }, 
                    suggestedMin: 15,
                    suggestedMax: 40  
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            let temp = tooltipItem.raw;
                            let symbol = temp >= 38 ? "🔥" : temp <= 22 ? "❄" : "";
                            return ` ${symbol} ${temp}°C`;
                        }
                    }
                }
            }
        }
    });
}

// Login functions
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);
            document.getElementById('loginForm').style.display = 'none';
            document.querySelector('.dashboard-header').style.display = 'block';
            document.querySelector('.dashboard').style.display = 'flex';
            document.querySelector('.monitoring-section').style.display = 'block';
            document.querySelector('.metrics-visualization').style.display = 'block';
            initializeCharts();
            startFetching();
        } else {
            alert('Usuario o contraseña incorrectos');  // error message
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error en el servidor. Por favor, intente más tarde.'); 
    });
}

function logout() {
    localStorage.removeItem('token');
    clearInterval(interval);
    isRunning = false;
    // Hide all elements
    document.querySelector('.dashboard-header').style.display = 'none';
    document.querySelector('.dashboard').style.display = 'none';
    document.querySelector('.monitoring-section').style.display = 'none';
    document.querySelector('.metrics-visualization').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
    // Clear data
    temperatures = [];
    timestamps = [];
    if (chart) {
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update();
    }
}

// Authentication helper
function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('token');
    const dashboardHeader = document.querySelector('.dashboard-header');
    const dashboard = document.querySelector('.dashboard');
    const monitoringSection = document.querySelector('.monitoring-section');
    const metricsVisualization = document.querySelector('.metrics-visualization');
    const loginForm = document.getElementById('loginForm');

    // Add event listeners
    document.getElementById('logoutButton').addEventListener('click', logout);
    document.getElementById("toggleSimulation").addEventListener("click", function () {
        if (isRunning) {
            clearInterval(interval);
            this.textContent = "Reanudar";
        } else {
            startFetching();
            this.textContent = "Pausar";
        }
        isRunning = !isRunning;
    });
    document.getElementById("exportJSON").addEventListener("click", exportToJSON);
    document.getElementById("exportCSV").addEventListener("click", exportToCSV);
    document.getElementById("viewAlerts").addEventListener("click", function () {
        const alertContainer = document.getElementById("alertContainer");
        alertContainer.classList.toggle("hidden");
        if (!alertContainer.classList.contains("hidden")) {
            hasNewAlert = false;
            document.getElementById("alertIndicator").classList.add("hidden");
        }
    });

    if (!token) {
        dashboardHeader.style.display = 'none';
        dashboard.style.display = 'none';
        monitoringSection.style.display = 'none';
        metricsVisualization.style.display = 'none';
        loginForm.style.display = 'block';
    } else {
        dashboardHeader.style.display = 'block';
        dashboard.style.display = 'flex';
        monitoringSection.style.display = 'block';
        metricsVisualization.style.display = 'block';
        loginForm.style.display = 'none';
        initializeCharts();
        startFetching();
    }
});

// Data fetching functions
function fetchTemperatures() {
    if (!isRunning) return;

    fetchWithAuth('http://127.0.0.1:5000/api/temperatures')
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) return;
        
        temperatures.length = 0;
        timestamps.length = 0;
        
        const limitedData = data.slice(-15);
        limitedData.forEach(item => {
            temperatures.push(item.temperature);
            timestamps.push(item.timestamp);
            checkCriticalTemperature(item.temperature, item.timestamp);
        });

        updateDisplay();
        updateChart();
    })
    .catch(error => console.error('Error al obtener temperaturas:', error));
}

function updateChart() {
    if (!chart) return;
    chart.data.labels = timestamps;
    chart.data.datasets[0].data = temperatures;
    chart.data.datasets[0].pointBackgroundColor = temperatures.map(temp => getPointColor(temp));
    chart.data.datasets[0].pointRadius = temperatures.map(temp => temp >= 37 || temp <= 24 ? 7 : 3);
    chart.update();
}

function fetchAverageTemperature() {
    if (!isRunning) return;
    
    fetchWithAuth('http://127.0.0.1:5000/api/metrics/average_temperature')
    .then(response => response.json())
    .then(data => {
        document.getElementById("tempPromedio24h").textContent = data.average_temperature;
    })
    .catch(error => console.error('Error al obtener temperatura promedio:', error));
}

function fetchTemperatureExtremes() {
    if (!isRunning) return;
    
    fetchWithAuth('http://127.0.0.1:5000/api/metrics/temperature_extremes')
    .then(response => response.json())
    .then(data => {
        document.getElementById("tempMax24h").textContent = data.max_temperature;
        document.getElementById("tempMin24h").textContent = data.min_temperature;
    })
    .catch(error => console.error('Error al obtener temperaturas extremas:', error));
}

function fetchAnomalyCount() {
    if (!isRunning) return;
    
    fetchWithAuth('http://127.0.0.1:5000/api/metrics/anomaly_count')
    .then(response => response.json())
    .then(data => {
        document.getElementById("highTempAlerts").textContent = data.high_temperature_alerts;
        document.getElementById("lowTempAlerts").textContent = data.low_temperature_alerts;
        document.getElementById("totalAlerts").textContent = data.total_alerts;
    })
    .catch(error => console.error('Error al obtener conteo de anomalías:', error));
}

function updateDisplay() {
    if (temperatures.length > 0) {
        let latestTemp = temperatures[temperatures.length - 1];
        document.getElementById("tempActual").textContent = latestTemp;
        let avgTemp = (temperatures.reduce((sum, t) => sum + t, 0) / temperatures.length).toFixed(2);
        document.getElementById("tempPromedio").textContent = avgTemp;
        let minTemp = Math.min(...temperatures);
        document.getElementById("tempMinLeft").textContent = minTemp.toFixed(2);
        let maxTemp = Math.max(...temperatures);
        document.getElementById("tempMaxLeft").textContent = maxTemp.toFixed(2);
    }
}

function startFetching() {
    fetchTemperatures();
    fetchAverageTemperature();
    fetchTemperatureExtremes();
    fetchAnomalyCount();
    updateMetrics();
    
    interval = setInterval(() => {
        fetchTemperatures();
        if (Date.now() % (2 * 5000) < 5000) {
            fetchAverageTemperature();
            fetchTemperatureExtremes();
            fetchAnomalyCount();
            updateMetrics();
        }
    }, 5000);
}

function updateMetrics() {
    if (!isRunning) return;
    
    fetchWithAuth('/metrics/history')
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const latest = data[0];
                document.getElementById('avg-temp').textContent = latest[1].toFixed(2);
                document.getElementById('max-temp').textContent = latest[2].toFixed(2);
                document.getElementById('min-temp').textContent = latest[3].toFixed(2);
                document.getElementById('anomalies').textContent = latest[4];

                const historyHtml = data.slice(0, 5).map(metric => `
                    <div class="history-item">
                        <span class="timestamp">${metric[0]}</span>
                        <span class="temp">Avg: ${metric[1].toFixed(2)}°C</span>
                        <span class="anomalies">Anomalies: ${metric[4]}</span>
                    </div>
                `).join('');
                document.getElementById('metrics-history').innerHTML = historyHtml;
            }
        })
        .catch(error => console.error('Error fetching metrics:', error));
}

function fetchMetricsByDate() {
    const selectedDate = document.getElementById('metricsDate').value;
    const selectedTime = document.getElementById('metricsTime').value;
    
    if (!selectedDate) {
        alert('Por favor selecciona una fecha');
        return;
    }

    fetchWithAuth(`/api/metrics/${selectedDate}?time_range=${selectedTime}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                displayNoDataMessage();
            } else {
                displayMetricsChart(data);
            }
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
            displayNoDataMessage();
        });
}

function displayNoDataMessage() {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    
    if (metricsChart) {
        metricsChart.destroy();
    }

    ctx.canvas.style.height = '150px';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '12px Arial';
    ctx.fillStyle = '#666';
    ctx.fillText('No hay métricas disponibles para este día u hora', ctx.canvas.width / 2, ctx.canvas.height / 2);
}

function displayMetricsChart(data) {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    data.sort((a, b) => new Date(a[0]) - new Date(b[0]));
    
    if (metricsChart) {
        metricsChart.destroy();
    }

    metricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d[0].split(' ')[1]),
            datasets: [
                {
                    label: 'Temperatura Promedio',
                    data: data.map(d => d[1]),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: 'Temperatura Máxima',
                    data: data.map(d => d[2]),
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                },
                {
                    label: 'Temperatura Mínima',
                    data: data.map(d => d[3]),
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Temperatura (°C)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hora'
                    }
                }
            }
        }
    });
}

// Export functions
function exportToJSON() {
    const data = timestamps.map((timestamp, index) => ({
        timestamp: timestamp,
        temperature: temperatures[index]
    }));
    const jsonData = JSON.stringify(data, null, 2);
    downloadFile("temperaturas.json", jsonData, "application/json");
}

function exportToCSV() {
    let csvContent = "Timestamp,Temperature\n";
    timestamps.forEach((timestamp, index) => {
        csvContent += `${timestamp},${temperatures[index]}\n`;
    });
    downloadFile("temperaturas.csv", csvContent, "text/csv");
}

function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// Alert functions
function checkCriticalTemperature(temp, timestamp) {
    let message = "";
    if (temp >= 37) {
        message = `🔥 Alerta: Temperatura alta (${temp}°C) a las ${timestamp}`;
    } else if (temp <= 24) {
        message = `❄ Alerta: Temperatura baja (${temp}°C) a las ${timestamp}`;
    }

    if (message && Math.random() < 0.3) {
        alertList.push(message);
        updateAlertList();
        notifyNewAlert();
    }
}

function updateAlertList() {
    if (alertList.length > 10) {
        alertList = alertList.slice(-10);
    }
    alertList = alertList.reverse();
    
    const alertListElement = document.getElementById("alertList");
    alertListElement.innerHTML = "";
    alertList.forEach(alert => {
        const li = document.createElement("li");
        li.textContent = alert;
        alertListElement.appendChild(li);
    });
}

function notifyNewAlert() {
    hasNewAlert = true;
    document.getElementById("alertIndicator").classList.remove("hidden");
}

function getPointColor(temp) {
    if (temp >= 37) return "red";
    if (temp <= 24) return "blue";
    return "black";
}