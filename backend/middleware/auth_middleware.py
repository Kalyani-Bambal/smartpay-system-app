from flask import request, jsonify

def authenticate():

    token = request.headers.get("Authorization")

    if not token:
        return jsonify({
            "error": "Unauthorized"
        }), 401