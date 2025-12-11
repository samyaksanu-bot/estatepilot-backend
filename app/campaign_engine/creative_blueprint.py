def generate_creative_blueprint(brief: dict, strategy: dict) -> dict:
    """
    Minimal placeholder creative blueprint.
    No GPT yet.
    Only returns required fields so the system does not break.
    """

    return {
        "headline": f"{brief.get('project_name', 'Project')} in {brief.get('location', '')}",
        "subheadline": "Modern living with essential amenities",
        "cta": "Check Availability",
        "copy_variants": [
            "Book a site visit today.",
            "Premium homes at a competitive price.",
        ],
        "sdxl_prompt": (
            "modern residential building, clean elevation, soft daylight, "
            "architectural realistic render, no people, no cars"
        ),
        "final_visual_recipe": {
            "primary_visual": "modern apartment elevation",
            "template_type": "ELEVATION",
            "show_price": True,
            "layout_priority": ["headline", "price", "cta"]
        }
    }
