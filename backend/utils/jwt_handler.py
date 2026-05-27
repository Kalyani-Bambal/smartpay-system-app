import jwt
import datetime

SECRET_KEY = "smartpay-secret-key"

def generate_token(user_id):

    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")