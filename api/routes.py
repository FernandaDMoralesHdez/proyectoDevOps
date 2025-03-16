from flask import Blueprint, jsonify
from api.metrics import get_average_temperature, get_temperature_extremes, get_anomaly_count

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/api/metrics/average_temperature', methods=['GET'])
def average_temperature():
    """Ruta para obtener la temperatura promedio de las últimas 24 horas."""
    avg_temp = get_average_temperature()
    return jsonify({"average_temperature": avg_temp})

@metrics_bp.route('/api/metrics/temperature_extremes', methods=['GET'])
def temperature_extremes():
    """Ruta para obtener las temperaturas extremas de las últimas 24 horas."""
    extremes = get_temperature_extremes()
    return jsonify(extremes)

@metrics_bp.route('/api/metrics/anomaly_count', methods=['GET'])
def anomaly_count():
    """Ruta para obtener el conteo de anomalías en las últimas 24 horas."""
    counts = get_anomaly_count()
    return jsonify(counts)
