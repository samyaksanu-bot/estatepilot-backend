from fastapi import APIRouter

from app.campaign_engine.campaign_preview import generate_campaign_preview

router = APIRouter(prefix="/campaign", tags=["Campaign Preview"])


@router.post("/debug/preview")
async def debug_campaign_preview(payload: dict):
    """
    Debug-only campaign preview.
    Does NOT touch WhatsApp or Meta.
    """
    return generate_campaign_preview(payload)
