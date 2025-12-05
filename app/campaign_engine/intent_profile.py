def build_intent_profile(project: dict) -> dict:
    """
    Builds buyer intent profile from project data.
    This function MUST exist because campaign_preview depends on it.
    """

    property_type = project.get("type", "flat")
    location = project.get("location", "Not specified")

    price_min = project.get("price_min_lakh")
    price_max = project.get("price_max_lakh")

    # ---- intent heuristics ----
    if price_min and price_max and price_max <= 40:
        intent_level = "medium"
        planning_timeline = "6-12 months"
    elif price_min and price_max:
        intent_level = "high"
        planning_timeline = "0-6 months"
    else:
        intent_level = "low"
        planning_timeline = "12+ months"

    return {
        "intent_level": intent_level,
        "buyer_type": "end_user",
        "property_type": property_type,
        "location": location,
        "budget_min": price_min,
        "budget_max": price_max,
        "planning_timeline": planning_timeline,
        "disqualifiers": ["brokers"]
    }
