# app/campaign_engine/workflow.py

from typing import Dict, Any
from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.image_engine import generate_sdxl_images


def _safe_dict(v):
    return v if isinstance(v, dict) else {}


def generate_full_campaign_plan(project_payload: Dict[str, Any]) -> Dict[str, Any]:

    # 1. Project brief
    try:
        brief = build_project_brief(project_payload) or {}
    except Exception as e:
        return {"status": "ERROR", "error": f"project_brief_exception: {str(e)}"}

    brief = _safe_dict(brief)

    # 2. Strategy
    try:
        strategy = generate_strategy(brief) or {}
    except Exception as e:
        strategy = {"error": f"generate_strategy_exception: {str(e)}"}

    strategy = _safe_dict(strategy)

    # 3. Creative blueprint
    try:
        creative_blueprint = generate_creative_blueprint(brief, strategy) or {}
    except Exception as e:
        creative_blueprint = {"error": f"creative_blueprint_exception: {str(e)}"}

    creative_blueprint = _safe_dict(creative_blueprint)

    # 4. Image generation (THE MOTOR)
    try:
        image_assets = generate_sdxl_images(creative_blueprint) or []
    except Exception as e:
        image_assets = [{
            "status": "placeholder",
            "error": f"image_generation_exception: {str(e)}"
        }]

    # 5. Final creative
    first_image = image_assets[0] if image_assets else {}

    final_creative = {
        "template_id": creative_blueprint.get("final_visual_recipe", {}).get(
            "template_hint", "PLACEHOLDER"
        ),
        "background_image": first_image.get("url") or first_image.get("base64"),
        "headline": creative_blueprint.get("headline") or brief.get("project_name"),
        "cta": creative_blueprint.get("cta") or "Check Availability on WhatsApp",
        "price": None
    }

    if brief.get("price_min_lakh") and brief.get("price_max_lakh"):
        final_creative["price"] = f"{brief['price_min_lakh']}–{brief['price_max_lakh']} Lakh"

    # 6. Final campaign plan
    final_campaign_plan = {
        "campaign_name": strategy.get(
            "campaign_name",
            f"{brief.get('project_name', 'Project')} Lead Campaign"
        ),
        "objective": "LEAD_GENERATION",
        "ad_sets": [{
            "adset_name": "Primary Audience Set",
            "target_radius_km": strategy.get("targeting", {}).get("target_radius_km"),
            "age_range": strategy.get("targeting", {}).get("age_filter"),
            "behaviors": strategy.get("targeting", {}).get("behavior_filters"),
            "exclusions": strategy.get("targeting", {}).get("exclusions"),
            "placements": strategy.get("placements"),
            "budget_recommendation": strategy.get("budget_plan"),
        }],
        "lead_form_structure": strategy.get("lead_form"),
        "ad_creatives": {
            "blueprint": creative_blueprint,
            "generated_images": image_assets
        },
        "messaging_pillars": strategy.get("messaging_pillars"),
        "whatsapp_bot_notes": strategy.get("whatsapp_bot_notes")
    }

    return {
        "status": "SUCCESS",
        "project_brief": brief,
        "strategy": strategy,
        "creative_blueprint": creative_blueprint,
        "image_assets": image_assets,
        "final_creative": final_creative,
        "final_campaign_plan": final_campaign_plan
    }
