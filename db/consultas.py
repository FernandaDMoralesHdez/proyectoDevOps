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
        if count == 0:
            print("No hay datos disponibles en las últimas 24 horas.")
            print("Por favor, asegúrate de que el servidor esté ejecutándose y generando datos.")
            return
            
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

def ver_monitoring_metrics():
    """Shows all metrics stored in the monitoring database."""
    with sqlite3.connect("db/monitoring.db") as conn:
        cursor = conn.cursor()
        
        # Get total count of records
        cursor.execute("SELECT COUNT(*) FROM metrics_history")
        total_records = cursor.fetchone()[0]
        
        # Get date range
        cursor.execute("""
            SELECT MIN(date(timestamp)), MAX(date(timestamp))
            FROM metrics_history
        """)
        min_date, max_date = cursor.fetchone()
        
        print("\n=== Resumen del monitoreo 24 hr ===")
        print(f"Total records: {total_records}")
        print(f"Date range: {min_date} to {max_date}")
        print("\n=== Historial de métricas de monitoreo ===")
        print("Timestamp           | Avg Temp | Max Temp | Min Temp | Anomalies")
        print("-" * 65)
        
        # Get all records ordered by timestamp
        cursor.execute("""
            SELECT * FROM metrics_history 
            ORDER BY timestamp DESC
        """)
        metrics = cursor.fetchall()  # Store the results in metrics variable
        
        for row in metrics:
            print(f"{row[0]:<19} | {row[1]:<8.2f} | {row[2]:<8.2f} | {row[3]:<8.2f} | {row[4]:<9}")

def ver_metricas_por_rango():
    """Ver métricas en un rango de fechas específico"""
    start_date = '2025-03-18'  # Ajusta estas fechas según tus datos
    end_date = '2025-03-19'
    
    with sqlite3.connect("db/monitoring.db") as conn:
        cursor = conn.execute("""
            SELECT * FROM metrics_history 
            WHERE date(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """, (start_date, end_date))
        
        print(f"\n=== Métricas {start_date} - {end_date} ===")
        print("Timestamp           | Avg Temp | Max Temp | Min Temp | Anomalies")
        print("-" * 65)
        for row in cursor.fetchall():
            print(f"{row[0]:<19} | {row[1]:<8.2f} | {row[2]:<8.2f} | {row[3]:<8.2f} | {row[4]:<9}")

# Modify the main block to include the new function
if __name__ == "__main__":
    '''ver_registros()
    ver_promedio_24h()
    ver_temperaturas_24h()
    ver_promedio_24h()'''
    #ver_monitoring_metrics()
    ver_metricas_por_rango()
