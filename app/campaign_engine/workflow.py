from app.database import supabase
from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint


def generate_strategy_only(payload: dict) -> dict:
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
from app.campaign_engine.image_engine import generate_sdxl_images


def generate_images_for_campaign(campaign_id: str) -> dict:
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

    images = generate_sdxl_images(blueprint)

    supabase.table("campaigns").update({
        "image_status": "completed",
        "images": images
    }).eq("id", campaign_id).execute()

    return {
        "campaign_id": campaign_id,
        "image_status": "completed",
        "images": images
    }
