from supabase import create_client
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase connected successfully")
except Exception as e:
    logger.critical(f"❌ Supabase connection failed: {e}")
    raise  # ⬅️ CRASH THE APP
