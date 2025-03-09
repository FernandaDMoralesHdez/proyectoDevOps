from flask import Flask, jsonify
from flask_cors import CORS
import time
import random
import threading
from db.database import init_db, insert_temperature, get_last_temperatures # Importar el módulo database.py

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend

def generate_temperature():
    """Simula el sensor de temperatura generando datos cada 2 segundos."""
    while True:
        temp = round(random.uniform(20, 40), 2)  # Simula temperatura entre 20 y 40°C
        insert_temperature(temp) # Inserta el dato en la base de datos
        print(f"Generado: {temp}°C a las {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(2)

@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    """Devuelve los últimos datos de temperatura desde SQLite."""
    return jsonify(get_last_temperatures())

@app.route('/')
def home():
    return "Servidor en funcionamiento. Visita http://127.0.0.1:5000/api/temperatures para ver los datos :)"

if __name__ == '__main__':
    init_db()  # Asegurar que la BD y tabla existen antes de iniciar Flask
    sensor_thread = threading.Thread(target=generate_temperature, daemon=True)
    sensor_thread.start()
    # Iniciar Flask
    app.run(debug=True, host='127.0.0.1', port=5000)



