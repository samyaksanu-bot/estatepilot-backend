import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
    META_APP_ID = os.getenv("META_APP_ID")
    META_APP_SECRET = os.getenv("META_APP_SECRET")

    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    JWT_SECRET = os.getenv("JWT_SECRET", "secret")
    JWT_ALGORITHM = "HS256"

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # ✅ FIXED

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
