from typing import Dict

def build_campaign_preview_ui(
    project: Dict,
    graphic_formula: Dict,
    template_selection: Dict,
    render_payload: Dict
) -> Dict:
    return {
        "preview": {
            "project": {
                "name": project.get("name"),
                "location": project.get("location"),
                "type": project.get("type")
            },
            "template_used": template_selection.get("selected_template", {}),
            "visual_layers": render_payload.get("visual_layers", []),
            "text_layers": render_payload.get("text_layers", []),
        },
        "status": "PREVIEW_OK"
    }
