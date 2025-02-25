let temperatures = [];
let timestamps = [];

// Obtiene el contexto del canvas para la gráfica
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
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: "Tiempo" } },
            y: { 
                title: { display: true, text: "Temperatura (°C)" }, 
                suggestedMin: 10,
                suggestedMax: 50  
            }
        }
    }
});

// Función para obtener el último dato de temperatura y actualizar la gráfica
function fetchLatestTemperature() {
    fetch('http://127.0.0.1:5000/api/last_temperature')
    .then(response => response.json())
    .then(data => {
        if (!data || !data.temperature) return;

        // Agregar solo el nuevo valor
        temperatures.push(data.temperature);
        timestamps.push(data.timestamp);

        // Mantener solo los últimos 10 valores en la gráfica
        if (temperatures.length > 10) {
            temperatures.shift();
            timestamps.shift();
        }

        updateDisplay();
        chart.data.labels = timestamps;
        chart.data.datasets[0].data = temperatures;
        chart.update();
    })
    .catch(error => console.error('Error al obtener la última temperatura:', error));
}

// Actualiza la temperatura actual y el promedio en la interfaz
function updateDisplay() {
    if (temperatures.length > 0) {
        let latestTemp = temperatures[temperatures.length - 1];
        document.getElementById("tempActual").textContent = latestTemp;
        let avgTemp = (temperatures.reduce((sum, t) => sum + t, 0) / temperatures.length).toFixed(2);
        document.getElementById("tempPromedio").textContent = avgTemp;
    }
}

// Llama a la función cada 2 segundos para actualizar en tiempo real
setInterval(fetchLatestTemperature, 2000);

// Inicia la consulta de datos
fetchLatestTemperature();

