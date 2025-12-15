from typing import Dict
from app.database import supabase
from app.logger import setup_logger
from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.image_engine import generate_sdxl_images

logger = setup_logger(__name__)


def generate_strategy_only(payload: dict) -> Dict:
    brief = build_project_brief(payload)
    strategy = generate_strategy(brief)
    blueprint = generate_creative_blueprint(brief, strategy)

    result = supabase.table("campaigns").insert({
        "brief": brief,
        "strategy": strategy,
        "blueprint": blueprint,
        "image_status": "pending"
    }).execute()

    campaign = result.data[0]

    return {
        "id": campaign["id"],
        "brief": brief,
        "strategy": strategy,
        "creative_blueprint": blueprint,
        "image_status": campaign["image_status"]
    }


def generate_images_for_campaign(campaign_id: str) -> Dict:
    record = (
        supabase
        .table("campaigns")
        .select("*")
        .eq("id", campaign_id)
        .single()
        .execute()
    )

    if not record.data:
        raise ValueError("Campaign not found")

    blueprint = record.data["blueprint"]

    try:
        images = generate_sdxl_images(blueprint)
        status = "completed"
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}", exc_info=True)
        images = []
        status = "failed"

    supabase.table("campaigns").update({
        "image_status": status,
        "images": images
    }).eq("id", campaign_id).execute()

    return {
        "campaign_id": campaign_id,
        "image_status": status,
        "images": images
    }
