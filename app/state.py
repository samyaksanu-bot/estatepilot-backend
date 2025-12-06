# app/state.py

from typing import Dict, List, Optional

# In-memory user state store (per phone number)
_user_state: Dict[str, dict] = {}

# Lead scoring thresholds (used for rank)
RANKS = [
    ("hot", 70),
    ("warm", 40),
    ("cold", 0),
]


def _calculate_rank(score: int) -> str:
    """
    Map numeric score -> rank label.
    """
    for rank, min_score in RANKS:
        if score >= min_score:
            return rank
    return "cold"


def _initial_state() -> dict:
    """
    Default state for a new WhatsApp user.
    This is the single source of truth for all state fields.
    """
    return {
        # Scoring-related
        "score": 0,
        "rank": "cold",
        "intent_history": [],      # list of detected intents (strings)
        "last_intent": None,
        "message_count": 0,

        # Handoff / escalation
        "handoff_done": False,

        # Conversation flow
        # Funnel will start from "intro" (intro → language → budget → ...)
        "step": "intro",

        # Language preference: "english" | "hindi" | "hinglish" | None
        "language": None,

        # Qualification data (to be filled by flow.py step by step)
        "budget": None,          # e.g. "40–50L" or numeric later
        "location": None,        # text description of preferred area
        "purpose": None,         # "self_use" / "investment" / None
        "timeline": None,        # e.g. "this_month" / "2_3_months" / "later"
        "loan_flag": None,       # "loan_ready" / "cash" / "unsure" / None
        "visit_time": None,      # user’s preferred visit timing text
        "qualified": False,      # True only when funnel deems them qualified

        # Behavioural / UX helpers
        "skip_count": 0,         # how many times user skipped/avoided key questions
        "frustration_flags": [], # list of messages/markers when user shows irritation

        # Optional: store brief conversation history for future AI use
        # Not heavy logging, just last few messages if needed.
        "conversation_history": [],  # list of dicts like {"from": "user/bot", "text": "..."}
    }


def get_state(phone: str) -> dict:
    """
    Get the state dict for a given phone.
    If it doesn't exist yet, create a new one with default values.
    """
    if phone not in _user_state:
        _user_state[phone] = _initial_state()
    else:
        # Ensure older users also get any newly added keys
        # without breaking existing state.
        base = _initial_state()
        base.update(_user_state[phone])
        _user_state[phone] = base

    return _user_state[phone]


def update_state_with_intent(phone: str, intent: Optional[str], intent_weight: int = 5) -> dict:
    """
    Existing intent-based scoring:

    - Increments message_count
    - Adds new intents to history (avoiding duplicates in a row)
    - Increases score by intent_weight per new intent
    - Recalculates rank (hot/warm/cold)
    """
    state = get_state(phone)

    state["message_count"] += 1

    # Avoid double-counting same consecutive intent
    if intent and intent != state.get("last_intent"):
        state["intent_history"].append(intent)
        state["score"] += intent_weight
        state["last_intent"] = intent

    # Recalculate rank based on updated score
    state["rank"] = _calculate_rank(state["score"])
    return state


def mark_handoff(phone: str) -> None:
    """
    Mark that this user's conversation has been handed over to a human agent.
    Further bot logic should not interfere after this flag is set.
    """
    state = get_state(phone)
    state["handoff_done"] = True
