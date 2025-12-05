from app.campaign_engine.intent_profile import build_intent_profile
from app.campaign_engine.creative_brief import generate_creative_brief
from app.campaign_engine.audience_builder import build_audience_plan
from app.campaign_engine.strategy import build_campaign_strategy


def generate_campaign_preview(project: dict) -> dict:
    """
    SAFE campaign preview generator.
    Nothing runs at import time.
    """

    # Step 1: intent inference
    intent_profile = build_intent_profile(project)

    # Step 2: strategy
    strategy = build_campaign_strategy(project, intent_profile)

    # Step 3: creative
    creative_brief = generate_creative_brief(
        project=project,
        intent_profile=intent_profile
    )

    # Step 4: audience
    audience_plan = build_audi
