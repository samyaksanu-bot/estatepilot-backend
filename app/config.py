# app/config.py

import os
from dotenv import load_dotenv

# Load environment variables (.env locally, Render env in prod)
load_dotenv()


class Settings:
    """
    Central configuration object.
    Keep this SIMPLE and explicit.
    """

    # --------------------------------------------------
    # Environment
    # --------------------------------------------------
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # --------------------------------------------------
    # OpenAI
    # --------------------------------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # --------------------------------------------------
    # WhatsApp / Meta
    # --------------------------------------------------
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
    META_APP_ID = os.getenv("META_APP_ID")
    META_APP_SECRET = os.getenv("META_APP_SECRET")

    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "verify_token")

    # --------------------------------------------------
    # Supabase
    # --------------------------------------------------
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # --------------------------------------------------
    # JWT
    # --------------------------------------------------
    JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-production")
    JWT_ALGORITHM = "HS256"


# Singleton settings object
settings = Settings()

