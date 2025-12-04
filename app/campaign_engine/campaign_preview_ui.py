from typing import Dict

def build_campaign_preview_ui(
    project: Dict,
    graphic_formula: Dict,
    template_selection: Dict,
    render_payload: Dict
) -> Dict:

    return {
        "preview_header": {
            "project_name": project["name"],
            "location": project["location"]
        },
        "visual_overview": {
            "template_used": render_payload["template_id"],
            "canvas": render_payload["canvas"]
        },
        "ad_text_blocks": render_payload["text_layers"],
        "risk_warnings": graphic_formula["risk_warnings"],
        "status": "PENDING_APPROVAL"
    }
