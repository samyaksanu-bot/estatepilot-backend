# app/campaign_engine/campaign_preview.py

from app.campaign_engine.strategy import decide_campaign_strategy
from app.campaign_engine.intent_profile import build_buyer_intent_profile
from app.campaign_engine.creative_brief import generate_creative_brief
from app.campaign_engine.caption_generator import generate_caption
from app.campaign_engine.audience_builder import build_audience


def generate_campaign_preview(project: dict) -> dict:
    """
    Runs the full campaign brain and returns
    a preview of what will be launched.
    """

    # 1. Decide campaign strategy
    strategy = decide_campaign_strategy(project)

    # 2. Build buyer intent profile
    intent_profile = build_buyer_intent_profile(project, strategy)

    # 3. Generate creative thinking (designer brain)
    creative_brief = generate_creative_brief(project, intent_profile)

    # 4. Generate captions (copywriter brain)
    captions = generate_caption(project, intent_profile, creative_brief)

    # 5. Build audience plan (media buyer brain)
    audience_plan = build_audience(project, intent_profile)

    return {
        "project_name": project.get("name", "Unnamed Project"),
        "strategy": strategy,
        "intent_profile": intent_profile,
        "creative_brief": creative_brief,
        "captions": captions,
        "audience_plan": audience_plan,
        "note_to_owner": (
            "This campaign is intentionally designed to attract fewer "
            "but higher-intent buyers. Lead volume may be lower, "
            "but quality and site-visit readiness will be higher."
        )
    }
