# app/intent_engine.py
"""
Very simple rule-based intent detector for English + Hinglish.
Returns a short intent code string like "price_query", "location_query", etc.
"""

from typing import Dict, List

# Keyword lists for each intent (English + Hinglish)
INTENT_KEYWORDS: Dict[str, List[str]] = {
    "price_query": [
        "price", "pricing", "rate", "rates", "cost", "kitna", "kitne", "amount",
        "starting", "start from", "start se", "budget", "per sqft", "per sq ft",
        " kya price", "price kya", "rate kya", "price range"
    ],
    "location_query": [
        "location", "where is", "kaha hai", "kahaan hai", "kidhar", "address",
        "exact location", "near which", "kis area", "which area", "kis side",
        "map", "google map", "landmark", "nearby", "closest metro"
    ],
    "configuration_query": [
        "1bhk", "2bhk", "3bhk", "4bhk",
        "configuration", "configuration options", "unit type",
        "size", "sizes", "sqft", "square feet", "carpet area",
        "area kitni", "kitna area", "layout", "floor plan", "floorplan",
        "plan bhejo", "layout bhejo"
    ],
    "site_visit": [
        "site visit", "visit the site", "site pe", "site par",
        "when can i visit", "kab dekh", "ghar dekhna", "flat dekhna",
        "come and see", "see the project", "visit arrange", "visit fix",
        "site dikhao", "tour", "walkthrough"
    ],
    "amenities_query": [
        "amenities", "facilities", "facility", "features",
        "swimming pool", "club house", "clubhouse", "gym", "garden",
        "parking", "kids play", "kids area", "security", "lift",
        "jogging track", "rooftop", "amenity"
    ],
    "possession_query": [
        "possession", "handover", "handover date",
        "kab milega", "kab tak ready", "ready to move",
        "rera", "oc", "cc", "completion", "delivery date",
        "possession date", "ready possession"
    ],
    "payment_plan_query": [
        "payment plan", "payment schedule", "emi", "loan", "home loan",
        "finance", "bank tie up", "down payment", "token amount",
        "booking amount", "installment", "installments", "milestone",
        "clp", "construction linked plan", "subvention"
    ],
    "builder_trust": [
        "builder", "developer", "who is the builder", "reputation",
        "track record", "delayed", "delay", "on time",
        "previous projects", "past projects", "brand", "trusted"
    ],
    "availability_query": [
        "available", "availability", "units left", "kitne flat bache",
        "sold out", "inventory", "higher floor", "lower floor",
        "corner flat", "garden facing", "road facing"
    ],
    "greeting": [
        "hi", "hii", "hello", "hlo", "hey", "yo",
        "good morning", "good afternoon", "good evening",
        "namaste", "namaskar", "ram ram"
    ],
    "thanks": [
        "thank you", "thanks", "thx", "tysm", "shukriya", "bahut dhanyavad"
    ],
}


def _normalize(text: str) -> str:
    return text.strip().lower()


def detect_intent(text: str) -> str:
    """
    Rule-based intent detection.
    Returns one of the keys in INTENT_KEYWORDS or "small_talk" as fallback.
    """
    t = _normalize(text)

    # Strong greeting detection
    if any(t.startswith(g) or t == g for g in INTENT_KEYWORDS["greeting"]):
        return "greeting"

    # Rule pass through keyword lists
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent in ("greeting", "thanks"):
            continue  # handled separately
        for kw in keywords:
            if kw in t:
                return intent

    # Thanks
    for kw in INTENT_KEYWORDS["thanks"]:
        if kw in t:
            return "thanks"

    # One-word budget messages like "50 lakh"
    if any(word in t for word in ["lakh", "lac", "cr", "crore"]) and any(
        word in t for word in ["budget", "price", "kitna", "amount"]
    ):
        return "price_query"

    # Fallback
    return "small_talk"
