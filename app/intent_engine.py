import re

# --------------------------------
# INTENT KEYWORDS (EN + HINGLISH + HINDI)
# --------------------------------

INTENT_KEYWORDS = {

    "greeting": [
        "hi", "hello", "hey", "namaste", "hii", "hlw",
        "good morning", "good evening"
    ],

    "price_query": [
        "price", "cost", "budget", "pricing", "rate",
        "kitna", "kitne ka", "price kya", "cost kya",
        "starting price", "range", "budget batao"
    ],

    "location_query": [
        "location", "where", "area", "place",
        "kaha", "kidhar", "kis area", "location kya",
        "address", "map"
    ],

    "configuration_query": [
        "bhk", "2bhk", "3bhk", "1bhk",
        "flat size", "square feet",
        "rooms", "bedroom",
        "kitne room", "ghar size"
    ],

    "amenities_query": [
        "amenities", "facilities",
        "gym", "park", "parking", "lift",
        "swimming pool", "security",
        "kya kya milega", "facility kya"
    ],

    "site_visit": [
        "site visit", "visit", "dekhna", "dekh sakta",
        "location visit", "project visit",
        "kab dekh sakte", "site dikhao"
    ],

    "purchase_intent_high": [
        "book", "booking", "final", "buy",
        "purchase", "advance",
        "ready to buy", "sure buy",
        "serious", "confirm", "payment"
    ],

    "loan_query": [
        "loan", "emi", "bank loan",
        "finance", "home loan",
        "emi kitna", "loan milega"
    ]
}

# --------------------------------
# INTENT DETECTOR
# --------------------------------

def detect_intent(text: str) -> str:
    if not text:
        return "vague"

    text = text.lower().strip()

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            # strict word boundary match
            if re.search(rf"\b{re.escape(kw)}\b", text):
                return intent

    return "vague"

