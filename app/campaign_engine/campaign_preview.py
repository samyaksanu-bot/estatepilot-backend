from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.image_engine import generate_sdxl_images


def generate_campaign_preview(project: dict) -> dict:
    """
    SAFE, DRY-RUN-ONLY PREVIEW.
    Used only for debugging or builder preview.
    Does NOT affect WhatsApp Bot or any live logic.
    """

    # 1. Clean brief + missing-data warnings
    brief = build_project_brief(project)

    # 2. Strategy (GPT-4.0)
    strategy = generate_strategy(brief)

    # 3. Creative blueprint (GPT-4.0)
    creative_blueprint = generate_creative_blueprint(brief, strategy)

    # 4. Visual mockups (SDXL)
    image_outputs = generate_sdxl_images(creative_blueprint)

    return {
        "status": "PREVIEW_OK",
        "brief": brief,
        "strategy": strategy,
        "creative_blueprint": creative_blueprint,
        "images": image_outputs
    }
 "audience_plan": audience_plan
    }

