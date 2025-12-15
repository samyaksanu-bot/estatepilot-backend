from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.campaign_engine.workflow import (
    generate_strategy_only,
    generate_images_for_campaign
)
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/campaign",
    tags=["Campaign Engine"]
)


# -------------------------------------------------------------------
# Request Schema
# -------------------------------------------------------------------

class ProjectPayload(BaseModel):
    project_name: str
    location: str
    price_min_lakh: Optional[float] = None
    price_max_lakh: Optional[float] = None
    property_type: Optional[str] = "flat"
    amenities: Optional[List[str]] = []
    unit_types: Optional[List[str]] = []
    notes: Optional[str] = ""


# -------------------------------------------------------------------
# 1️⃣ Campaign Strategy Generation (FAST, NO IMAGES)
# -------------------------------------------------------------------

@router.post("/generate")
async def generate_campaign(payload: ProjectPayload):
    """
    Creates campaign record with:
    - project brief
    - strategy
    - creative blueprint
    Images are NOT generated here.
    """

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
        logger.error("Campaign generation failed", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Campaign strategy generation failed"
        )


# -------------------------------------------------------------------
# 2️⃣ Image Generation (ISOLATED, RETRYABLE)
# -------------------------------------------------------------------

@router.post("/{campaign_id}/images")
async def generate_campaign_images(campaign_id: str):
    """
    Generates images for an existing campaign.
    Can be retried safely.
    Never blocks campaign creation.
    """

    try:
        result = generate_images_for_campaign(campaign_id)

        return {
            "campaign_id": campaign_id,
            "status": result["image_status"],
            "images": result["images"]
        }

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    except Exception as e:
        logger.error("Image generation failed", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Image generation failed. Retry allowed."
        )
