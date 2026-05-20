from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import time
import os

app = Flask(__name__)
CORS(app)

# =========================
# DATABASE CONNECTION
# =========================

while True:
    try:
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            cursorclass=pymysql.cursors.DictCursor
        )

        print("✅ Connected to MySQL")

        cursor = db.cursor()

        # Auto-create table permanently
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender VARCHAR(100),
            receiver VARCHAR(100),
            amount DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        db.commit()

        print("✅ transactions table ready")

        break

    except Exception as e:
        print("❌ Database connection failed:", e)
        time.sleep(5)

# =========================
# HOME ROUTE
# =========================

@app.route("/")
def home():
    return jsonify({
        "message": "SmartPay Backend Running Successfully"
    })

# =========================
# SEND MONEY API
# =========================

@app.route("/send", methods=["POST"])
def send_money():

    data = request.json

    sender = data.get("sender")
    receiver = data.get("receiver")
    amount = data.get("amount")

    try:
        cursor = db.cursor()

        query = """
        INSERT INTO transactions(sender, receiver, amount)
        VALUES(%s, %s, %s)
        """

        cursor.execute(query, (sender, receiver, amount))

        db.commit()

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

    try:
        cursor = db.cursor()

        cursor.execute("""
        SELECT * FROM transactions
        ORDER BY id DESC
        """)

        result = cursor.fetchall()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)