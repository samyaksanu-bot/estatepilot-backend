def generate_creative_brief(input_data: dict) -> dict:
    property_type = input_data.get("property_type", "flat")

    visual_layout = (
        "elevation + amenities snapshot"
        if property_type == "flat"
        else "layout map + plot visualization"
    )

    return {
        "design_tone": "informative, welcoming, simple",
        "visual_layout": visual_layout,   # ✅ GUARANTEED KEY
        "headline_style": "balanced text with lifestyle cues",
        "color_palette": "light colors, soft contrast",
        "must_show": [
            "price range",
            "location clarity",
            "project type clarity"
        ],
        "must_not_show": [
            "fake luxury imagery",
            "celebrity photos",
            "misleading claims"
        ]
    }

