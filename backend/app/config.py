# backend/app/config.py (Updated Version)

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings by loading them from a .env file.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Database Settings ---
    DATABASE_URL: str

    # --- JWT Authentication Settings ---
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- Email Settings ---
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    # --- Frontend Settings (THIS IS THE NEW ADDITION) ---
    FRONTEND_URL: str

# We create a single, global instance of the Settings class.
# We will import this 'settings' object into other files.
settings = Settings()
