import os
from flask import Blueprint, jsonify, current_app
from api.metrics import get_average_temperature, get_temperature_extremes, get_anomaly_count
from monitoring.metrics_monitor import MetricsMonitor

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/metrics/history', methods=['GET'])
def get_metrics_history():
    monitor = current_app.monitor  # Get monitor instance from Flask app
    history = monitor.get_metrics_history()
    return jsonify(history)

@metrics_bp.route('/metrics/report', methods=['GET'])
def generate_report():
    monitor = current_app.monitor
    # Create reports directory inside monitoring folder
    reports_dir = 'monitoring/reports'
    os.makedirs(reports_dir, exist_ok=True)
    monitor.export_metrics_report(f'{reports_dir}/metrics_report.json')
    return jsonify({"message": "Report generated successfully"})    

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

@metrics_bp.route('/api/metrics/<date>', methods=['GET'])
def get_metrics_by_date(date):
    """Ruta para obtener métricas de un día específico."""
    monitor = current_app.monitor
    start_date = f"{date} 00:00:00"
    end_date = f"{date} 23:59:59"
    metrics = monitor.get_metrics_by_range(start_date, end_date)
    return jsonify(metrics)
