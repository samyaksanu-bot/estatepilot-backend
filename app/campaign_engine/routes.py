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

@router.post("/{campaign_id}/images")
async def generate_images(campaign_id: str):
    try:
        return generate_images_for_campaign(campaign_id)
    except Exception as e:
        logger.error(str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Image generation failed")

    """
    Trigger image generation for an existing campaign.
    This endpoint is async-safe and retryable.
    """
    try:
        # 1. Fetch campaign from DB
        res = supabase.table("campaigns").select("*").eq("id", campaign_id).single().execute()
        campaign = res.data

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # 2. Update image status → GENERATING
        supabase.table("campaigns").update({
            "image_status": "GENERATING"
        }).eq("id", campaign_id).execute()

        # 3. Generate images (isolated call)
        images = generate_images_for_campaign(campaign_id)

        # 4. Persist results
        supabase.table("campaigns").update({
            "image_assets": images,
            "image_status": "READY"
        }).eq("id", campaign_id).execute()

        return {
            "campaign_id": campaign_id,
            "status": "IMAGES_READY",
            "image_assets": images
        }

    except Exception as e:
        logger.error(str(e), exc_info=True)

        # Mark failed but recoverable
        supabase.table("campaigns").update({
            "image_status": "FAILED"
        }).eq("id", campaign_id).execute()

        raise HTTPException(
            status_code=500,
            detail="Image generation failed. Retry allowed."
        )
