def build_campaign_strategy(project: dict, intent_profile: dict) -> dict:
    """
    Core campaign strategy evaluator.
    MUST exist because campaign_preview imports it.
    """

    price_min = project.get("price_min_lakh")
    price_max = project.get("price_max_lakh")

    # intent = high, medium, low
    intent_level = intent_profile.get("intent_level", "medium")

    # goal logic
    if intent_level == "high":
        campaign_goal = "lead_form"
        core_angle = "trust + urgency"
    elif intent_level == "medium":
        campaign_goal = "lead_form"
        core_angle = "trust + lifestyle"
    else:
        campaign_goal = "traffic"
        core_angle = "awareness + lifestyle"

    return {
        "intent_level": intent_level,
        "campaign_goal": campaign_goal,
        "core_angle": core_angle
    }
