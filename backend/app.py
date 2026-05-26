from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pymysql
import os
import time

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST
)

# =========================
# FLASK APP
# =========================

app = Flask(__name__)
CORS(app)

# =========================
# PROMETHEUS METRICS
# =========================

transactions_total = Counter(
    'smartpay_transactions_total',
    'Total transactions',
    ['status']
)

transaction_amount = Counter(
    'smartpay_transaction_amount_total',
    'Total amount transacted',
    ['status']
)

db_connection_attempts = Counter(
    'smartpay_db_connection_attempts',
    'Database connection attempts',
    ['status']
)

db_query_duration = Histogram(
    'smartpay_db_query_duration_seconds',
    'Database query duration',
    ['operation']
)

active_connections = Gauge(
    'smartpay_active_db_connections',
    'Active database connections'
)

# =========================
# DATABASE ENV VARIABLES
# =========================

MYSQL_HOST = os.getenv("DB_HOST")
MYSQL_USER = os.getenv("DB_USER")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD")
MYSQL_DATABASE = os.getenv("DB_NAME")

db = None

# =========================
# DATABASE CONNECTION
# =========================

def connect_database():

    global db

    while True:

        try:

            print("Attempting MySQL Connection...")

            db_connection_attempts.labels(status='attempt').inc()

            db = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=10
            )

            active_connections.set(1)

            db_connection_attempts.labels(status='success').inc()

            print("✅ Connected to MySQL Successfully")

            create_table()

            break

        except Exception as e:

            active_connections.set(0)

            db_connection_attempts.labels(status='failed').inc()

            print(f"❌ Database Connection Failed: {e}")

            time.sleep(5)

# =========================
# CREATE TABLE
# =========================

def create_table():

    global db

    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender VARCHAR(100) NOT NULL,
        receiver VARCHAR(100) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(50) DEFAULT 'completed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    print("✅ transactions table ready")

# =========================
# CONNECT DATABASE ON STARTUP
# =========================

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

    start_time = time.time()

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Invalid JSON body"
            }), 400

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
        INSERT INTO transactions (
            sender,
            receiver,
            amount,
            status
        )
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                sender,
                receiver,
                amount,
                "completed"
            )
        )

        transaction_id = cursor.lastrowid

        transactions_total.labels(status='success').inc()

        transaction_amount.labels(status='success').inc(float(amount))

        db_query_duration.labels(
            operation='insert'
        ).observe(time.time() - start_time)

        print(f"✅ Transaction Success: {transaction_id}")

        return jsonify({
            "message": "Transaction Successful",
            "transaction_id": transaction_id
        }), 201

    except Exception as e:

        transactions_total.labels(status='failed').inc()

        print(f"❌ Transaction Failed: {e}")

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# GET TRANSACTIONS
# =========================

@app.route("/transactions", methods=["GET"])
def get_transactions():

    global db

    start_time = time.time()

    try:

        db.ping(reconnect=True)

        cursor = db.cursor()

        cursor.execute("""
        SELECT * FROM transactions
        ORDER BY id DESC
        """)

        result = cursor.fetchall()

        db_query_duration.labels(
            operation='select'
        ).observe(time.time() - start_time)

        return jsonify(result), 200

    except Exception as e:

        print(f"❌ Fetch Failed: {e}")

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# PROMETHEUS METRICS
# =========================

@app.route("/metrics", methods=["GET"])
def metrics():

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )

# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    print("🚀 Starting SmartPay Backend on Port 5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
