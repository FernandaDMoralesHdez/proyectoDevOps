import sqlite3
from datetime import datetime
import json

class MetricsMonitor:
    def __init__(self, db_path="db/monitoring.db"):
        self.db_path = db_path
        self.init_db()
        self.load_historical_data()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics_history (
                    timestamp TEXT,
                    avg_temp REAL,
                    max_temp REAL,
                    min_temp REAL,
                    anomaly_count INTEGER,
                    PRIMARY KEY (timestamp)
                )
            ''')

    def load_historical_data(self):
        """Load all historical data from temperaturas.db into monitoring metrics"""
        with sqlite3.connect("db/temperaturas.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    timestamp,
                    AVG(temperature),
                    MAX(temperature),
                    MIN(temperature),
                    COUNT(CASE WHEN temperature NOT BETWEEN 24 AND 37 THEN 1 END)
                FROM registros
                GROUP BY date(timestamp)
                ORDER BY timestamp
            """)
            
            for row in cursor.fetchall():
                timestamp, avg_temp, max_temp, min_temp, anomalies = row
                if avg_temp is not None:
                    self.store_metrics(
                        round(avg_temp, 2),
                        round(max_temp, 2),
                        round(min_temp, 2),
                        anomalies,
                        timestamp
                    )        

    def store_metrics(self, avg_temp, max_temp, min_temp, anomaly_count, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO metrics_history 
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, avg_temp, max_temp, min_temp, anomaly_count))
            except sqlite3.IntegrityError:
                pass  # Skip if timestamp already exists

    def collect_current_metrics(self):
        """Collect current metrics from the temperature database"""
        from api.metrics import get_average_temperature, get_temperature_extremes, get_anomaly_count
        
        avg_temp = get_average_temperature()
        extremes = get_temperature_extremes()
        anomalies = get_anomaly_count()
        
        if avg_temp and extremes['max_temperature']:
            self.store_metrics(
                avg_temp,
                extremes['max_temperature'],
                extremes['min_temperature'],
                anomalies['total_alerts']
            )

    def get_metrics_history(self, hours=24):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM metrics_history 
                WHERE timestamp >= datetime('now', ?) 
                ORDER BY timestamp DESC
            ''', (f'-{hours} hours',))
            return cursor.fetchall()

    def get_metrics_by_range(self, start_date, end_date):
        """Query metrics for a specific date range"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM metrics_history 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
            return cursor.fetchall()

    def export_metrics_report(self, filepath):
        history = self.get_metrics_history()
        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics_history": [
                {
                    "timestamp": row[0],
                    "average_temperature": row[1],
                    "max_temperature": row[2],
                    "min_temperature": row[3],
                    "anomaly_count": row[4]
                }
                for row in history
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
    
    def start_periodic_collection(self, interval=300):  # 300 seconds = 5 minutes
        """Start collecting metrics periodically"""
        import threading
        import time
        
        def collect_loop():
            while True:
                self.collect_current_metrics()
                time.sleep(interval)
        
        thread = threading.Thread(target=collect_loop, daemon=True)
        thread.start()