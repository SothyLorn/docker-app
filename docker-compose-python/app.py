from flask import Flask, jsonify
import psycopg2
import redis
import os
import socket

app = Flask(__name__)


def get_db_connection():
    """Establish connection to PostgreSQL database."""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        database=os.getenv('DB_NAME', 'mydb'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'secret123'),
        port=os.getenv('DB_PORT', '5432')
    )
    return conn


def get_redis():
    """Establish connection to Redis cache."""
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'redis'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        decode_responses=True
    )
    return r


@app.route('/')
def home():
    """Home endpoint returning basic app information."""
    return jsonify({
        'message': 'Hello from Docker Compose!',
        'hostname': socket.gethostname(),
        'environment': os.getenv('APP_ENV', 'development')
    })


@app.route('/health')
def health():
    """Health check endpoint for database and Redis connectivity."""
    try:
        conn = get_db_connection()
        conn.close()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    try:
        r = get_redis()
        r.ping()
        redis_status = 'connected'
    except Exception as e:
        redis_status = f'error: {str(e)}'

    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'redis': redis_status
    })


@app.route('/counter')
def counter():
    """Counter endpoint that increments on each visit."""
    r = get_redis()
    count = r.incr('hits')
    return jsonify({'visits': count})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)