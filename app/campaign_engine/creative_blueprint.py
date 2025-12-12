# app/campaign_engine/creative_blueprint.py

from typing import Dict, Any
from app.ai_engine import call_gpt_json

# -------------------------------------------------------------------
# 1. Deterministic, fact-safe visual recipe (Python-first, no hallucination)
# -------------------------------------------------------------------
def _build_final_visual_recipe(brief: Dict[str, Any]) -> Dict[str, Any]:
    prop_type = (brief.get("property_type") or brief.get("type") or "").lower()
    show_price = bool(brief.get("price_min_lakh") and brief.get("price_max_lakh"))

    if prop_type == "plot":
        primary_visual = "map"
        template_hint = "STATIC_MAP_FOCUS"
    else:
        primary_visual = "elevation"
        template_hint = "STATIC_ELEVATION_FOCUS"

    show_amenities = bool(brief.get("amenities"))

    return {
        "primary_visual": primary_visual,
        "template_hint": template_hint,
        "show_price": show_price,
        "show_amenities": show_amenities,
        "visual_style": "modern_residential" if prop_type != "plot" else "open_landscape",
        "mood": "trust_building_realistic",
        "lighting": "soft_daylight"
    }


# -------------------------------------------------------------------
# 2. GPT Strict Prompt — No hallucination allowed
# -------------------------------------------------------------------
def _build_fact_safe_prompt(brief: Dict[str, Any], strategy: Dict[str, Any]) -> str:
    amenities = brief.get("amenities") or []

    price_min = brief.get("price_min_lakh")
    price_max = brief.get("price_max_lakh")
    price_string = "Not provided"
    if price_min and price_max:
        price_string = f"{price_min}–{price_max} Lakhs"

    return f"""
You are EstatePilot's Creative Blueprint Generator.

STRICT FACT RULES:
- DO NOT invent amenities. Allowed amenities ONLY: {amenities}.
- DO NOT add towers, floors, unit sizes, luxury elements not provided.
- DO NOT add ocean, mountain, mall, skyline, forest, lake or fake surroundings.
- DO NOT fabricate RERA details.
- Price MUST remain EXACT: {price_string}.
- Visuals must be realistic, trustworthy and simple.

OUTPUT JSON SCHEMA:
{{
  "headline": str,
  "subheadline": str | null,
  "cta": "Check Availability on WhatsApp",
  "visual_focus": str,
  "layout_style": str,
  "allowed_elements": [str,...],
  "forbidden_elements": [str,...],
  "sdxl_prompt": str,
  "sdxl_negative_prompt": str,
  "tone_keywords": [str,...],
  "color_palette": [str,...],
  "reasoning": str
}}

PROJECT FACTS:
Project Name: {brief.get("project_name")}
Location: {brief.get("location")}
Property Type: {brief.get("property_type")}
Price: {price_string}
Amenities (strict list): {amenities}
Buyer Persona: {brief.get("buyer_persona")}
Zone: {brief.get("zone")}

STRATEGY INPUT:
Messaging pillars: {strategy.get("messaging_pillars")}
Core angle: {strategy.get("core_angle")}
"""

# -------------------------------------------------------------------
# 3. Assemble SDXL Prompt (safe Python rules)
# -------------------------------------------------------------------
def _build_sdxl_from_recipe(brief: Dict[str, Any], recipe: Dict[str, Any]) -> Dict[str, str]:
    project = brief.get("project_name") or "Project"
    location = brief.get("location") or ""
    prop_type = brief.get("property_type") or brief.get("type") or ""

    base = (
        f"Realistic architectural visual of {project}, {prop_type}, located in {location}. "
        f"Style: {recipe['visual_style']}. Mood: {recipe['mood']}. Lighting: {recipe['lighting']}. "
    )

    if recipe["primary_visual"] == "elevation":
        base += "Focus on clean front elevation. No invented skyline."
    else:
        base += "Top-down or angled map/plot visualization. No invented surroundings."

    neg = (
        "No mountains, no oceans, no malls, no skyline, no luxury elements not provided, "
        "no celebrities, no invented amenities, no dramatic effects, no glossy reflection."
    )

    return {"sdxl_prompt": base, "sdxl_negative_prompt": neg}


# -------------------------------------------------------------------
# 4. MAIN FUNCTION — FINAL CREATIVE BLUEPRINT
# -------------------------------------------------------------------
def generate_creative_blueprint(brief: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:

    # Python-first factual visual recipe
    recipe = _build_final_visual_recipe(brief)

    # Build strict GPT system prompt
    system_prompt = _build_fact_safe_prompt(brief, strategy)

    user_prompt = "Generate the creative blueprint JSON. Follow schema strictly. No extra text."

    gpt_resp = call_gpt_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="gpt-4.1",
        temperature=0.0,
        max_tokens=500,
        retries=1
    )

    # If GPT failed → fallback safe template
    if not isinstance(gpt_resp, dict) or gpt_resp.get("error"):
        fallback_sdxl = _build_sdxl_from_recipe(brief, recipe)
        return {
            "final_visual_recipe": recipe,
            "headline": brief.get("project_name", "New Project"),
            "subheadline": brief.get("location"),
            "cta": "Check Availability on WhatsApp",
            "visual_focus": "front elevation",
            "layout_style": "clean grid",
            "allowed_elements": ["realistic elevation", "soft daylight"],
            "forbidden_elements": ["fake luxury", "invented amenities", "mountain views"],
            "sdxl_prompt": fallback_sdxl["sdxl_prompt"],
            "sdxl_negative_prompt": fallback_sdxl["sdxl_negative_prompt"],
            "tone_keywords": ["trust", "clarity"],
            "color_palette": ["white", "beige", "light grey"],
            "template_hint": recipe["template_hint"],
            "layout_hint": "hero_top_text_bottom",
            "reasoning": "Fallback because GPT returned invalid JSON."
        }

    # Merge GPT response with SDXL recipe
    sdxl = _build_sdxl_from_recipe(brief, recipe)

    gpt_resp["final_visual_recipe"] = recipe
    gpt_resp["sdxl_prompt"] = sdxl["sdxl_prompt"]
    gpt_resp["sdxl_negative_prompt"] = sdxl["sdxl_negative_prompt"]
    gpt_resp["template_hint"] = recipe["template_hint"]
    gpt_resp["layout_hint"] = (
        "hero_top_text_bottom"
        if recipe["primary_visual"] == "elevation"
        else "map_top_details_bottom"
    )

    return gpt_resp
