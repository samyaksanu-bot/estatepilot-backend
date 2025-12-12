# app/campaign_engine/strategy_engine.py

from typing import Dict, Any
from app.ai_engine import call_gpt_json


def _safe_lower(value):
    """Utility: always return a safe lowercase string."""
    return str(value or "").lower()


def _deterministic_radius(brief: Dict[str, Any]) -> Dict[str, int]:
    def mid(a, b): return (a + b) // 2

    price_min = brief.get("price_min_lakh") or 0
    price_max = brief.get("price_max_lakh") or 0

    prop_type = _safe_lower(brief.get("type") or brief.get("property_type"))
    zone_hint = _safe_lower(brief.get("zone"))

    notes = _safe_lower(brief.get("notes"))
    infra = brief.get("future_infrastructure", False) or any(
        kw in notes for kw in ["highway", "metro", "ring road", "airport", "expressway", "industrial corridor"]
    )

    if prop_type == "plot":
        min_km, max_km = 12, 25
    elif infra:
        min_km, max_km = 10, 25
    elif price_max and price_max < 40:
        min_km, max_km = 10, 20
    elif zone_hint == "urban":
        min_km, max_km = 3, 6
    elif zone_hint == "suburban":
        min_km, max_km = 5, 9
    elif zone_hint == "remote":
        min_km, max_km = 10, 25
    elif "villa" in prop_type:
        min_km, max_km = 7, 12
    else:
        min_km, max_km = 5, 8

    recommended = mid(min_km, max_km)
    return {"recommended": recommended, "min": min_km, "max": max_km}


def _build_system_prompt() -> str:
    return """
You are ESTATEPILOT Strategy Engine (expert real-estate Meta Ads strategist).
You MUST return ONLY valid JSON (no extra text). Follow the schema exactly.

CRITICAL RULES:
- Do NOT invent factual data. Use ONLY project brief fields.
- If uncertain, return null or empty lists.
- Radius logic must follow deterministic rules.
- Behavior/exclusion filters MUST be chosen only when they make contextual sense:

BEHAVIOR FILTERS (choose selectively):
- likely_to_move → good for end-user residential, urban zones, families
- home_loan_intent → use when price is mid/high OR end-user family product
- active_property_researcher → use for plots OR investment-led markets OR remote zones

EXCLUSIONS (choose selectively):
- real_estate_agent / broker / realtor → exclude for all residential campaigns
- students → exclude if price > 25 lakh or family-oriented housing
- non_local_residents → exclude only when hyperlocal end-user targeting is required

OUTPUT SCHEMA:
{
  "persona": str|null,
  "intent_level": "high"|"medium"|"low",
  "property_type": str|null,
  "targeting": {
     "target_radius_km": {"recommended": int, "min": int, "max": int},
     "age_filter": [int,int] | null,
     "behavior_filters": [str,...],
     "exclusions": [str,...],
     "geo_notes": str|null
  },
  "placements": { "<placement_name>": true|false, ... },
  "budget_plan": {"daily": number|null, "total": number|null, "currency": "INR"},
  "lead_form": [
     {"id": str, "type": "choice"|"text"|"phone", "text": str, "required": true|false}
  ],
  "messaging_pillars": [str,...],
  "creative_copy": {
     "headline": str,
     "primary_text": str,
     "short_variants": [str,...],
     "cta": str
  },
  "whatsapp_bot_notes": {
     "what_to_emphasize": [str,...],
     "what_to_avoid": [str,...],
     "qualification_priority": [str,...]
  }
}
"""


def generate_strategy(brief: Dict[str, Any]) -> Dict[str, Any]:

    radius = _deterministic_radius(brief)

    brief_summary = {
        "project_name": brief.get("project_name"),
        "location": brief.get("location"),
        "price_min_lakh": brief.get("price_min_lakh"),
        "price_max_lakh": brief.get("price_max_lakh"),
        "unit_types": brief.get("unit_types"),
        "floors": brief.get("floors"),
        "amenities": brief.get("amenities"),
        "type": brief.get("type") or brief.get("property_type"),
        "zone": brief.get("zone"),
        "notes": brief.get("notes"),
        "images_provided": bool(brief.get("images"))
    }

    user_prompt = f"PROJECT_BRIEF:{brief_summary}\n\nGenerate the JSON strategy following the schema."

    resp = call_gpt_json(
        system_prompt=_build_system_prompt(),
        user_prompt=user_prompt,
        model="gpt-4.1",
        temperature=0.15,
        max_tokens=900,
        retries=2
    )

    # FALLBACK
    if not isinstance(resp, dict) or resp.get("error"):
        return {
            "persona": "mixed_buyer",
            "intent_level": "medium",
            "property_type": brief.get("type") or brief.get("property_type") or "flat",
            "targeting": {
                "target_radius_km": radius,
                "age_filter": [28, 55],
                "behavior_filters": ["likely_to_move"],
                "exclusions": ["real_estate_agent", "broker"],
                "geo_notes": None
            },
            "placements": {
                "facebook_feed": True,
                "instagram_feed": True,
                "instagram_reels": True,
                "audience_network": False,
                "in_stream": False,
                "in_article": False
            },
            "budget_plan": {"daily": 1000, "total": None, "currency": "INR"},
            "lead_form": [
                {"id": "budget", "type": "choice", "text": "What is your budget (INR lakhs)?", "required": True},
                {"id": "timeline", "type": "choice", "text": "When do you plan to buy?", "required": True}
            ],
            "messaging_pillars": ["price_transparency", "location_advantage", "credibility"],
            "creative_copy": {
                "headline": f"{brief.get('project_name') or 'Project'} — Check Price & Availability",
                "primary_text": "Contact to know price, site visit, and floor plans.",
                "short_variants": ["Book Site Visit"],
                "cta": "Book Site Visit"
            },
            "whatsapp_bot_notes": {
                "what_to_emphasize": ["price", "location"],
                "what_to_avoid": ["fabricated facts"],
                "qualification_priority": ["budget", "timeline"]
            }
        }

    # REQUIRED KEYS
    required_top = [
        "persona", "intent_level", "property_type", "targeting",
        "placements", "budget_plan", "lead_form",
        "messaging_pillars", "creative_copy", "whatsapp_bot_notes"
    ]
    for k in required_top:
        resp.setdefault(k, None)

    # TARGETING SAFE DEFAULTS
    targeting = resp.get("targeting") or {}
    targeting.setdefault("target_radius_km", radius)
    targeting.setdefault("behavior_filters", ["likely_to_move"])
    targeting.setdefault("exclusions", ["real_estate_agent", "broker"])
    targeting.setdefault("age_filter", [28, 55])
    resp["targeting"] = targeting

    # PLACEMENTS SAFE DEFAULTS
    placements = resp.get("placements") or {}
    default_placements = {
        "facebook_feed": True,
        "instagram_feed": True,
        "instagram_reels": True,
        "audience_network": False,
        "in_stream": False,
        "in_article": False
    }
    for k, v in default_placements.items():
        placements.setdefault(k, v)
    resp["placements"] = placements

    # BUDGET SAFE
    bp = resp.get("budget_plan") or {}
    bp.setdefault("daily", 1000)
    bp.setdefault("total", None)
    bp.setdefault("currency", "INR")
    resp["budget_plan"] = bp

    # LEAD FORM SAFE
    lf = resp.get("lead_form") or []
    if not lf:
        lf = [
            {"id": "budget", "type": "choice", "text": "What is your budget (INR lakhs)?", "required": True},
            {"id": "timeline", "type": "choice", "text": "When do you plan to buy?", "required": True}
        ]
    resp["lead_form"] = lf

    # CREATIVE COPY SAFE
    cc = resp.get("creative_copy") or {}
    cc.setdefault("headline", f"{brief.get('project_name') or 'Project'} — Check Price & Availability")
    cc.setdefault("primary_text", "Contact to know price, site visit, and floor plans.")
    cc.setdefault("short_variants", ["Book Site Visit"])
    cc.setdefault("cta", "Book Site Visit")
    resp["creative_copy"] = cc

    # WHATSAPP NOTES SAFE
    wbn = resp.get("whatsapp_bot_notes") or {}
    wbn.setdefault("what_to_emphasize", ["price", "location"])
    wbn.setdefault("what_to_avoid", ["fabricated facts"])
    wbn.setdefault("qualification_priority", ["budget", "timeline"])
    resp["whatsapp_bot_notes"] = wbn

    return resp
