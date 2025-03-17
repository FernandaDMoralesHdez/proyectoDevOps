import sqlite3

DB_NAME = "db/temperaturas.db"

def ver_registros():
    """Muestra todos los registros de temperatura almacenados."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros ORDER BY id ASC")
        registros = cursor.fetchall()
        
        print("ID | Timestamp           | Temperature (°C)")
        print("-" * 40)
        for row in registros:
            print(f"{row[0]:<3} | {row[1]:<20} | {row[2]:<5}")

if __name__ == "__main__":
    ver_registros()

def ver_promedio_24h():
    """Muestra el promedio de temperatura de las últimas 24 horas."""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                AVG(temperature), 
                COUNT(temperature), 
                MIN(temperature), 
                MAX(temperature),
                COUNT(CASE WHEN temperature > 37 THEN 1 END) as high_alerts,
                COUNT(CASE WHEN temperature < 24 THEN 1 END) as low_alerts
            FROM registros 
            WHERE timestamp >= ?
        """, (yesterday_str,))
        avg, count, min_temp, max_temp, high_alerts, low_alerts = cursor.fetchone()
        
        print("\n=== Estadísticas últimas 24 horas ===")
        print(f"Promedio: {round(avg, 2)}°C")
        print(f"Cantidad de registros: {count}")
        print(f"Temperatura mínima: {round(min_temp, 2)}°C")
        print(f"Temperatura máxima: {round(max_temp, 2)}°C")
        print("\n=== Alertas en las últimas 24 horas ===")
        print(f"Alertas por temperatura alta: {high_alerts}")
        print(f"Alertas por temperatura baja: {low_alerts}")
        print(f"Total de alertas: {high_alerts + low_alerts}")

def ver_temperaturas_24h():
    """Muestra solo las temperaturas de las últimas 24 horas."""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT temperature FROM registros 
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (yesterday_str,))
        temperaturas = cursor.fetchall()

        print("\n=== Temperaturas en las últimas 24 horas ===")
        for temp in temperaturas:
            print(f"{temp[0]}°C")  # Solo imprime la temperatura

# Modify the main block to include the new function
if __name__ == "__main__":
    '''ver_registros()
    ver_promedio_24h()
    ver_temperaturas_24h()'''
    ver_promedio_24h()
