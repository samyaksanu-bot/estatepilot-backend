def generate_strategy(brief: dict) -> dict:
    """
    Minimal placeholder strategy engine.
    No GPT yet.
    Only returns the required keys so the system does not break.
    """

    # fallback values (we will replace these later)
    return {
        "intent_level": "medium",
        "property_type": "flat",
        "target_radius_km": 5,
        "age_filter": [28, 55],
        "behavior_filters": ["likely_to_move"],
        "exclusions": ["agents", "brokers"],
        "placements": {
            "facebook_feed": True,
            "instagram_feed": True,
            "instagram_reels": True,
            "audience_network": False
        },
        "budget_plan": {"daily": 1000},
        "lead_form": [
            {"id": "budget", "text": "What is your budget?"},
            {"id": "timeline", "text": "When do you plan to buy?"},
        ],
        "messaging_pillars": ["location", "price", "lifestyle"],
        "whatsapp_bot_notes": {
            "highlight_price": True,
            "highlight_location": True
        }
    }
