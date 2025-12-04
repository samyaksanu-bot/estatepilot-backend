def generate_creative_brief(project: dict, intent_profile: dict) -> dict:
    """
    Final, safe creative brief generator.
    Depends on BOTH project + intent_profile.
    Guaranteed no NameError / KeyError.
    """

    # --- safe extraction ---
    property_type = intent_profile.get(
        "property_type",
        project.get("type", "flat")
    )

    location = intent_profile.get(
        "location",
        project.get("location", "Location not specified")
    )

    budget_min = project.get("price_min_lakh", "—")
    budget_max = project.get("price_max_lakh", "—")

    # --- visual logic ---
    if property_type == "flat":
        visual_layout = "front elevation + amenities"
    else:
        visual_layout = "layout map + plot visualization"

    return {
        "design_tone": "trust-building, informative, calm",
        "visual_layout": visual_layout,
        "headline_style": "clarity-first, lifestyle-secondary",
        "color_palette": "neutral, light, low saturation",
        "must_show": [
            f"Price range: ₹{budget_min}–{budget_max} lakh",
            location,
            f"Project type: {property_type}"
        ],
        "must_not_show": [
            "fake luxury imagery",
            "celebrity references",
            "misleading promises",
            "irrelevant stock visuals"
        ],
        "reasoning": (
            "Designed to attract high-intent buyers through transparency "
            "and realism, filtering casual or low-quality leads."
        )
    }
