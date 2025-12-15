from typing import Dict, Any
from uuid import uuid4
from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.image_engine import generate_sdxl_images
from app.database import supabase
from app.logger import setup_logger

logger = setup_logger(__name__)


def generate_strategy_only(project_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    STEP 1
    - Generate brief
    - Generate strategy
    - Generate creative blueprint
    - Persist campaign
    """

    campaign_id = str(uuid4())

    brief = build_project_brief(project_payload)
    strategy = generate_strategy(brief)
    blueprint = generate_creative_blueprint(brief, strategy)

    record = {
        "id": campaign_id,
        "brief": brief,
        "strategy": strategy,
        "blueprint": blueprint,
        "image_status": "PENDING"
    }

    supabase.table("campaigns").insert(record).execute()

    return record


def generate_images_for_campaign(campaign_id: str) -> Dict[str, Any]:
    """
    STEP 2
    - Fetch campaign
    - Generate images
    - Update DB
    """

    res = (
        supabase
        .table("campaigns")
        .select("*")
        .eq("id", campaign_id)
        .single()
        .execute()
    )

    if not res.data:
        raise ValueError("Campaign not found")

    campaign = res.data

    images = generate_sdxl_images(campaign["blueprint"])

    supabase.table("campaigns").update(
        {
            "image_assets": images,
            "image_status": "DONE"
        }
    ).eq("id", campaign_id).execute()

    return {
        "campaign_id": campaign_id,
        "image_status": "DONE",
        "images": images
    }
