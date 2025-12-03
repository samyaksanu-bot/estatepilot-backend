# app/campaign_engine/strategy.py

def decide_campaign_strategy(project: dict) -> dict:
    """
    Decides how serious the campaign should be
    based on project details.
    """

    price_min = project.get("price_min_lakh", 0)
    possession = project.get("possession", "unknown")
    project_type = project.get("type", "flat")

    # Default values
    intent_level = "medium"
    campaign_goal = "lead_form"
    core_angle = "trust"

    # High-intent rules
    if possession == "ready" and price_min >= 40:
        intent_level = "high"
        campaign_goal = "whatsapp_click"

    if project_type == "plot":
        core_angle = "price + location"

    if project_type == "flat":
        core_angle = "trust + lifestyle"

    return {
        "intent_level": intent_level,
        "campaign_goal": campaign_goal,
        "core_angle": core_angle
    }

