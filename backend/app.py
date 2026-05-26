from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pymysql
import time
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time as time_module

app = Flask(__name__)
CORS(app)

# =========================
# PROMETHEUS METRICS
# =========================

transactions_total = Counter('smartpay_transactions_total', 'Total transactions', ['status'])
transaction_amount = Counter('smartpay_transaction_amount_total', 'Total amount transacted', ['status'])
db_connection_attempts = Counter('smartpay_db_connection_attempts', 'Database connection attempts', ['status'])
db_query_duration = Histogram('smartpay_db_query_duration_seconds', 'Database query duration', ['operation'])
active_connections = Gauge('smartpay_active_db_connections', 'Active database connections')
transactions_pending = Gauge('smartpay_transactions_pending', 'Pending transactions count')

# =========================
# DATABASE CONFIG
# =========================

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

db = None

# =========================
# DATABASE CONNECTION
# =========================

def connect_database():
    global db

    while True:
        try:
            db_connection_attempts.labels(status='attempting').inc()
            db = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )

            db_connection_attempts.labels(status='success').inc()
            active_connections.set(1)
            print("✅ Connected to MySQL")

            cursor = db.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender VARCHAR(100),
                receiver VARCHAR(100),
                amount DECIMAL(10,2),
                status VARCHAR(50) DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at),
                INDEX idx_status (status)
            )
            """)

            print("✅ transactions table ready")

            break

        except Exception as e:
            db_connection_attempts.labels(status='failed').inc()
            active_connections.set(0)
            print("❌ Database connection failed:", e)
            time_module.sleep(5)

# Connect on startup
connect_database()

# =========================
# HOME ROUTE
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "SmartPay Backend Running Successfully"
    }), 200

# =========================
# HEALTH CHECK
# =========================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    }), 200

# =========================
# SEND MONEY API
# =========================

@app.route("/send", methods=["POST"])
def send_money():

    global db
    start_time = time_module.time()

    try:
        data = request.get_json()

        sender = data.get("sender")
        receiver = data.get("receiver")
        amount = data.get("amount")

        if not sender or not receiver or not amount:
            transactions_total.labels(status='failed').inc()
            return jsonify({
                "error": "sender, receiver and amount are required"
            }), 400

        db.ping(reconnect=True)

        cursor = db.cursor()

        query = """
        INSERT INTO transactions(sender, receiver, amount, status)
        VALUES(%s, %s, %s, %s)
        """

        cursor.execute(query, (sender, receiver, amount, 'completed'))

        # Update metrics
        transactions_total.labels(status='completed').inc()
        transaction_amount.labels(status='completed').inc(amount)
        db_query_duration.labels(operation='insert').observe(time_module.time() - start_time)

        return jsonify({
            "message": "Transaction Successful",
            "transaction_id": cursor.lastrowid
        }), 201

    except Exception as e:
        transactions_total.labels(status='failed').inc()
        db_query_duration.labels(operation='insert').observe(time_module.time() - start_time)
        return jsonify({
            "error": str(e)
        }), 500

# =========================
# GET ALL TRANSACTIONS
# =========================

@app.route("/transactions", methods=["GET"])
def transactions():

    global db
    start_time = time_module.time()

    try:
        db.ping(reconnect=True)

        cursor = db.cursor()

        cursor.execute("""
        SELECT * FROM transactions
        ORDER BY id DESC
        """)

        result = cursor.fetchall()
        
        # Update pending count
        cursor.execute("""
        SELECT COUNT(*) as pending FROM transactions WHERE status='pending'
        """)
        pending_count = cursor.fetchone()['pending']
        transactions_pending.set(pending_count)
        
        db_query_duration.labels(operation='select').observe(time_module.time() - start_time)

        return jsonify(result), 200

    except Exception as e:
        db_query_duration.labels(operation='select').observe(time_module.time() - start_time)
        return jsonify({
            "error": str(e)
        }), 500

# =========================
# PROMETHEUS METRICS ENDPOINT
# =========================

@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    print("🚀 Starting SmartPay Backend on Port 5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )