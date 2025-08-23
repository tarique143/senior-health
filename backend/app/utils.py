# backend/app/utils.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from .config import settings
import jwt
from datetime import datetime, timedelta

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

def create_password_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"exp": expire, "sub": email, "scope": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def send_password_reset_email(email: EmailStr, token: str):
    reset_url = f"{settings.FRONTEND_URL}/Reset_Password?token={token}"
    html_content = f"""
    <html><body>
        <p>Please click the button below to reset your password.</p>
        <a href="{reset_url}" style="background-color: #0068C9; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px;">
           Reset Your Password
        </a>
    </body></html>
    """
    message = MessageSchema(
        subject="Health Companion: Password Reset Link",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
