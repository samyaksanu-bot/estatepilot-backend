from typing import Dict, Optional

def render_static_template(
    image_spec: Dict,
    template_selection: Dict,
    project_assets: Optional[Dict] = None
) -> Dict:

    return {
        "template_id": template_selection["selected_template"]["template_id"],
        "canvas": image_spec["canvas"],
        "text_layers": image_spec["text_elements"],
        "visual_layers": image_spec["visual_elements"],
        "quality_checks": image_spec["quality_checks"]
    }
