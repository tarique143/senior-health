# backend/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Manages application settings by loading them from a .env file.
    This centralized approach makes configuration management easy and secure.
    """
    # Configure Pydantic to load settings from a file named '.env'
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Database Settings ---
    # The connection string for your database.
    # Example for PostgreSQL: "postgresql://user:password@host:port/dbname"
    DATABASE_URL: str

    # --- JWT Authentication Settings ---
    # A secret key for signing JWTs. Should be long, random, and kept secret.
    # You can generate one with: `openssl rand -hex 32`
    SECRET_KEY: str
    # The algorithm used to sign the JWT (e.g., "HS256").
    ALGORITHM: str
    # Default lifetime of a standard access token in minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    # Lifetime of a "remember me" access token in days.
    ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER: int

    # --- Email Settings ---
    # These are required for sending password reset emails and daily reminders.
    # If using Gmail, use a Google App Password for MAIL_PASSWORD.
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    # --- Frontend Settings ---
    # The base URL of your Streamlit frontend.
    # This is crucial for creating correct password reset links.
    FRONTEND_URL: str


# Create a single, global instance of the Settings class.
# This 'settings' object will be imported into other files
# to access configuration values.
settings = Settings()
