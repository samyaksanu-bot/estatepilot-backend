def build_audience_plan(project: dict, intent_profile: dict) -> dict:
    """
    Build audience plan from project + intent signals.
    This function MUST exist because campaign_preview imports it.
    """

    location = intent_profile.get("location", project.get("location", "Not specified"))

    radius_km = 8
    reason = "Buyers outside this radius rarely convert for real estate"

    placements = {
        "facebook_feed": True,
        "instagram_feed": True,
        "instagram_reels": True,
        "audience_network": False,
        "messenger": False
    }

    return {
        "geo_targeting": {
            "location_name": location,
            "radius_km": radius_km,
            "reason": reason
        },
        "language": "English + Hindi",
        "context_note": "Use simple, local language. Avoid corporate tone.",
        "placements": placements,
        "placement_reason": "Balanced delivery for discovery + intent",
        "expansion_allowed": True,
        "compliance_notes": [
            "Special Ad Category: Housing",
            "No age, gender, income targeting",
            "No discriminatory exclusions"
        ]
    }
