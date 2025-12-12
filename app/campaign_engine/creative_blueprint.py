# app/campaign_engine/creative_blueprint.py

from typing import Dict, Any, List
from app.ai_engine import call_gpt_json


def _build_fact_safe_prompt(brief: Dict[str, Any], strategy: Dict[str, Any]) -> str:
    """
    System prompt to enforce strict real estate creative rules:
    - NO adding amenities
    - NO fake views, lakes, malls, luxury not stated
    - NO RERA invention
    - NO pricing fabrication
    - NO claim beyond provided project briefs
    """

    amenities = brief.get("amenities") or []
    price_min = brief.get("price_min_lakh")
    price_max = brief.get("price_max_lakh")
    price_string = "Not provided"
    if price_min and price_max:
        price_string = f"{price_min}–{price_max} Lakhs"

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
Return a creative blueprint that SDXL (image model) will use to create ad visuals.

MANDATORY OUTPUT STRUCTURE:
{
  "headline": str,
  "subheadline": str|null,
  "cta": "Check Availability on WhatsApp",
  "visual_focus": str,      # e.g., "elevation", "side-angle tower", "neat building silhouette"
  "layout_style": str,      # e.g., "clean grid", "hero elevation top, details bottom"
  "allowed_elements": [...],
  "forbidden_elements": [...],
  "sdxl_prompt": str,
  "sdxl_negative_prompt": str,
  "tone_keywords": [...],
  "color_palette": [...],
  "reasoning": str
}

ABOUT THE PROJECT (FACTUAL ONLY):
Project Name: {brief.get("project_name")}
Location: {brief.get("location")}
Property Type: {brief.get("property_type")}
Price: {price_string}
Amenities (strict): {amenities}
Buyer Persona: {brief.get("buyer_persona")} (confidence: {brief.get("buyer_persona_confidence")})
Zone Hint: {brief.get("zone")} (confidence: {brief.get("zone_confidence")})

STRATEGY INPUT:
Core angle: {strategy.get("core_angle")}
Messaging pillars: {strategy.get("messaging_pillars")}
Lead form emphasis: {strategy.get("lead_form")}
"""


def generate_creative_blueprint(brief: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the Creative Blueprint: the clean specification of what SDXL
    should generate visually AND the hierarchy of messaging for the ad creative.
    GPT-4.1 is used in STRICT mode (no hallucination).
    """

    system_prompt = _build_fact_safe_prompt(brief, strategy)

    user_prompt = """
Generate a REAL ESTATE AD creative blueprint.
Use EXACT factual information; NEVER invent any details.
Follow the mandatory output schema strictly.
Return ONLY valid JSON.
"""

    response = call_gpt_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="gpt-4.1",
        temperature=0.0,
        max_tokens=500,
        retries=1
    )

    # Emergency fallback if GPT returns error
    if not isinstance(response, dict) or response.get("error"):
        return {
            "headline": brief.get("project_name", "New Residential Project"),
            "subheadline": brief.get("location"),
            "cta": "Check Availability on WhatsApp",
            "visual_focus": "front elevation silhouette",
            "layout_style": "clean grid",
            "allowed_elements": ["realistic building massing", "soft daylight", "neutral background"],
            "forbidden_elements": ["fake luxury", "invented amenities", "celebrity models", "mountain views"],
            "sdxl_prompt": (
                f"realistic, clean architectural visual of a residential building in "
                f"{brief.get('location', '')}, neutral daylight, no luxury effects, no fake scenery"
            ),
            "sdxl_negative_prompt": "fake luxury, mountains, skyline, mall, invented amenities",
            "tone_keywords": ["trust", "clarity", "neutral", "reliable"],
            "color_palette": ["white", "light grey", "soft beige"],
            "reasoning": "Fallback safe template because GPT returned invalid JSON."
        }

    return response
