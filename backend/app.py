from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import time
import os

app = Flask(__name__)
CORS(app)

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
            db = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )

            print("✅ Connected to MySQL")

            cursor = db.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender VARCHAR(100),
                receiver VARCHAR(100),
                amount DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            print("✅ transactions table ready")

            break

        except Exception as e:
            print("❌ Database connection failed:", e)
            time.sleep(5)

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

    try:
        data = request.get_json()

        sender = data.get("sender")
        receiver = data.get("receiver")
        amount = data.get("amount")

        if not sender or not receiver or not amount:
            return jsonify({
                "error": "sender, receiver and amount are required"
            }), 400

        db.ping(reconnect=True)

        cursor = db.cursor()

        query = """
        INSERT INTO transactions(sender, receiver, amount)
        VALUES(%s, %s, %s)
        """

        cursor.execute(query, (sender, receiver, amount))

        return jsonify({
            "message": "Transaction Successful"
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# =========================
# GET ALL TRANSACTIONS
# =========================

@app.route("/transactions", methods=["GET"])
def transactions():

    global db

    try:
        db.ping(reconnect=True)

        cursor = db.cursor()

        cursor.execute("""
        SELECT * FROM transactions
        ORDER BY id DESC
        """)

        result = cursor.fetchall()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

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