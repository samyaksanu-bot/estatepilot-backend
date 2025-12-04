# app/campaign_engine/campaign_preview.py

from app.campaign_engine.strategy import decide_campaign_strategy
from app.campaign_engine.intent_profile import build_buyer_intent_profile
from app.campaign_engine.creative_brief import generate_creative_brief
from app.campaign_engine.caption_generator import generate_caption
from app.campaign_engine.audience_builder import build_audience


def generate_campaign_preview(project: dict) -> dict:
    """
    SAFE preview generator.
    Never crashes on missing intent profile.
    """

    try:
        creative_decision = generate_creative_brief(
            project,
            intent_profile={}
        )
    except Exception as e:
        return {
            "status": "ERROR",
            "reason": "creative_brief_failed",
            "details": str(e),
        }

    return {
        "status": "OK",
        "creative_decision": creative_decision,
    }
