from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'my-secret-key'  # In production, use environment variable

ROLES = {
    'admin': ['read', 'write', 'export', 'configure'],
    'operator': ['read', 'export'],
    'viewer': ['read']
}

def create_token(username, role):
    token = jwt.encode({
        'user': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    return token

def requires_auth(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Missing token'}), 401

            try:
                token = token.split()[1]  # Remove 'Bearer' prefix
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                role = payload['role']
                
                if permission not in ROLES[role]:
                    return jsonify({'message': 'Insufficient permissions'}), 403
                
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token'}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator