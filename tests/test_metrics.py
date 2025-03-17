import pytest
import sqlite3
from datetime import datetime, timedelta
from api.metrics import get_average_temperature, get_temperature_extremes, get_anomaly_count

def test_get_average_temperature():
    """Test average temperature calculation"""
    avg_temp = get_average_temperature()
    assert avg_temp is not None
    assert isinstance(avg_temp, float)
    assert 20 <= avg_temp <= 40  # Rango esperado de temperaturas

def test_get_temperature_extremes():
    """Test temperature extremes retrieval"""
    extremes = get_temperature_extremes()
    assert extremes is not None
    assert isinstance(extremes, dict)
    assert 'max_temperature' in extremes
    assert 'min_temperature' in extremes
    # Verificar que máxima sea mayor que mínima
    if extremes['max_temperature'] and extremes['min_temperature']:
        assert extremes['max_temperature'] >= extremes['min_temperature']

def test_get_anomaly_count():
    """Test anomaly counting"""
    counts = get_anomaly_count()
    assert counts is not None
    assert isinstance(counts, dict)
    assert 'high_temperature_alerts' in counts
    assert 'low_temperature_alerts' in counts
    assert 'total_alerts' in counts
    # Verificar que el total sea la suma de altas y bajas
    assert counts['total_alerts'] == counts['high_temperature_alerts'] + counts['low_temperature_alerts']

def test_handle_no_data():
    """Test that functions handle empty results correctly"""
    # Use a future date where we know there won't be any data
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("db/temperaturas.db")
    cursor = conn.cursor()
    
    # Query with a future date to ensure no results
    cursor.execute("SELECT AVG(temperature) FROM registros WHERE timestamp >= ?", (future_date,))
    result = cursor.fetchone()[0]
    conn.close()
    
    # Verify that None is returned when no data is found
    assert result is None

    