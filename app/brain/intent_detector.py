# app/brain/intent_detector.py

import re

INTENTS = {
    "GREETING": [
        "hi", "hello", "hey", "namaste"
    ],

    "PRICE_QUERY": [
        "price", "cost", "budget", "kitna", "daam",
        "starting price", "total amount"
    ],

    "LOCATION_QUERY": [
        "location", "area", "kidhar", "where", 
        "kis area", "region"
    ],

    "AMENITIES_QUERY": [
        "amenities", "facilities", "aas paas",
        "school", "hospital", "nearby"
    ],

    "INVENTORY_QUERY": [
        "2bhk", "3bhk", "plot", "size", "carpet area",
        "super built", "floor"
    ],

    "VISIT_INTENT": [
        "site visit", "visit", "dekhna", "location bhejo"
    ],

    "CALLBACK_REQUEST": [
        "call me", "phone", "baat karni", "callback"
    ],

    "PAYMENT_PLAN": [
        "emi", "loan", "down payment", "installment"
    ],

    "LEGAL_TRUST": [
        "rera", "legal", "approved", "registry"
    ],

    "OBJECTION": [
        "expensive", "mehnga", "price high", "discount"
    ],

    "DOCUMENT_REQUEST": [
        "brochure", "floor plan", "images", "layout"
    ],

    "VAGUE": [
        "tell me more", "explain", "details", "worth it"
    ]
}


def detect_intent(text: str) -> str:
    text = text.lower().strip()

    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                return intent

    return "UNKNOWN"
