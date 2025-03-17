import pytest
from flask import Flask
from api.routes import metrics_bp

@pytest.fixture
def app():
    """Create test application"""
    app = Flask(__name__)
    app.register_blueprint(metrics_bp)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_average_temperature_route(client):
    """Test average temperature endpoint"""
    response = client.get('/api/metrics/average_temperature')
    assert response.status_code == 200
    data = response.get_json()
    assert 'average_temperature' in data
    assert isinstance(data['average_temperature'], (float, type(None)))

def test_temperature_extremes_route(client):
    """Test temperature extremes endpoint"""
    response = client.get('/api/metrics/temperature_extremes')
    assert response.status_code == 200
    data = response.get_json()
    assert 'max_temperature' in data
    assert 'min_temperature' in data
    if data['max_temperature'] and data['min_temperature']:
        assert data['max_temperature'] >= data['min_temperature']

def test_anomaly_count_route(client):
    """Test anomaly count endpoint"""
    response = client.get('/api/metrics/anomaly_count')
    assert response.status_code == 200
    data = response.get_json()
    assert 'high_temperature_alerts' in data
    assert 'low_temperature_alerts' in data
    assert 'total_alerts' in data
    assert data['total_alerts'] == data['high_temperature_alerts'] + data['low_temperature_alerts']