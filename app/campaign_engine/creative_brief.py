def generate_creative_brief(
    project: dict,
    intent_profile: dict
) -> dict:
    """
    Builds a professional creative brief.
    Must NEVER fail due to missing keys.
    """

    property_type = intent_profile.get("property_type", project.get("type", "flat"))

    visual_layout = (
        "elevation + amenities snapshot"
        if property_type == "flat"
        else "layout map + plot visualization"
    )

    return {
        "design_tone": "informative, welcoming, simple",
        "visual_layout": visual_layout,
        "headline_style": "balanced text with lifestyle cues",
        "color_palette": "light colors, soft contrast",
        "must_show": [
            f"Price range: ₹{intent_profile.get('budget_min', '—')}–{intent_profile.get('budget_max', '—')} lakh",
            f"Location: {intent_profile.get('location', 'Not specified')}",
            f"Project type: {property_type}"
        ],
        "must_not_show": [
            "fake luxury imagery",
            "celebrity photos",
            "over-promising claims",
            "irrelevant lifestyle visuals"
        ],
        "reasoning": (
            "This design prioritizes clarity and buyer trust. "
            "High-intent buyers engage; casual scrollers self-filter."
        )
    }
