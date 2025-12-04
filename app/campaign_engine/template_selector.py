from typing import Dict

def select_visual_template(graphic_formula: Dict) -> Dict:
    recipe = graphic_formula["final_visual_recipe"]

    if "map" in recipe["primary_visual"]:
        template = {
            "template_id": "STATIC_MAP_FOCUS",
            "visual_blocks": ["map_or_layout", "price_block"]
        }
    else:
        template = {
            "template_id": "STATIC_ELEVATION_FOCUS",
            "visual_blocks": ["elevation_image", "amenities_icons"]
        }

    return {
        "selected_template": template
    }
