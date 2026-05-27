from flask import Blueprint, jsonify

receipt_bp = Blueprint("receipt", __name__)

@receipt_bp.route("/receipt/<id>", methods=["GET"])
def receipt(id):

    return jsonify({
        "message": f"Receipt generated for transaction {id}"
    })