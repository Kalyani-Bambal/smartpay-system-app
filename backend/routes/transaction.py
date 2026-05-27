from flask import Blueprint, request, jsonify

from db import get_db_connection

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/send-money", methods=["POST"])
def send_money():

    data = request.json

    sender = data["sender"]
    receiver = data["receiver"]
    amount = data["amount"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO transactions
        (sender_name, receiver_name, amount, status)
        VALUES(%s,%s,%s,%s)
        """,
        (sender, receiver, amount, "completed")
    )

    db.commit()

    return jsonify({
        "message": "Money sent successfully"
    })

@transaction_bp.route("/transactions", methods=["GET"])
def transactions():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM transactions ORDER BY created_at DESC"
    )

    data = cursor.fetchall()

    return jsonify(data)