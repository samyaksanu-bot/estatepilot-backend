# app/campaign_engine/strategy_engine.py

from typing import Dict, Any
from app.ai_engine import call_gpt_json


def _deterministic_radius(brief: Dict[str, Any]) -> Dict[str, int]:
    """
    Fallback / deterministic radius logic (returns recommended,min,max).
    Encodes our locked rules and returns integer km values.
    """
    # helpers
    def mid(a, b): return (a + b) // 2

    price_min = brief.get("price_min_lakh") or 0
    price_max = brief.get("price_max_lakh") or 0
    prop_type = (brief.get("type") or brief.get("property_type") or "").lower()
    zone_hint = brief.get("zone", "").lower()
    infra = brief.get("future_infrastructure", False) or any(
        kw in (brief.get("notes","") or "").lower() for kw in ["highway", "metro", "ring road", "airport", "expressway", "industrial corridor"]
    )

    # default buckets (min,max)
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
    """
    System prompt that instructs GPT-4.1 to output strict JSON matching the schema required by EstatePilot.
    Keep concise but firm on rules.
    """
    return """
You are ESTATEPILOT Strategy Engine (expert real-estate Meta Ads strategist).
You MUST return ONLY valid JSON (no extra text). Follow the schema exactly.
CRITICAL RULES:
- Do NOT invent factual data (prices, RERA, amenities). Use only fields present in the Project Brief.
- Keep outputs terse and machine-parsable.
- If uncertain, prefer null or empty lists rather than fabricating data.
- Use the dynamic radius rules: prefer end-user hyperlocal radius for urban projects and wider radius for investor/remote projects or when future infrastructure is present.
OUTPUT SCHEMA (exact keys required):
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
    """
    Production strategy engine using GPT-4.1 via call_gpt_json.
    Returns a JSON-serializable dict matching the strict schema (Option C).
    """
    # 1) Basic local safe defaults and deterministic radius
    radius = _deterministic_radius(brief)

    # 2) Prepare user prompt with brief summary (keep it compact)
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

    # 3) Call GPT-4.1 via helper
    resp = call_gpt_json(
        system_prompt=_build_system_prompt(),
        user_prompt=user_prompt,
        model="gpt-4.1",
        temperature=0.15,
        max_tokens=900,
        retries=2
    )

    # 4) If model returned an error or missing keys, fallback to deterministic minimal strategy
    if not isinstance(resp, dict) or resp.get("error"):
        # deterministic fallback minimal structure
        fallback = {
            "persona": "mixed_buyer",
            "intent_level": "medium",
            "property_type": brief.get("type") or brief.get("property_type") or "flat",
            "targeting": {
                "target_radius_km": radius,
                "age_filter": [28, 55],
                "behavior_filters": ["likely_to_move"],
                "exclusions": ["agents", "brokers"],
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
                "headline": f"{brief.get('project_name') or 'Project'} — Know Price & Availability",
                "primary_text": "Discover homes with transparent pricing and verified amenities. Book a site visit now.",
                "short_variants": ["Book your visit", "Know price & availability"],
                "cta": "Book Site Visit"
            },
            "whatsapp_bot_notes": {
                "what_to_emphasize": ["price", "location", "parking"],
                "what_to_avoid": ["making possession promises", "inventing amenities"],
                "qualification_priority": ["budget","timeline","intent"]
            }
        }
        # attach model error if present
        if isinstance(resp, dict) and resp.get("error"):
            fallback["generation_error"] = resp
        return fallback

    # 5) Validate keys and merge with deterministic radius if model did not provide it
    # Ensure all top-level keys exist
    required_top = ["persona", "intent_level", "property_type", "targeting",
                    "placements", "budget_plan", "lead_form",
                    "messaging_pillars", "creative_copy", "whatsapp_bot_notes"]
    for k in required_top:
        if k not in resp:
            resp[k] = None

    # Ensure targeting.radius exists; if not, use deterministic radius
    targeting = resp.get("targeting") or {}
    if not targeting.get("target_radius_km"):
        targeting["target_radius_km"] = radius
    # Ensure arrays exist
    targeting.setdefault("behavior_filters", ["likely_to_move"])
    targeting.setdefault("exclusions", ["agents", "brokers"])
    targeting.setdefault("age_filter", [28, 55])
    resp["targeting"] = targeting

    # Ensure placements dict exists with safe defaults
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

    # budget_plan safe defaults
    bp = resp.get("budget_plan") or {}
    bp.setdefault("daily", bp.get("daily", 1000))
    bp.setdefault("total", bp.get("total", None))
    bp.setdefault("currency", "INR")
    resp["budget_plan"] = bp

    # lead_form safe shape
    lf = resp.get("lead_form") or []
    if not isinstance(lf, list) or len(lf) == 0:
        lf = [
            {"id": "budget", "type": "choice", "text": "What is your budget (INR lakhs)?", "required": True},
            {"id": "timeline", "type": "choice", "text": "When do you plan to buy?", "required": True}
        ]
    resp["lead_form"] = lf

    # creative_copy safety
    cc = resp.get("creative_copy") or {}
    cc.setdefault("headline", f"{brief.get('project_name') or 'Project'} — Check Price & Availability")
    cc.setdefault("primary_text", "Contact to know price, site visit, and floor plans.")
    cc.setdefault("short_variants", cc.get("short_variants", ["Book Site Visit"]))
    cc.setdefault("cta", cc.get("cta", "Book Site Visit"))
    resp["creative_copy"] = cc

    # whatsapp notes safety
    wbn = resp.get("whatsapp_bot_notes") or {}
    wbn.setdefault("what_to_emphasize", wbn.get("what_to_emphasize", ["price", "location"]))
    wbn.setdefault("what_to_avoid", wbn.get("what_to_avoid", ["fabricated facts"]))
    wbn.setdefault("qualification_priority", wbn.get("qualification_priority", ["budget", "timeline"]))
    resp["whatsapp_bot_notes"] = wbn

    # final ensure all values JSON serializable (primitives, lists, dicts)
    return resp

