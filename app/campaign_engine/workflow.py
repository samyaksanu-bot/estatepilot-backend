# app/campaign_engine/workflow.py

from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.campaign_engine.template_selector import select_visual_template
from app.campaign_engine.static_image_generator import generate_static_image_spec
from app.campaign_engine.image_engine import generate_sdxl_images


def generate_full_campaign_plan(project_payload: dict) -> dict:
    """
    MASTER ORCHESTRATOR FOR ESTATEPILOT PILLAR 2
    -------------------------------------------------------
    FINAL PIPELINE:
    1. Build Project Brief
    2. Generate Strategy (GPT-4.1)
    3. Create Creative Blueprint (GPT-4.1 strict, no hallucination)
    4. Select visual template (rules-based)
    5. Build static image spec for SDXL
    6. Generate SDXL images (stub or real model)
    7. Build complete campaign plan
    """

    # ---------------------------------------------------
    # STEP 1 — CLEAN + VALIDATE BUILDER INPUT
    # ---------------------------------------------------
    brief = build_project_brief(project_payload)

    # ---------------------------------------------------
    # STEP 2 — META ADS STRATEGY ENGINE (GPT-4.1)
    # ---------------------------------------------------
    strategy = generate_strategy(brief)

    # ---------------------------------------------------
    # STEP 3 — CREATIVE BLUEPRINT (GPT-4.1, strict factual)
    # ---------------------------------------------------
    creative_blueprint = generate_creative_blueprint(brief, strategy)

    # ---------------------------------------------------
    # STEP 4 — TEMPLATE SELECTION (pure logic, no hallucination)
    # ---------------------------------------------------
    template_selection = select_visual_template(creative_blueprint)

    # ---------------------------------------------------
    # STEP 5 — STATIC IMAGE SPEC (final SDXL instructions)
    # ---------------------------------------------------
    image_spec = generate_static_image_spec(
        creative_blueprint=creative_blueprint,
        template_selection=template_selection,
        brief=brief
    )

    # ---------------------------------------------------
    # STEP 6 — SDXL IMAGE GENERATION (stub or real model)
    # ---------------------------------------------------
    images = generate_sdxl_images(image_spec)

    # ---------------------------------------------------
    # STEP 7 — FINAL MANUAL META CAMPAIGN PLAN
    # ---------------------------------------------------
    final_campaign_plan = {
        "campaign_name": strategy.get("campaign_name", f"{brief.get('project_name', 'Project')} Lead Campaign"),
        "objective": "LEAD_GENERATION",

        "ad_sets": [
            {
                "adset_name": "Primary Audience Set",
                "target_radius_km": strategy.get("targeting", {}).get("target_radius_km"),
                "age_range": strategy.get("targeting", {}).get("age_filter"),
                "behaviors": strategy.get("targeting", {}).get("behavior_filters"),
                "exclusions": strategy.get("targeting", {}).get("exclusions"),
                "placements": strategy.get("placements"),
                "budget_recommendation": strategy.get("budget_plan")
            }
        ],

        "lead_form_structure": strategy.get("lead_form"),

        "ad_creatives": {
            "blueprint": creative_blueprint,
            "template": template_selection,
            "image_spec": image_spec,
            "generated_images": images
        },

        "messaging_pillars": strategy.get("messaging_pillars"),
        "whatsapp_bot_notes": strategy.get("whatsapp_bot_notes")
    }

    # ---------------------------------------------------
    # RETURN FINAL RESPONSE
    # ---------------------------------------------------
    return {
        "status": "SUCCESS",

        "project_brief": brief,
        "strategy": strategy,
        "creative_blueprint": creative_blueprint,

        "template_used": template_selection,
        "image_spec": image_spec,
        "image_assets": images,

        "final_campaign_plan": final_campaign_plan
    }

