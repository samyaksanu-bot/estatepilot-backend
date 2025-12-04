from typing import Dict

def generate_static_image_spec(
    graphic_formula: Dict,
    template_selection: Dict,
    project: Dict
) -> Dict:

    price = ""
    if graphic_formula["final_visual_recipe"].get("show_price", True):
        price = f"₹{project['price_min_lakh']}–{project['price_max_lakh']} Lakh"

    return {
        "canvas": {"width": 1080, "height": 1080},
        "text_elements": [
            {"type": "headline", "text": project["name"]},
            {"type": "location", "text": project["location"]},
            {"type": "price", "text": price},
            {"type": "cta", "text": "Check availability on WhatsApp"}
        ],
        "visual_elements": template_selection["selected_template"]["visual_blocks"],
        "quality_checks": ["readable", "not_misleading"]
    }
