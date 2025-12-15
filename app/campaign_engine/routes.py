# app/campaign_engine/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.campaign_engine.workflow import (
    generate_strategy_only,
    generate_images_for_campaign
)
from app.database import supabase
from app.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/campaign", tags=["Campaign Engine"])


class ProjectPayload(BaseModel):
    project_name: str
    location: str
    price_min_lakh: Optional[float] = None
    price_max_lakh: Optional[float] = None
    property_type: Optional[str] = "flat"
    amenities: Optional[List[str]] = []
    unit_types: Optional[List[str]] = []
    notes: Optional[str] = ""


@router.post("/generate")
async def generate_campaign(payload: ProjectPayload):
    try:
        campaign = generate_strategy_only(payload.dict())

        return {
            "campaign_id": campaign["id"],
            "status": "STRATEGY_READY",
            "project_brief": campaign["brief"],
            "strategy": campaign["strategy"],
            "creative_blueprint": campaign["creative_blueprint"],
            "image_status": campaign["image_status"]
        }

    except Exception as e:
        logger.error(str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Campaign generation failed")
f
