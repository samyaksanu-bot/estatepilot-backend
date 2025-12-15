# app/database.py

from supabase import create_client
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

supabase = None

try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("✅ Supabase client initialized")
    else:
        logger.warning("⚠️ Supabase env vars missing")

except Exception as e:
    logger.error(f"❌ Supabase init failed: {str(e)}")
    supabase = None

