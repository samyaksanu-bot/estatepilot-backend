# app/brain/scoring_rules.py

INTENT_SCORES = {
    # High intent
    "VISIT_INTENT": 30,
    "CALLBACK_REQUEST": 25,
    "DOCUMENT_REQUEST": 15,

    # Medium intent
    "PRICE_QUERY": 8,
    "LOCATION_QUERY": 8,
    "AMENITIES_QUERY": 8,
    "PAYMENT_PLAN": 8,
    "INVENTORY_QUERY": 6,
    "COMPARISON": 6,
    "INVESTMENT_INTENT": 6,
    "TIMELINE_QUERY": 10,

    # Low intent
    "GREETING": 1,
    "VAGUE": 2
}

NEGATIVE_SIGNALS = {
    "not interested": -20,
    "no need": -20,
    "just checking": -8
}

HOT_SCORE = 40
WARM_SCORE = 15
