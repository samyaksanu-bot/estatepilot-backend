# app/campaign_engine/creative_blueprint.py
from typing import Dict, Any
from app.ai_engine import call_gpt_json

def _safe_str(v: Any) -> str:
    return "" if v is None else str(v)

def _safe_list(v: Any) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]

def _build_fact_safe_prompt(brief: Dict[str, Any], strategy: Dict[str, Any]) -> str:
    amenities = _safe_list(brief.get("amenities"))
    price_min = brief.get("price_min_lakh")
    price_max = brief.get("price_max_lakh")
    price_string = "Not provided"
    if price_min and price_max:
        price_string = f"{price_min}–{price_max} Lakhs"

    project_name = _safe_str(brief.get("project_name"))
    location = _safe_str(brief.get("location"))
    prop_type = _safe_str(brief.get("property_type") or brief.get("type"))
    buyer_persona = _safe_str(brief.get("buyer_persona"))
    buyer_conf = _safe_str(brief.get("buyer_persona_confidence"))
    zone = _safe_str(brief.get("zone"))
    zone_conf = _safe_str(brief.get("zone_confidence"))

    return f"""
You are EstatePilot's Creative Blueprint Generator for REAL ESTATE ADVERTISING.

STRICT RULES:
- DO NOT invent amenities. Use ONLY these confirmed amenities: {amenities}.
- DO NOT create fake luxury visuals, water bodies, mountain views, skyline views, or greenery not confirmed.
- DO NOT infer RERA details.
- DO NOT change price. Use EXACT project price: {price_string}.
- DO NOT add floors, towers, unit sizes or materials not mentioned.
- You may phrase visuals aesthetically, but CANNOT invent factual elements.

GOAL:
Return a creative blueprint that the image model will use to create ad visuals.

MANDATORY OUTPUT STRUCTURE:
{{
  "headline": str,
  "subheadline": str|null,
  "cta": "Check Availability on WhatsApp",
  "visual_focus": str,
  "layout_style": str,
  "allowed_elements": [...],
  "forbidden_elements": [...],
  "sdxl_prompt": str,
  "sdxl_negative_prompt": str,
  "tone_keywords": [...],
  "color_palette": [...],
  "reasoning": str
}}

ABOUT THE PROJECT (FACTUAL ONLY):
Project Name: {project_name}
Location: {location}
Property Type: {prop_type}
Price: {price_string}
Amenities (strict): {amenities}
Buyer Persona: {buyer_persona} (confidence: {buyer_conf})
Zone Hint: {zone} (confidence: {zone_conf})

STRATEGY INPUT:
Core angle: {_safe_str(strategy.get('core_angle'))}
Messaging pillars: {_safe_str(strategy.get('messaging_pillars'))}
Lead form emphasis: {_safe_str(strategy.get('lead_form'))}
"""

def generate_creative_blueprint(brief: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
    system_prompt = _build_fact_safe_prompt(brief, strategy)

    user_prompt = """
Generate a REAL ESTATE AD creative blueprint.
Use EXACT factual information; NEVER invent any details.
Follow the mandatory output schema strictly.
Return ONLY valid JSON.
"""

    try:
        response = call_gpt_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="gpt-4.1",
            temperature=0.0,
            max_tokens=500,
            retries=2
        )
    except Exception as e:
        response = {"error": f"call_gpt_json_exception: {str(e)}"}

    # Validate response
    if not isinstance(response, dict) or response.get("error"):
        # safe fallback
        return {
            "headline": brief.get("project_name", "New Residential Project"),
            "subheadline": brief.get("location"),
            "cta": "Check Availability on WhatsApp",
            "visual_focus": "front elevation silhouette",
            "layout_style": "clean grid",
            "allowed_elements": [_safe_str(a) for a in _safe_list(brief.get("amenities"))],
            "forbidden_elements": [
                "fake luxury", "invented amenities", "celebrity models",
                "mountain views", "ocean", "mall"
            ],
            "sdxl_prompt": (
                f"realistic, clean architectural visual of a residential building in "
                f"{_safe_str(brief.get('location',''))}, neutral daylight, no luxury effects, no fake scenery"
            ),
            "sdxl_negative_prompt": "fake luxury, mountains, skyline, mall, invented amenities",
            "tone_keywords": ["trust", "clarity", "neutral", "reliable"],
            "color_palette": ["white", "light grey", "soft beige"],
            "reasoning": "Fallback safe template because model returned invalid response."
        }

    # Final safety: coerce keys and types
    res = {}
    res["headline"] = _safe_str(response.get("headline") or response.get("title") or brief.get("project_name", "Project"))
    res["subheadline"] = response.get("subheadline") or _safe_str(brief.get("location"))
    res["cta"] = response.get("cta") or "Check Availability on WhatsApp"
    res["visual_focus"] = _safe_str(response.get("visual_focus") or "front elevation silhouette")
    res["layout_style"] = _safe_str(response.get("layout_style") or "clean grid")
    res["allowed_elements"] = _safe_list(response.get("allowed_elements") or brief.get("amenities") or [])
    res["forbidden_elements"] = _safe_list(response.get("forbidden_elements") or [])
    res["sdxl_prompt"] = _safe_str(response.get("sdxl_prompt") or response.get("prompt") or "")
    res["sdxl_negative_prompt"] = _safe_str(response.get("sdxl_negative_prompt") or response.get("negative_prompt") or "")
    res["tone_keywords"] = _safe_list(response.get("tone_keywords") or [])
    res["color_palette"] = _safe_list(response.get("color_palette") or [])
    res["reasoning"] = _safe_str(response.get("reasoning") or "Generated by EstatePilot creative blueprinter.")
    # also pass back final_visual_recipe if model provided
    res["final_visual_recipe"] = response.get("final_visual_recipe") or response.get("visual_recipe") or {
        "primary_visual": "elevation",
        "template_hint": "STATIC_ELEVATION_FOCUS",
        "show_price": True,
        "show_amenities": True,
        "visual_style": "modern_residential",
        "mood": "trust_building_realistic",
        "lighting": "soft_daylight"
    }
    return res
