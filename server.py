from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import threading
import time
import random
import os

# Configuración del entorno antes de inicializar Flask
os.environ["FLASK_ENV"] = "development"

# Inicializa la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS en toda la aplicación
# Nombre de la base de datos
DATABASE = 'temperatures.db'

def init_db():
    """Crea la base de datos y la tabla si no existen."""
    conn = sqlite3.connect(DATABASE)  # Conecta a la base de datos SQLite
    c = conn.cursor()  # Crea un cursor para ejecutar comandos SQL
    c.execute('''
        CREATE TABLE IF NOT EXISTS temperatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Clave primaria autoincremental
            timestamp TEXT,  -- Fecha y hora del registro
            temperature REAL  -- Temperatura en formato decimal
        )
    ''')
    conn.commit()  # Guarda los cambios
    conn.close()  # Cierra la conexión

def insert_temperature(temp, timestamp):
    """Inserta un nuevo registro de temperatura en la base de datos."""
    conn = sqlite3.connect(DATABASE)  # Conecta a la base de datos
    c = conn.cursor()
    c.execute('INSERT INTO temperatures (timestamp, temperature) VALUES (?, ?)', (timestamp, temp))
    conn.commit()  # Guarda los cambios
    conn.close()  # Cierra la conexión

def sensor_simulation():
    """Simula un sensor que genera temperaturas aleatorias cada 2 segundos"""
    while True:
        temp = round(random.uniform(15, 40), 2)  # Genera una temperatura aleatoria entre 15 y 40°C
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Obtiene la fecha y hora actual
        insert_temperature(temp, timestamp)  # Inserta el registro en la base de datos
        print(f"Insertado: {temp}°C a las {timestamp}")  # Muestra la información en consola
        time.sleep(10)  # Espera 2 segundos antes de generar otro dato

@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    """Ruta API que devuelve las últimas 10 temperaturas almacenadas en JSON"""
    limit = request.args.get("limit", default=50, type=int)  # Permite cambiar el límite desde el frontend
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'SELECT timestamp, temperature FROM temperatures ORDER BY id DESC LIMIT {limit}')
    rows = c.fetchall()
    conn.close()
    rows.reverse()  
    return jsonify([{"timestamp": row[0], "temperature": row[1]} for row in rows])

@app.route('/')
def home():
    return "Servidor en funcionamiento. Visita http://127.0.0.1:5000/api/temperatures para ver los datos :)"

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos
    
    # Crea un hilo en segundo plano para simular el sensor de temperatura
    sensor_thread = threading.Thread(target=sensor_simulation, daemon=True)
    sensor_thread.start()  # Inicia el hilo en segundo plano
    
    # Inicia la aplicación Flask en modo debug
    app.run(debug=True, host='127.0.0.1', port=5000)
