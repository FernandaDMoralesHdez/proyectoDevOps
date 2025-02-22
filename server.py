import sqlite3  # Para manejar la base de datos SQLite
import threading  # Para ejecutar procesos en segundo plano
import time  # Para manejar fechas y tiempos
import random  # Para generar temperaturas aleatorias
from flask import Flask, jsonify  # Flask para la API y jsonify para devolver JSON

# Inicializa la aplicación Flask
app = Flask(__name__)
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
        temp = round(random.uniform(20, 30), 2)  # Genera una temperatura aleatoria entre 20 y 30°C
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Obtiene la fecha y hora actual
        insert_temperature(temp, timestamp)  # Inserta el registro en la base de datos
        print(f"Insertado: {temp}°C a las {timestamp}")  # Muestra la información en consola
        time.sleep(2)  # Espera 2 segundos antes de generar otro dato

@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    """Ruta API que devuelve las últimas 10 temperaturas almacenadas en JSON"""
    conn = sqlite3.connect(DATABASE)  # Conecta a la base de datos
    c = conn.cursor()
    c.execute('SELECT timestamp, temperature FROM temperatures ORDER BY id DESC LIMIT 10')  # Obtiene los últimos 10 registros
    rows = c.fetchall()  # Obtiene los resultados de la consulta
    conn.close()  # Cierra la conexión
    rows.reverse()  # Invierte el orden para mostrar los datos en orden cronológico
    data = [{"timestamp": row[0], "temperature": row[1]} for row in rows]  # Convierte los datos en formato JSON
    return jsonify(data)  # Devuelve los datos en formato JSON

@app.route('/')
def home():
    return "Servidor en funcionamiento. Visita http://127.0.0.1:5000/api/temperatures para ver los datos :)"

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos
    
    # Crea un hilo en segundo plano para simular el sensor de temperatura
    sensor_thread = threading.Thread(target=sensor_simulation, daemon=True)
    sensor_thread.start()  # Inicia el hilo en segundo plano
    
    # Inicia la aplicación Flask en modo debug
    app.run(debug=True)
