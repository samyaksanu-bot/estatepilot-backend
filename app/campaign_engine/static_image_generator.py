# app/campaign_engine/static_image_generator.py

from typing import Dict, Any


def generate_static_image_spec(
    creative_blueprint: Dict[str, Any],
    template_selection: Dict[str, Any],
    brief: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Converts the Creative Blueprint + Template Selection into a final
    SDXL-ready image specification.

    This file does NOT generate images.
    It ONLY defines what SDXL should produce (structure + constraints).
    """

    template = template_selection.get("selected_template", {})
    project_name = brief.get("project_name", "Residential Project")
    location = brief.get("location", "")
    price_min = brief.get("price_min_lakh")
    price_max = brief.get("price_max_lakh")

    # Price string (strict, non-invented)
    if price_min and price_max:
        price_str = f"{price_min}–{price_max} Lakhs"
    else:
        price_str = None

    # SDXL prompt and negative prompt from blueprint
    sdxl_prompt = creative_blueprint.get("sdxl_prompt")
    negative_prompt = creative_blueprint.get("sdxl_negative_prompt")

    # Text elements for the rendered template
    text_layers = []

    # Headline
    if creative_blueprint.get("headline"):
        text_layers.append({
            "type": "headline",
            "text": creative_blueprint["headline"]
        })

    # Subheadline (optional)
    if creative_blueprint.get("subheadline"):
        text_layers.append({
            "type": "subheadline",
            "text": creative_blueprint["subheadline"]
        })

    # Price (optional)
    if price_str:
        text_layers.append({
            "type": "price",
            "text": price_str
        })

    # CTA (ALWAYS where ad performance depends)
    text_layers.append({
        "type": "cta",
        "text": creative_blueprint.get("cta", "Check Availability on WhatsApp")
    })

    # Build final spec object for SDXL
    spec = {
        "canvas": {
            "width": 1080,
            "height": 1080
        },
        "template_id": template.get("template_id"),
        "visual_blocks": template.get("visual_blocks", []),
        "layout": template.get("recommended_layout", "safe_grid"),
        "text_layers": text_layers,
        "sdxl_prompt": sdxl_prompt,
        "sdxl_negative_prompt": negative_prompt,
        "style": {
            "tone_keywords": creative_blueprint.get("tone_keywords", []),
            "color_palette": creative_blueprint.get("color_palette", [])
        },
        "factual_rules": {
            "allowed_elements": creative_blueprint.get("allowed_elements", []),
            "forbidden_elements": creative_blueprint.get("forbidden_elements", [])
        }
    }

    # Required for debugging & safety
    spec["debug"] = {
        "project_name": project_name,
        "location": location
    }

    return spec
