# backend/app/utils.py

from datetime import datetime, timedelta

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jose import jwt
from pydantic import EmailStr

from app.config import settings

# --- Email Connection Configuration ---
# This configuration object reads email server settings from your .env file
# via the global `settings` instance. It's used by FastMail to connect to
# your email provider's SMTP server.
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


def create_password_reset_token(email: str) -> str:
    """
    Creates a short-lived and scoped JSON Web Token (JWT) for password resets.

    Args:
        email: The email address of the user requesting the reset.

    Returns:
        A signed JWT string that can be sent to the user.
    """
    # Set a short expiration time (e.g., 30 minutes) for the token.
    expire = datetime.utcnow() + timedelta(minutes=30)

    # The token payload includes the expiration time, the user's email (subject),
    # and a "scope". The scope is a crucial security measure to ensure this token
    # can ONLY be used for resetting a password and not for general API access.
    to_encode = {"exp": expire, "sub": email, "scope": "password_reset"}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def send_password_reset_email(email: EmailStr, token: str):
    """
    Constructs and sends a password reset email to the user.

    This function is designed to be run as a background task so it doesn't
    block the API response.

    Args:
        email: The recipient's email address.
        token: The password reset JWT to be included in the reset link.
    """
    # Construct the full URL for the password reset page on the frontend.
    reset_url = f"{settings.FRONTEND_URL}/Reset_Password?token={token}"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 30px;">
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your Health Companion account.</p>
            <p>Please click the button below to set a new password. This link is valid for 30 minutes.</p>
            <a href="{reset_url}"
               style="background-color: #0068C9; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; font-weight: bold;">
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
        subject="Health Companion: Your Password Reset Link",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"Password reset email sent successfully to {email}")
    except Exception as e:
        # It's important to log errors in background tasks for debugging.
        print(f"Failed to send password reset email to {email}. Error: {e}")
