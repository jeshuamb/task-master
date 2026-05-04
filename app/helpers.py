import jwt
from app import db
from app.auth.models import User
from datetime import datetime, timedelta, timezone
from flask import current_app
from flask_mail import Message
from .extensions import mail
from .logger_config import logger

def send_reset_email(email, link):
    msg = Message(
        subject="Restablecer contraseña - TaskMaster",
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        recipients=[email]
    )

    msg.body = f"""
Hola, {email}
    
Para restablecer tu contraseña, haz clic en el siguiente enlace:

{link}

Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje.
"""

    try:
        mail.send(msg)
        return True
    except Exception:
        logger.exception(f"Error enviando reset email a {email}")
        return False

def reset_generation_token(user_id):
    user = User.get_user_by_id(user_id)

    user.reset_token_version += 1
    db.session.commit()

    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config["SECRET_KEY"]

    payload = {
        "user_id": user.id,
        "version": user.reset_token_version,  
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "type": "password_reset"
    }

    return jwt.encode(payload, secret, algorithm="HS256")


def verify_reset_token(token):
    try:
        secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config["SECRET_KEY"]
        data = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    user = User.get_user_by_id(data.get("user_id"))
    if not user:
        return None

    token_version = data.get("version")

    if token_version != user.reset_token_version:
        return None

    return user.id