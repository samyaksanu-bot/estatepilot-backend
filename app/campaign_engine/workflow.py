from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.image_engine import generate_sdxl_images
import uuid


def generate_strategy_only(payload: dict) -> dict:
    brief = build_project_brief(payload)
    strategy = generate_strategy(brief)
    blueprint = generate_creative_blueprint(brief, strategy)

    campaign_id = str(uuid.uuid4())

    return {
        "id": campaign_id,
        "brief": brief,
        "strategy": strategy,
        "creative_blueprint": blueprint,
        "image_status": "NOT_STARTED"
    }


def generate_images_for_campaign(creative_blueprint: dict) -> dict:
    images = generate_sdxl_images(creative_blueprint)

    return {
        "image_status": "COMPLETED",
        "images": images
    }
