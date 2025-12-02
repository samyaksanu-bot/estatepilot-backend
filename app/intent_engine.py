# app/intent_engine.py

import re

INTENT_PATTERNS = {
    "price_query": [
        r"price", r"cost", r"budget", r"rate",
        r"kitna", r"daam", r"kitne ka", r"starting"
    ],
    "location_query": [
        r"location", r"area", r"address", r"kahan",
        r"kahaan", r"kis area", r"place", r"near"
    ],
    "site_visit": [
        r"visit", r"site visit", r"dekhna", r"mil sakte",
        r"kab aa sakte", r"onsite"
    ],
    "configuration": [
        r"bhk", r"flat size", r"area sqft", r"size",
        r"2bhk", r"3bhk"
    ],
    "amenities": [
        r"amenities", r"facilities", r"park",
        r"gym", r"lift", r"power backup"
    ],
    "loan_query": [
        r"loan", r"emi", r"bank", r"home loan",
        r"finance", r"interest"
    ],
    "timeline": [
        r"ready", r"possession", r"handover",
        r"kab milega", r"completion"
    ]
}


def detect_intent(text: str) -> str | None:
    text = text.lower()

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return intent

    return None
