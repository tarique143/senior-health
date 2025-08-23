# backend/app/utils.py (Corrected)

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.config import settings
from jose import jwt  # <-- BADLAV YAHAN HUA HAI
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
    """Creates a short-lived JWT for password reset."""
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"exp": expire, "sub": email, "scope": "password_reset"}
    # Yahan 'jwt' ab 'jose' se aa raha hai
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def send_password_reset_email(email: EmailStr, token: str):
    """Sends the password reset email to the user."""
    
    reset_url = f"{settings.FRONTEND_URL}/Reset_Password?token={token}"
    
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your Health Companion account.</p>
            <p>Please click the button below to set a new password. This link is valid for 30 minutes.</p>
            <a href="{reset_url}" 
               style="background-color: #0068C9; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px;">
               Reset Your Password
            </a>
            <p style="margin-top: 30px; font-size: 12px; color: #888;">
                If you did not request a password reset, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Health Companion: Password Reset Link",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
