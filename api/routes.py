import os
from flask import Blueprint, jsonify, current_app, request
from api.metrics import get_average_temperature, get_temperature_extremes, get_anomaly_count
from monitoring.metrics_monitor import MetricsMonitor
from datetime import datetime, timedelta
from security.auth import requires_auth, create_token

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
    """Ruta para obtener métricas de un día específico con filtro de hora opcional."""
    try:
        # Validate date
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        min_date = datetime.strptime('2025-03-19', '%Y-%m-%d')
        if date_obj < min_date:
            return jsonify({"error": "Fecha no válida"})

        monitor = current_app.monitor
        time_range = request.args.get('time_range', 'all')
        
        # Set time range based on selection
        if time_range == 'all':
            start_time = "00:00:00"
            end_time = "23:59:59"
        else:
            hour = int(time_range)
            start_time = f"{hour:02d}:00:00"
            end_time = f"{(hour + 6):02d}:59:59"

        start_date = f"{date} {start_time}"
        end_date = f"{date} {end_time}"
        
        metrics = monitor.get_metrics_by_range(start_date, end_date)
        
        if not metrics:
            return jsonify({"error": "No hay datos disponibles"})
            
        return jsonify(metrics)
        
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"})

@metrics_bp.route('/api/metrics/export', methods=['GET'])
@requires_auth('export')
def export_metrics():
    """Only users with export permission can access this"""
    # Export functionality
    pass

@metrics_bp.route('/api/metrics/configure', methods=['POST'])
@requires_auth('configure')
def configure_metrics():
    """Only admins can configure the system"""
    # Configuration functionality
    pass

@metrics_bp.route('/api/login', methods=['POST'])
def login():
    """Login endpoint to get JWT token"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # For demo purposes - in production use proper user database
    users = {
        'admin': {'password': 'admin123', 'role': 'admin'},
        'operator': {'password': 'op123', 'role': 'operator'},
        'viewer': {'password': 'view123', 'role': 'viewer'}
    }
    
    if username in users and users[username]['password'] == password:
        token = create_token(username, users[username]['role'])
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401
