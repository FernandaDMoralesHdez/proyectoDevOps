import sqlite3
import time
from datetime import datetime, timedelta

def get_average_temperature():
    """
    Calcula la temperatura promedio de las últimas 24 horas.
    
    Returns:
        float: Temperatura promedio redondeada a 2 decimales.
    """
    # Calcular la fecha de hace 24 horas
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    
    # Conectar a la base de datos
    conn = sqlite3.connect("db/temperaturas.db")
    cursor = conn.cursor()
    
    # Consultar temperaturas de las últimas 24 horas
    cursor.execute("""
        SELECT AVG(temperature) 
        FROM registros 
        WHERE timestamp >= ?
    """, (yesterday_str,))
    
    result = cursor.fetchone()[0]
    conn.close()
    
    # Si no hay datos, devolver None
    if result is None:
        return None
    
    # Redondear a 2 decimales
    return round(result, 2)

def get_temperature_extremes():
    """
    Obtiene las temperaturas máximas y mínimas de las últimas 24 horas.
    
    Returns:
        dict: Diccionario con temperaturas máxima y mínima
    """
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("db/temperaturas.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT MAX(temperature), MIN(temperature),
               MAX(CASE WHEN temperature >= 37 THEN timestamp END) as max_timestamp,
               MIN(CASE WHEN temperature <= 24 THEN timestamp END) as min_timestamp
        FROM registros 
        WHERE timestamp >= ?
    """, (yesterday_str,))
    
    max_temp, min_temp, max_time, min_time = cursor.fetchone()
    conn.close()
    
    return {
        "max_temperature": round(max_temp, 2) if max_temp else None,
        "min_temperature": round(min_temp, 2) if min_temp else None,
        "max_timestamp": max_time,
        "min_timestamp": min_time
    }

def get_anomaly_count():
    """
    Cuenta las anomalías de temperatura en las últimas 24 horas.
    Una anomalía es cuando la temperatura está fuera del rango normal (24-37°C).
    
    Returns:
        dict: Conteo de anomalías por tipo
    """
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("db/temperaturas.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN temperature > 37 THEN 1 END) as high_temp_count,
            COUNT(CASE WHEN temperature < 24 THEN 1 END) as low_temp_count
        FROM registros 
        WHERE timestamp >= ?
    """, (yesterday_str,))
    
    high_count, low_count = cursor.fetchone()
    conn.close()
    
    return {
        "high_temperature_alerts": high_count,
        "low_temperature_alerts": low_count,
        "total_alerts": high_count + low_count
    }
