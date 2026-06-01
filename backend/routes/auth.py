from flask import Blueprint, request, jsonify
import bcrypt

from db import get_db_connection
from utils.jwt_handler import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.json

        if not data or not data.get("username") or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Missing required fields"}), 400

        username = data["username"]
        email = data["email"]
        password = data["password"]

        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO users(username,email,password_hash)
            VALUES(%s,%s,%s)
            """,
            (username, email, hashed.decode())
        )

        db.commit()
        cursor.close()
        db.close()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except Exception as e:
        error_msg = str(e)
        if "Duplicate entry" in error_msg or "unique constraint" in error_msg.lower():
            return jsonify({"error": "Username or email already exists"}), 409
        return jsonify({"error": f"Registration failed: {error_msg}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json

        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Missing required fields"}), 400

        email = data["email"]
        password = data["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            cursor.close()
            db.close()
            return jsonify({
                "error": "User not found"
            }), 404

        valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not valid:
            cursor.close()
            db.close()
            return jsonify({
                "error": "Invalid password"
            }), 401

        token = generate_token(user["id"])
        cursor.close()
        db.close()

        return jsonify({
            "token": token,
            "username": user["username"]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500