# app/state.py

from typing import Dict, List

# In-memory user state store
_user_state: Dict[str, dict] = {}

# Lead scoring thresholds
RANKS = [
    ("hot", 70),
    ("warm", 40),
    ("cold", 0),
]


def _calculate_rank(score: int) -> str:
    for rank, min_score in RANKS:
        if score >= min_score:
            return rank
    return "cold"


def get_state(phone: str) -> dict:
    if phone not in _user_state:
        _user_state[phone] = {
            "score": 0,
            "rank": "cold",
            "intent_history": [],
            "last_intent": None,
            "message_count": 0,
            "handoff_done": False,
        }
    return _user_state[phone]


def update_state_with_intent(phone: str, intent: str, intent_weight: int = 5) -> dict:
    state = get_state(phone)

    state["message_count"] += 1

    # Avoid double counting same consecutive intent
    if intent and intent != state["last_intent"]:
        state["intent_history"].append(intent)
        state["score"] += intent_weight
        state["last_intent"] = intent

    state["rank"] = _calculate_rank(state["score"])
    return state


def mark_handoff(phone: str):
    state = get_state(phone)
    state["handoff_done"] = True
