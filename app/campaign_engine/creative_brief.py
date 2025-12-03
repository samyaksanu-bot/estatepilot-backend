# app/campaign_engine/creative_brief.py

def generate_creative_brief(project: dict, intent_profile: dict) -> dict:
    """
    Acts like a senior real-estate graphic designer.
    Decides WHAT the creative should communicate and HOW.
    """

    intent_level = intent_profile["intent_level"]
    property_type = intent_profile["property_type"]
    price_min, price_max = intent_profile["budget_range"]

    # ----- 1. Creative Personality -----
    if intent_level == "high":
        design_tone = "serious, clean, trust-focused"
    else:
        design_tone = "informative, welcoming, simple"

    # ----- 2. Visual Layout Decision -----
    if property_type == "plot":
        visual_layout = "site layout + location map"
        headline_style = "bold text, high clarity"
    else:
        visual_layout = "elevation + amenities snapshot"
        headline_style = "balanced text with lifestyle cues"

    # ----- 3. Color Psychology (important) -----
    if intent_level == "high":
        color_palette = "neutral colors, white background, dark text"
    else:
        color_palette = "light colors, soft contrast"

    # ----- 4. Mandatory Elements (must be visible) -----
    must_show = [
        f"Price range: ₹{price_min}–{price_max} lakh",
        "Exact location or nearest landmark",
        "Project type clarity (plot / flat)",
    ]

    # Possession clarity increases trust
    if project.get("possession") == "ready":
        must_show.append("Ready to register")

    # ----- 5. Disallowed Elements (designer discipline) -----
    must_not_show = [
        "fake luxury imagery",
        "celebrity photos",
        "over-promising words like 'best' or 'no.1'",
        "misleading lifestyle visuals"
    ]

    # ----- 6. Why this creative will work -----
    reasoning = (
        "This creative filters casual viewers and builds trust by being "
        "price-transparent, location-clear, and visually serious. "
        "High-intent buyers feel safe engaging. Low-intent users scroll away."
    )

    return {
        "design_tone": design_tone,
        "visual_layout": visual_layout,
        "headline_style": headline_style,
        "color_palette": color_palette,
        "must_show": must_show,
        "must_not_show": must_not_show,
        "reasoning": reasoning
    }
