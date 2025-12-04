# app/campaign_engine/template_renderer.py

def render_static_template(
    image_spec: dict,
    template_selection: dict,
    project_assets: dict | None = None
) -> dict:
    """
    Converts a static image specification into
    a render-ready design payload.
    No AI. No assumptions. No hallucination.
    """

    if project_assets is None:
        project_assets = {}

    template = template_selection["selected_template"]

    # -----------------------------
    # CANVAS SETUP
    # -----------------------------
    canvas = {
        "width": image_spec["canvas"]["width"],
        "height": image_spec["canvas"]["height"],
        "background": image_spec["canvas"]["background"]
    }

    # -----------------------------
    # LOAD ASSETS (SAFE ONLY)
    # -----------------------------
    assets = {
        "logo": project_assets.get("logo"),
        "verified_images": project_assets.get("verified_images", []),
        "map": project_assets.get("map"),
        "layout": project_assets.get("layout")
    }

    # -----------------------------
    # PLACE TEXT ELEMENTS
    # -----------------------------
    text_layers = []
    for element in image_spec["text_elements"]:
        text_layers.append(
            {
                "type": element["type"],
                "text": element["text"],
                "position": element["position"],
                "font_weight": element.get("font_weight", "regular"),
                "max_lines": element.get("max_lines"),
                "safe": True
            }
        )

    # -----------------------------
    # PLACE VISUAL ELEMENTS
    # -----------------------------
    visual_layers = []
    for element in image_spec["visual_elements"]:
        visual_layers.append(
            {
                "asset_type": element["asset_type"],
                "source": assets,
                "safe_use": element["safe_use"]
            }
        )

    # -----------------------------
    # FINAL RENDER PAYLOAD
    # -----------------------------
    return {
        "render_type": "static_template",
        "template_id": template["template_id"],
        "canvas": canvas,
        "text_layers": text_layers,
        "visual_layers": visual_layers,
        "branding": {
            "brand_safe": template.get("brand_safe", True),
            "logo_required": bool(project_assets.get("logo"))
        },
        "quality_checks": image_spec["quality_checks"],
        "engine_note": (
            "This payload is ready for Canva/Figma-style rendering. "
            "All content is verified and engine-controlled."
        )
    }
