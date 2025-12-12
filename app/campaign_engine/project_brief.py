# app/campaign_engine/project_brief.py
import re
import io
from typing import Dict, Any, List, Optional

# optional PDF text extraction; do not fail if PyPDF2 missing
try:
    from PyPDF2 import PdfReader  # type: ignore
except Exception:
    PdfReader = None  # type: ignore

from app.ai_engine import call_gpt_json

# -------------------------
# Helpers: parsing utilities
# -------------------------
_PRICE_RE = re.compile(r"₹?\s*([0-9\.,]+)\s*(lakh|lakhs|lac|crore|cr|k)?", re.IGNORECASE)
_RANGE_RE = re.compile(r"([0-9\.,]+)\s*(?:-|to|–)\s*([0-9\.,]+)\s*(lakh|lakhs|crore|cr)?", re.IGNORECASE)


def _normalize_number(text: str) -> Optional[float]:
    """
    Convert number strings like '65', '65.5', '1.2' (with commas/dots) to float.
    """
    if text is None:
        return None
    t = str(text).replace(",", "").strip()
    try:
        return float(t)
    except Exception:
        return None


def _scale_value(value: float, unit: Optional[str]) -> Optional[float]:
    """
    Convert numeric + unit into Lakhs (float).
    E.g., (1.2, 'cr') -> 120.0 (lakhs)
    """
    if value is None:
        return None
    if not unit:
        return value  # assume already in lakhs
    unit = unit.lower()
    if "cr" in unit or "crore" in unit:
        return value * 100.0
    if "lac" in unit or "lakh" in unit or "lakhs" in unit:
        return value
    if unit == "k":
        # k assumed thousands of rupees -> convert to lakhs
        return value / 100.0
    return value


def _parse_price_from_text(text: str) -> (Optional[float], Optional[float]):
    """
    Try to extract min/max price (in Lakhs) from free text.
    Returns (min_lakh, max_lakh)
    """
    if not text:
        return None, None
    # 1) explicit range with units
    m = _RANGE_RE.search(text)
    if m:
        a = _normalize_number(m.group(1))
        b = _normalize_number(m.group(2))
        unit = m.group(3)
        a_scaled = _scale_value(a, unit)
        b_scaled = _scale_value(b, unit)
        if a_scaled and b_scaled:
            return min(a_scaled, b_scaled), max(a_scaled, b_scaled)

    # 2) single price mentions
    prices = []
    for m in _PRICE_RE.finditer(text):
        num = _normalize_number(m.group(1))
        unit = m.group(2)
        scaled = _scale_value(num, unit)
        if scaled:
            prices.append(scaled)
    if len(prices) == 1:
        return prices[0], prices[0]
    if len(prices) >= 2:
        return min(prices), max(prices)
    return None, None


def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    If PyPDF2 is available, extract text; otherwise return empty string.
    """
    if not PdfReader:
        return ""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n".join(pages)
    except Exception:
        return ""


# -------------------------
# GPT helper (for classification only)
# -------------------------
def _call_brief_classifier(brief_sample: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ask GPT to classify buyer persona and zone, and produce a short neutral summary.
    Strict JSON only. NO inventing facts. If uncertain, return nulls.
    """
    system_prompt = """
You are EstatePilot Brief Classifier. You MUST return ONLY valid JSON and follow these rules:
- Do NOT invent any factual detail (amenities, RERA, prices). Use only the fields provided.
- Provide classification only (persona, zone_hint) and a one-line factual summary based on given fields.
- If uncertain, return null for that field.
OUTPUT SCHEMA:
{
  "persona": str|null,                # e.g., "mid_income_family","premium_end_user","investor","nri","mixed"
  "persona_confidence": "low"|"medium"|"high",
  "zone_hint": "urban"|"suburban"|"remote"|null,
  "zone_confidence": "low"|"medium"|"high",
  "short_summary": str|null
}
"""
    user_prompt = f"PROJECT_BRIEF_SAMPLE:{brief_sample}\n\nReturn the JSON following the schema."
    resp = call_gpt_json(system_prompt=system_prompt, user_prompt=user_prompt, model="gpt-4.1", temperature=0.0, max_tokens=250, retries=1)
    # If model returned error, return safe defaults
    if not isinstance(resp, dict) or resp.get("error"):
        return {
            "persona": None,
            "persona_confidence": "low",
            "zone_hint": None,
            "zone_confidence": "low",
            "short_summary": None
        }
    # Keep only allowed keys
    return {
        "persona": resp.get("persona"),
        "persona_confidence": resp.get("persona_confidence"),
        "zone_hint": resp.get("zone_hint"),
        "zone_confidence": resp.get("zone_confidence"),
        "short_summary": resp.get("short_summary")
    }


# -------------------------
# Main exported function
# -------------------------
def build_project_brief(project_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hybrid extractor: Python-first extraction + GPT-assisted classification.
    Returns a strict dict with normalized fields and missing_fields list.
    """
    p = project_payload or {}

    # Basic fields (prefer explicit keys)
    name = p.get("project_name") or p.get("name") or p.get("projectTitle") or None
    location = p.get("location") or p.get("locality") or p.get("address") or None
    raw_price_text = p.get("price_text") or p.get("price") or p.get("price_range") or ""
    price_min = p.get("price_min_lakh") or p.get("price_min") or None
    price_max = p.get("price_max_lakh") or p.get("price_max") or None
    property_type = (p.get("type") or p.get("property_type") or p.get("category") or "").lower() or None
    unit_types = p.get("unit_types") or p.get("units") or []
    floors = p.get("floors") or p.get("no_of_floors") or None
    amenities = p.get("amenities") or p.get("features") or []
    status = p.get("status") or p.get("project_status") or None
    rera = p.get("rera_number") or p.get("rera") or None
    notes = p.get("notes") or p.get("description") or ""
    images = p.get("images") or []
    logo_url = p.get("logo_url") or p.get("logo") or None

    # 1) If price min/max not provided, try to parse from raw text/description
    if (not price_min or not price_max) and raw_price_text:
        pm, px = _parse_price_from_text(raw_price_text)
        if pm and not price_min:
            price_min = pm
        if px and not price_max:
            price_max = px

    # 2) Also try parsing from notes (unstructured)
    if (not price_min or not price_max) and notes:
        pm, px = _parse_price_from_text(notes)
        if pm and not price_min:
            price_min = pm
        if px and not price_max:
            price_max = px

    # 3) If PDF text provided (as bytes in 'pdf_bytes'), extract text and parse
    pdf_text = ""
    if p.get("pdf_bytes"):
        try:
            pdf_bytes = p.get("pdf_bytes")
            if isinstance(pdf_bytes, (bytes, bytearray)):
                pdf_text = _extract_text_from_pdf_bytes(bytes(pdf_bytes))
                # try parse price from pdf text
                if pdf_text and (not price_min or not price_max):
                    pm, px = _parse_price_from_text(pdf_text)
                    if pm and not price_min:
                        price_min = pm
                    if px and not price_max:
                        price_max = px
        except Exception:
            pdf_text = ""

    # 4) Detect future infrastructure hints (simple keywords)
    infra_keywords = ["highway", "metro", "ring road", "expressway", "airport", "industrial corridor", "upcoming metro", "proposed expressway"]
    future_infra = False
    infra_matches = []
    combined_search_text = " ".join(filter(None, [notes, raw_price_text, pdf_text, location or ""])).lower()
    for kw in infra_keywords:
        if kw in combined_search_text:
            future_infra = True
            infra_matches.append(kw)

    # 5) Zone hint from payload or quick rules
    zone = p.get("zone") or None
    if not zone:
        # quick heuristic: if location text contains 'village' or 'outer' or ' outskirts' -> remote
        l = (location or "").lower()
        if any(tok in l for tok in ("village", "outskirts", "outer", "remote", "periphery")):
            zone = "remote"
        elif any(tok in l for tok in ("colony", "sector", "zone", "phase", "block", "area", "road", "street")):
            # ambiguous -> default to suburban unless explicit urban hint
            zone = "suburban"
        else:
            zone = None

    # 6) Normalize amenities: only keep strings and do not invent anything (strict)
    clean_amenities = []
    for a in (amenities or []):
        if not a:
            continue
        if isinstance(a, dict):
            text = a.get("name") or a.get("title") or ""
        else:
            text = str(a)
        t = text.strip()
        if t:
            clean_amenities.append(t)

    # 7) Build preliminary brief for GPT classification (small, factual)
    brief_for_gpt = {
        "project_name": name,
        "location": location,
        "price_min_lakh": price_min,
        "price_max_lakh": price_max,
        "property_type": property_type,
        "unit_types": unit_types,
        "floors": floors,
        "amenities_provided_explicitly": clean_amenities,
        "status": status,
        "rera_number": rera,
        "future_infrastructure_mentioned": future_infra,
        "notes_sample": (notes or "")[:800],  # keep short
        "pdf_text_present": bool(pdf_text)
    }

    # 8) Ask GPT only to classify persona and zone & short summary (no facts)
    classification = _call_brief_classifier(brief_for_gpt)

    # 9) Missing fields detection (fields we require for full campaign safety)
    required = ["project_name", "location", "price_min_lakh", "price_max_lakh", "property_type"]
    missing = []
    for key in required:
        val = {
            "project_name": name,
            "location": location,
            "price_min_lakh": price_min,
            "price_max_lakh": price_max,
            "property_type": property_type
        }.get(key)
        if val in (None, "", [], {}):
            missing.append(key)

    # 10) Input instructions for missing fields (short)
    input_instructions = []
    if "project_name" in missing:
        input_instructions.append("Provide the official project name.")
    if "location" in missing:
        input_instructions.append("Provide a specific location or locality (e.g., 'Anisabad, Patna').")
    if "price_min_lakh" in missing or "price_max_lakh" in missing:
        input_instructions.append("Provide price range (e.g., '65-80 Lakhs' or '₹75 Lakh').")
    if "property_type" in missing:
        input_instructions.append("Specify property type (flat / villa / plot / commercial).")

    # 11) Risk notes (if builder proceeds despite missing fields)
    risk_notes = []
    if missing:
        risk_notes.append("Some required fields are missing. Campaign quality will be reduced and leads may be low-quality.")
    if future_infra and not location:
        risk_notes.append("Future infrastructure detected in text but exact location missing — verify before running ads.")
    if pdf_text and not (price_min and price_max):
        risk_notes.append("PDF contains text but price could not be fully extracted. Review price fields.")

    # 12) Final normalized brief object returned to callers
    brief = {
        "project_name": name,
        "location": location,
        "price_min_lakh": price_min,
        "price_max_lakh": price_max,
        "property_type": property_type,
        "unit_types": unit_types,
        "floors": floors,
        "amenities": clean_amenities,
        "status": status,
        "rera_number": rera,
        "notes": notes,
        "images": images,
        "logo_url": logo_url,
        "pdf_text": pdf_text,
        "future_infrastructure": future_infra,
        "infrastructure_matches": infra_matches,
        "zone": classification.get("zone_hint") or zone,
        "zone_confidence": classification.get("zone_confidence"),
        "buyer_persona": classification.get("persona"),
        "buyer_persona_confidence": classification.get("persona_confidence"),
        "short_summary": classification.get("short_summary"),
        "missing_fields": missing,
        "input_instructions": input_instructions,
        "risk_notes": risk_notes,
    }

    return brief
