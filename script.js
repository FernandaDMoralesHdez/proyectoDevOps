let isRunning = true;
let interval;
let temperatures = [];
let timestamps = [];

// Inicializar la gráfica con Chart.js
const ctx = document.getElementById("temperatureChart").getContext("2d");
const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: timestamps,
        datasets: [{
            label: "Temperatura (°C)",
            data: temperatures,
            borderColor: "red",
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            borderWidth: 2,
            fill: true,
            pointBackgroundColor: temperatures.map(temp => getPointColor(temp)), // Cambia color de puntos críticos
            pointRadius: temperatures.map(temp => temp >= 37 || temp <= 24 ? 7 : 3), // Agranda los puntos críticos
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: "Tiempo" } },
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

// Obtener datos desde el backend Flask
function fetchTemperatures() {
    if (!isRunning) return;  // No hacer fetch si está pausado

    fetch('http://127.0.0.1:5000/api/temperatures')
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) {
            console.log("No hay datos disponibles aún.");
            return;
        }

        // Limpiar arrays
        temperatures.length = 0;
        timestamps.length = 0;

        data.forEach(item => {
            temperatures.push(item.temperature);
            timestamps.push(item.timestamp);
        });

        updateDisplay();
        chart.data.labels = timestamps;
        chart.data.datasets[0].data = temperatures;
        chart.update();
    })
    .catch(error => console.error('Error al obtener temperaturas:', error));
}

// Mostrar la temperatura actual y el promedio
function updateDisplay() {
    if (temperatures.length > 0) {
        let latestTemp = temperatures[temperatures.length - 1];
        document.getElementById("tempActual").textContent = latestTemp;
        let avgTemp = (temperatures.reduce((sum, t) => sum + t, 0) / temperatures.length).toFixed(2);
        document.getElementById("tempPromedio").textContent = avgTemp;
    }
}

// Inicia la consulta de datos
function startFetching() {
    fetchTemperatures();  // Ejecuta la primera consulta de inmediato
    interval = setInterval(fetchTemperatures, 2000);
}

// Botón para pausar/reanudar la consulta
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

// Comienza la consulta de datos
startFetching();

// Agregar eventos a los botones de exportación
document.getElementById("exportJSON").addEventListener("click", exportToJSON);
document.getElementById("exportCSV").addEventListener("click", exportToCSV);

// Función para exportar datos a JSON
function exportToJSON() {
    const data = timestamps.map((timestamp, index) => ({
        timestamp: timestamp,
        temperature: temperatures[index]
    }));
    const jsonData = JSON.stringify(data, null, 2);
    downloadFile("temperaturas.json", jsonData, "application/json");
}

function exportToCSV() {
    let csvContent = "Timestamp,Temperature\n"; // Encabezados
    timestamps.forEach((timestamp, index) => {
        csvContent += `${timestamp},${temperatures[index]}\n`; // Alineación correcta
    });
    downloadFile("temperaturas.csv", csvContent, "text/csv");
}


// Función auxiliar para descargar archivos
function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

function getPointColor(temp) {
    if (temp >= 38) return "red";  // Temperatura alta (peligro)
    if (temp <= 22) return "blue"; // Temperatura baja (peligro)
    return "black";  // Normal
}
//Nuevo codigo
let alertList = [];
let hasNewAlert = false;

document.getElementById("viewAlerts").addEventListener("click", function () {
    const alertContainer = document.getElementById("alertContainer");
    alertContainer.classList.toggle("hidden"); // Mostrar/Ocultar alertas

    // Si se abren las alertas, quitar el indicador 🔴
    if (!alertContainer.classList.contains("hidden")) {
        hasNewAlert = false;
        document.getElementById("alertIndicator").classList.add("hidden");
    }
});

// Función para agregar alertas de manera controlada
function checkCriticalTemperature(temp, timestamp) {
    let message = "";
    if (temp >= 37) {
        message = `🔥 Alerta: Temperatura alta (${temp}°C) a las ${timestamp}`;
    } else if (temp <= 24) {
        message = `❄ Alerta: Temperatura baja (${temp}°C) a las ${timestamp}`;
    }

    // Aplicamos una probabilidad del 30% para que la alerta se genere
    if (message && Math.random() < 0.3) {  // 30% de probabilidad
        alertList.push(message);
        updateAlertList();
        notifyNewAlert();
    }
}

// Función para actualizar la lista de alertas en pantalla
function updateAlertList() {
    const alertListElement = document.getElementById("alertList");
    alertListElement.innerHTML = ""; // Limpia la lista
    alertList.forEach(alert => {
        const li = document.createElement("li");
        li.textContent = alert;
        alertListElement.appendChild(li);
    });
}

// Función para mostrar el indicador 🔴 en el botón
function notifyNewAlert() {
    hasNewAlert = true;
    document.getElementById("alertIndicator").classList.remove("hidden");
}

// Integrar alertas en la lógica de actualización de datos
function fetchTemperatures() {
    if (!isRunning) return;  // No hacer fetch si está pausado

    fetch('http://127.0.0.1:5000/api/temperatures')
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) {
            console.log("No hay datos disponibles aún.");
            return;
        }

        temperatures.length = 0;
        timestamps.length = 0;

        data.forEach(item => {
            temperatures.push(item.temperature);
            timestamps.push(item.timestamp);
            checkCriticalTemperature(item.temperature, item.timestamp); // Revisar alertas
        });

        updateDisplay();
        chart.data.labels = timestamps;
        chart.data.datasets[0].data = temperatures;
        chart.update();
    })
    .catch(error => console.error('Error al obtener temperaturas:', error));
}


