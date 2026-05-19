from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import uuid

app = Flask(__name__)
CORS(app)

# RDS MySQL connection
db = pymysql.connect(
    host="smartpay-mysql-rds.c3yc888c4lqk.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="Smartpay123#",
    database="smartpaydb"
)

# -----------------------------
# CREATE TRANSACTION API
# -----------------------------
@app.route('/transfer', methods=['POST'])
def transfer_money():

    data = request.json

    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']

    transaction_id = str(uuid.uuid4())[:8]

    cursor = db.cursor()

    query = """
    INSERT INTO transactions
    (transaction_id, sender_name, receiver_name, amount, status)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        transaction_id,
        sender,
        receiver,
        amount,
        "SUCCESS"
    )

    cursor.execute(query, values)

    db.commit()

    return jsonify({
        "message": "Transaction Successful",
        "transaction_id": transaction_id
    })


# -----------------------------
# GET ALL TRANSACTIONS
# -----------------------------
@app.route('/transactions', methods=['GET'])
def get_transactions():

    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")

    result = cursor.fetchall()

    return jsonify(result)


# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)