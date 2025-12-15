from supabase import create_client
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

supabase = None

def init_supabase():
    global supabase

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.error("❌ SUPABASE_URL or SUPABASE_KEY missing")
        return None

    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("✅ Supabase connected successfully")
        return supabase
    except Exception as e:
        logger.error(f"❌ Supabase init failed: {e}", exc_info=True)
        supabase = None
        return None


# Initialize on import
init_supabase()
