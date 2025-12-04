def generate_creative_brief(
    project: dict,
    intent_profile: dict
) -> dict:
    """
    Canonical creative brief generator.
    Depends on BOTH project data and buyer intent.
    This function must never crash.
    """

    property_type = (
        intent_profile.get("property_type")
        or project.get("type")
        or "flat"
    )

    location = (
        intent_profile.get("location")
        or project.get("location")
        or "Location not specified"
    )

    budget_min = intent_profile.get("budget_min", project.get("price_min_lakh", "—"))
    budget_max = intent_profile.get("budget_max", project.get("price_max_lakh", "—"))

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
            "celebrity references",
            "fake luxury visuals",
            "misleading promises",
            "irrelevant stock imagery"
        ],
        "reasoning": (
            "This creative is intentionally transparent and restrained. "
            "It attracts buyers with planning intent while filtering "
            "out low-quality curiosity traffic."
        )
    }

