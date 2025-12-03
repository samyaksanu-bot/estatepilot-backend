# app/campaign_engine/audience_builder.py

def build_audience(project: dict, intent_profile: dict) -> dict:
    """
    Builds a Meta-safe audience plan.
    This does NOT publish ads.
    It only defines how delivery should be constrained.
    """

    location = intent_profile["location"]
    intent_level = intent_profile["intent_level"]
    property_type = intent_profile["property_type"]

    # -------- 1. GEO TARGETING --------
    # Tight geo keeps relevance high
    if property_type == "plot":
        geo_radius_km = 5
    else:
        geo_radius_km = 8

    geo_targeting = {
        "location_name": location,
        "radius_km": geo_radius_km,
        "reason": "Buyers outside this radius rarely convert for real estate"
    }

    # -------- 2. LANGUAGE & CONTEXT --------
    language = "English + Hindi"
    context_note = "Use simple, local language. Avoid corporate tone."

    # -------- 3. PLACEMENT CONTROL --------
    if intent_level == "high":
        placements = {
            "facebook_feed": True,
            "instagram_feed": True,
            "instagram_reels": False,
            "audience_network": False,
            "messenger": False
        }
        placement_reason = "Restrict to high-attention placements only"
    else:
        placements = {
            "facebook_feed": True,
            "instagram_feed": True,
            "instagram_reels": True,
            "audience_network": False,
            "messenger": False
        }
        placement_reason = "Balanced delivery for discovery + intent"
    
    # -------- 4. TARGETING EXPANSION --------
    expansion_allowed = False if intent_level == "high" else True

    # -------- 5. HOUSING AD CATEGORY NOTE --------
    compliance_notes = [
        "Special Ad Category: Housing",
        "No age, gender, income targeting",
        "No discriminatory exclusions"
    ]

    # -------- 6. FINAL AUDIENCE PLAN --------
    return {
        "geo_targeting": geo_targeting,
        "language": language,
        "context_note": context_note,
        "placements": placements,
        "placement_reason": placement_reason,
        "expansion_allowed": expansion_allowed,
        "compliance_notes": compliance_notes
    }
