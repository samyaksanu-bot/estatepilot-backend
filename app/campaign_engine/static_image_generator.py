# app/campaign_engine/static_image_generator.py

def generate_static_image_spec(
    graphic_formula: dict,
    template_selection: dict,
    project: dict
) -> dict:
    """
    Generates a static image specification
    ready for rendering by design tools.
    """

    final_recipe = graphic_formula["final_visual_recipe"]
    template = template_selection["selected_template"]

    price_text = ""
    if final_recipe.get("show_price", True):
        price_min, price_max = project.get("price_min_lakh"), project.get("price_max_lakh")
        price_text = f"From ₹{price_min}–{price_max} Lakh"

    # -----------------------------
    # CORE CANVAS SETTINGS
    # -----------------------------
    canvas_spec = {
        "width": 1080,
        "height": 1080,
        "background": final_recipe.get("color_palette")
    }

    # -----------------------------
    # TEXT ELEMENTS
    # -----------------------------
    text_elements = [
        {
            "type": "headline",
            "text": project.get("name"),
            "position": template.get("headline_position"),
            "font_weight": "bold",
            "max_lines": 2
        },
        {
            "type": "subtext",
            "text": project.get("location"),
            "position": "below_headline"
        }
    ]

    if price_text:
        text_elements.append(
            {
                "type": "price",
                "text": price_text,
                "position": "prominent",
                "font_weight": "bold"
            }
        )

    text_elements.append(
        {
            "type": "cta",
            "text": final_recipe.get("cta"),
            "position": "bottom"
        }
    )

    # -----------------------------
    # VISUAL ELEMENTS
    # -----------------------------
    visual_elements = []
    for block in template.get("visual_blocks", []):
        visual_elements.append(
            {
                "asset_type": block,
                "source": "brochure_or_verified_assets",
                "safe_use": True
            }
        )

    # -----------------------------
    # QUALITY CHECK RULES
    # -----------------------------
    quality_checks = [
        "headline_readable_on_mobile",
        "price_clear_if_shown",
        "location_visible",
        "no_text_overlap",
        "no_misleading_imagery"
    ]

    return {
        "canvas": canvas_spec,
        "text_elements": text_elements,
        "visual_elements": visual_elements,
        "quality_checks": quality_checks,
        "engine_note": (
            "This static image spec prioritizes clarity, trust, "
            "and high-intent engagement over decorative design."
        )
    }
