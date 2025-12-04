# app/campaign_engine/campaign_preview_ui.py

def build_campaign_preview_ui(
    project: dict,
    graphic_formula: dict,
    template_selection: dict,
    render_payload: dict
) -> dict:
    """
    Builds a human-readable campaign preview
    that feels like a professional ad proof.
    """

    preview = {
        "preview_header": {
            "project_name": project.get("name"),
            "property_type": project.get("type"),
            "location": project.get("location"),
        },

        "visual_overview": {
            "template_used": render_payload["template_id"],
            "canvas": f'{render_payload["canvas"]["width"]}x{render_payload["canvas"]["height"]}',
            "visual_style": graphic_formula["final_visual_recipe"]["design_tone"],
            "primary_visual": graphic_formula["final_visual_recipe"]["primary_visual"],
        },

        "ad_text_blocks": [
            {
                "label": layer["type"],
                "text": layer["text"],
                "position": layer["position"]
            }
            for layer in render_payload["text_layers"]
        ],

        "call_to_action": {
            "cta_text": next(
                (layer["text"] for layer in render_payload["text_layers"] if layer["type"] == "cta"),
                None
            )
        },

        "builder_overrides": graphic_formula["builder_overrides_applied"],

        "risk_warnings": graphic_formula["risk_warnings"],

        "approval_section": {
            "status": "pending",
            "builder_actions_available": [
                "Change headline",
                "Toggle price visibility",
                "Request different imagery",
                "Approve & proceed"
            ]
        },

        "engine_note": (
            "This preview represents how your ad will appear structurally. "
            "Final visuals will be rendered after approval."
        )
    }

    return preview
