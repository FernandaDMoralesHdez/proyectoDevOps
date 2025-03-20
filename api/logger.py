import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Configure logger
def setup_logger():
    logger = logging.getLogger('temperature_monitor')
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create rotating file handler
    handler = RotatingFileHandler(
        'logs/temperature_monitor.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )

    # Create custom JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName
            }
            return json.dumps(log_entry)

    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger

# Create logger instance
logger = setup_logger()