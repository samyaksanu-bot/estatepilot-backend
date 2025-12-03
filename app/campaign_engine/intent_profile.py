# app/campaign_engine/intent_profile.py

def build_buyer_intent_profile(project: dict, strategy: dict) -> dict:
    """
    Creates a single source of truth
    about the buyer we want.
    """

    intent_level = strategy["intent_level"]

    if intent_level == "high":
        planning_timeline = "0-6 months"
        disqualifiers = [
            "brokers",
            "budget below range",
            "just browsing"
        ]
    else:
        planning_timeline = "6-12 months"
        disqualifiers = [
            "brokers"
        ]

    return {
        "intent_level": intent_level,
        "buyer_type": project.get("buyer_type", "end_user"),
        "budget_range": [
            project.get("price_min_lakh"),
            project.get("price_max_lakh")
        ],
        "planning_timeline": planning_timeline,
        "disqualifiers": disqualifiers,
        "property_type": project.get("type"),
        "location": project.get("location")
    }
