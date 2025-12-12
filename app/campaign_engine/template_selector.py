# app/campaign_engine/template_selector.py

from typing import Dict, Any


def select_visual_template(creative_blueprint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Template selector based on blueprint's visual_focus + layout_style.
    This version is compatible with the new creative_blueprint schema.
    
    It chooses a layout template that SDXL will render into.
    No hallucination, no fabricated views — only structural choice.
    """

    visual_focus = (creative_blueprint.get("visual_focus") or "").lower()
    layout_style = (creative_blueprint.get("layout_style") or "").lower()

    # -------------------------------
    # RULE 1 — Elevation-focused visual
    # -------------------------------
    if "elevation" in visual_focus or "building" in visual_focus or "tower" in visual_focus:
        template = {
            "template_id": "ELEVATION_CLEAN_HERO",
            "visual_blocks": [
                "hero_elevation",
                "price_strip",
                "cta_block"
            ],
            "recommended_layout": layout_style or "hero_top_details_bottom"
        }
    
    # -------------------------------
    # RULE 2 — Silhouette-style visual (safe for half-built projects)
    # -------------------------------
    elif "silhouette" in visual_focus or "mass" in visual_focus:
        template = {
            "template_id": "SILHOUETTE_SAFE_TEMPLATE",
            "visual_blocks": [
                "soft_silhouette",
                "neutral_background",
                "amenities_icons_optional"
            ],
            "recommended_layout": layout_style or "minimal_center_focus"
        }

    # -------------------------------
    # RULE 3 — Plot or land visuals
    # -------------------------------
    elif "plot" in visual_focus or "land" in visual_focus:
        template = {
            "template_id": "PLOT_LANDSCAPE_TEMPLATE",
            "visual_blocks": [
                "open_land_visual",
                "plot_boundary_hint",
                "cta_block"
            ],
            "recommended_layout": layout_style or "clean_open_space"
        }

    # -------------------------------
    # RULE 4 — Generic fallback
    # -------------------------------
    else:
        template = {
            "template_id": "GENERIC_REAL_ESTATE_TEMPLATE",
            "visual_blocks": [
                "neutral_background",
                "headline_block",
                "cta_block"
            ],
            "recommended_layout": layout_style or "simple_grid"
        }

    return {
        "selected_template": template,
        "debug_info": {
            "matched_visual_focus": visual_focus,
            "matched_layout_style": layout_style
        }
    }
