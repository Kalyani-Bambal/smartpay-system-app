from flask import Blueprint, jsonify

from db import get_db_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/transactions", methods=["GET"])
def all_transactions():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM transactions")

    data = cursor.fetchall()

    return jsonify(data)

@admin_bp.route("/admin/failed", methods=["GET"])
def failed_transactions():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM transactions WHERE status='failed'"
    )

    data = cursor.fetchall()

    return jsonify(data)