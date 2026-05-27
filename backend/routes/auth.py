from flask import Blueprint, request, jsonify
import bcrypt

from db import get_db_connection
from utils.jwt_handler import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.json

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

    return jsonify({
        "message": "User registered successfully"
    })

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

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
        return jsonify({
            "error": "User not found"
        }), 404

    valid = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not valid:
        return jsonify({
            "error": "Invalid password"
        }), 401

    token = generate_token(user["id"])

    return jsonify({
        "token": token,
        "username": user["username"]
    })