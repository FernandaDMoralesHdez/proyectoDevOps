from flask import Flask, jsonify
from flask_cors import CORS
import time
import random
import threading

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend

# Lista temporal para almacenar las temperaturas en memoria
temperature_data = []

def generate_temperature():
    """Simula el sensor de temperatura generando datos cada 2 segundos."""
    while True:
        temp = round(random.uniform(20, 40), 2)  # Simula temperatura entre 20 y 40°C
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Obtiene la hora actual
        if len(temperature_data) >= 20:  # Mantiene un límite de 20 datos
            temperature_data.pop(0)
        temperature_data.append({"timestamp": timestamp, "temperature": temp})
        print(f"Generado: {temp}°C a las {timestamp}")  # Para depuración en consola
        time.sleep(2)

@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    """Devuelve los últimos datos de temperatura almacenados temporalmente."""
    return jsonify(temperature_data)

@app.route('/')
def home():
    return "Servidor en funcionamiento. Visita http://127.0.0.1:5000/api/temperatures para ver los datos :)"

if __name__ == '__main__':
    # Iniciar la generación de datos en un hilo separado
    sensor_thread = threading.Thread(target=generate_temperature, daemon=True)
    sensor_thread.start()
    
    # Iniciar Flask
    app.run(debug=True, host='127.0.0.1', port=5000)


