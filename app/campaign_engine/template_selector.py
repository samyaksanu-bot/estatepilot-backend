# app/campaign_engine/template_selector.py

def select_visual_template(graphic_formula: dict) -> dict:
    """
    Selects the best visual template based on the final visual recipe.
    Keeps creatives consistent, readable, and high quality.
    """

    final_recipe = graphic_formula["final_visual_recipe"]
    intent_note = graphic_formula.get("risk_warnings", [])

    format_type = final_recipe.get("format", "static")
    primary_visual = final_recipe.get("primary_visual")
    design_tone = final_recipe.get("design_tone")

    template = {}
    rationale = []

    # -----------------------------
    # STATIC IMAGE TEMPLATES
    # -----------------------------
    if format_type == "static":
        if "map" in primary_visual or "layout" in primary_visual:
            template = {
                "template_id": "STATIC_MAP_FOCUS",
                "canvas": "1080x1080",
                "headline_position": "top",
                "visual_blocks": ["map_or_layout", "price_block"],
                "text_density": "medium",
                "brand_safe": True
            }
            rationale.append("Map/layout driven visuals work best for location-sensitive buyers.")

        else:
            template = {
                "template_id": "STATIC_ELEVATION_FOCUS",
                "canvas": "1080x1080",
                "headline_position": "bottom",
                "visual_blocks": ["elevation_image", "amenities_icons"],
                "text_density": "light",
                "brand_safe": True
            }
            rationale.append("Elevation-focused visuals suit lifestyle and discovery buyers.")

    # -----------------------------
    # VIDEO TEMPLATES (CONTROLLED)
    # -----------------------------
    if format_type == "video":
        template = {
            "template_id": "SIMPLE_MOTION_SLIDE",
            "canvas": "1080x1080",
            "duration_seconds": 6,
            "slides": [
                "headline_slide",
                "primary_visual_slide",
                "cta_slide"
            ],
            "motion_style": "slow_zoom_fade",
            "brand_safe": True
        }
        rationale.append("Short informational motion avoids overproduction and keeps credibility.")

    # -----------------------------
    # SAFETY + QUALITY NOTES
    # -----------------------------
    quality_notes = [
        "Text must be readable on mobile",
        "Price and location cannot be hidden in templates",
        "Avoid clutter and excessive animation"
    ]

    return {
        "selected_template": template,
        "selection_rationale": rationale,
        "quality_notes": quality_notes,
        "engine_note": (
            "Template choice prioritizes clarity and buyer intent over visual novelty."
        )
    }
