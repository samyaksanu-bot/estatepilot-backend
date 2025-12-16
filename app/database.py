# app/database.py
import os
from supabase import create_client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

supabase = None

if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("✅ Supabase connected")
    except Exception as e:
        logger.error(f"❌ Supabase init failed: {e}")
else:
    logger.warning("⚠️ Supabase env vars missing")
