let isRunning = true;
let temperatures = [];
let timestamps = [];
let interval;

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
            y: { title: { display: true, text: "Temperatura (°C)" }, min: 15, max: 35 }
        }
    }
});

// Función para generar datos de temperatura aleatorios
function getRandomTemperature() {
    return (Math.random() * 10 + 20).toFixed(2); // Simula valores entre 20 y 30°C
}

// Función para actualizar la temperatura y la gráfica
function updateTemperature() {
    let newTemp = parseFloat(getRandomTemperature());
    let timestamp = new Date().toLocaleTimeString();

    // Agrega los nuevos datos
    temperatures.push(newTemp);
    timestamps.push(timestamp);

    // Limita el número de puntos en la gráfica (máx. 10)
    if (temperatures.length > 10) {
        temperatures.shift();
        timestamps.shift();
    }

    // Actualiza el texto de temperatura
    document.getElementById("tempActual").textContent = newTemp;
    let averageTemp = (temperatures.reduce((sum, t) => sum + t, 0) / temperatures.length).toFixed(2);
    document.getElementById("tempPromedio").textContent = averageTemp;

    // Refresca la gráfica
    chart.update();
}

// Inicia la simulación
function startSimulation() {
    interval = setInterval(updateTemperature, 2000);
}

// Botón para pausar o reanudar la simulación
document.getElementById("toggleSimulation").addEventListener("click", function () {
    if (isRunning) {
        clearInterval(interval);
        this.textContent = "Reanudar";
    } else {
        startSimulation();
        this.textContent = "Pausar";
    }
    isRunning = !isRunning;
});

startSimulation();

