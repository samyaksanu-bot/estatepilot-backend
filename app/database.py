from supabase import create_client, Client
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

supabase: Client | None = None

try:
    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
    logger.info("✅ Supabase client initialized")
except Exception as e:
    logger.error(f"❌ Supabase init failed: {str(e)}")
    supabase = None
