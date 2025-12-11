# app/campaign_engine/workflow.py

from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.image_engine import generate_sdxl_images


def generate_full_campaign_plan(project_payload: dict) -> dict:
    """
    MASTER ORCHESTRATOR FOR ESTATEPILOT PILLAR 2
    -------------------------------------------------------
    Steps:
    1. Build Project Brief (validation + extraction)
    2. Strategy generation (GPT-4.0)
    3. Creative Blueprint generation (GPT-4.0)
    4. SDXL image generation
    5. Campaign Plan (for manual Meta setup)
    """

    # Step 1: Clean and validate builder input
    brief = build_project_brief(project_payload)

    # Step 2: Full Strategy
    strategy = generate_strategy(brief)

    # Step 3: Creative Blueprint
    creative_blueprint = generate_creative_blueprint(brief, strategy)

    # Step 4: SDXL image generation
    images = generate_sdxl_images(creative_blueprint)

    # Step 5: Meta Ads final manual setup blueprint
    final_campaign_plan = {
        "campaign_name": strategy.get("campaign_name", f"{brief.get('project_name', 'Project')} Lead Campaign"),
        "objective": "LEAD_GENERATION",
        "ad_sets": [
            {
                "adset_name": "Primary Audience Set",
                "target_radius_km": strategy.get("target_radius_km"),
                "age_range": strategy.get("age_filter"),
                "behaviors": strategy.get("behavior_filters"),
                "exclusions": strategy.get("exclusions"),
                "placements": strategy.get("placements"),
                "budget_recommendation": strategy.get("budget_plan"),
            }
        ],
        "lead_form_structure": strategy.get("lead_form"),
        "ad_creatives": {
            "blueprint": creative_blueprint,
            "generated_images": images
        },
        "messaging_pillars": strategy.get("messaging_pillars"),
        "whatsapp_bot_notes": strategy.get("whatsapp_bot_notes")
    }

    return {
        "status": "SUCCESS",
        "project_brief": brief,
        "strategy": strategy,
        "creative_blueprint": creative_blueprint,
        "image_assets": images,
        "final_campaign_plan": final_campaign_plan
    }
