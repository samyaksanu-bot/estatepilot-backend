# --------------------------------
# INTENT → SCORE WEIGHT
# --------------------------------

INTENT_SCORE = {
    "greeting": 0,
    "price_query": 2,
    "location_query": 1,
    "configuration_query": 2,
    "amenities_query": 1,
    "loan_query": 2,
    "site_visit": 5,
    "purchase_intent_high": 10,
    "vague": 0
}

# --------------------------------
# UPDATE LEAD SCORE
# --------------------------------

def update_score(state: dict, intent: str) -> dict:
    score = state.get("score", 0)
    score += INTENT_SCORE.get(intent, 0)
    state["score"] = score
    state["intent_history"] = state.get("intent_history", [])
    state["intent_history"].append(intent)

    # Rank assignment
    if score >= 12:
        state["rank"] = "HOT"
    elif score >= 6:
        state["rank"] = "WARM"
    else:
        state["rank"] = "COLD"

    return state
