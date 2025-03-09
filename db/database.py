import sqlite3
import time

DB_NAME = "temperaturas.db"

def init_db():
    """Crea la base de datos y la tabla si no existen."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL
            )
        ''')
        conn.commit()

def insert_temperature(temp):
    """Inserta un nuevo registro de temperatura en la base de datos."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registros (timestamp, temperature) VALUES (?, ?)", (timestamp, temp))
        conn.commit()

def get_last_temperatures(limit=50):
    """Recupera los últimos registros de temperatura."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, temperature 
            FROM (
                SELECT * FROM registros ORDER BY id DESC LIMIT ?
            ) 
            ORDER BY id ASC
        """, (limit,))
        data = [{"timestamp": row[0], "temperature": row[1]} for row in cursor.fetchall()]
    return data

# Ejecutar la creación de la tabla si este archivo se ejecuta directamente
if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")
