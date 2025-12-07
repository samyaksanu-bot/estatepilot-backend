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
        "intent_history": [],
        "last_intent": None,
        "message_count": 0,

        # Handoff / escalation
        "handoff_done": False,

        # Conversation flow
        "step": "intro",

        # Language preference
        "language": None,

        # Qualification data
        "budget": None,
        "location": None,
        "purpose": None,
        "timeline": None,
        "loan_flag": None,
        "visit_time": None,
        "qualified": False,
        "stop_questions": False,

        # Behaviour tracking
        "skip_count": 0,
        "frustration_flags": [],

        # Conversation memory (for AI fallback)
        "conversation_history": [],     # [{from: "user"|"bot", text: "..."}]

        # NEW — AI integration mode:
        # "lead" = from ad (qualification)
        # "personal" = random chat / non-lead
        "conversation_mode": None,

        # NEW — for attaching project details:
        # Example:
        # {
        #   "name": "...",
        #   "price_range": "...",
        #   "location": "...",
        #   "usp": "...",
        #   "unit_types": "2BHK / 3BHK",
        # }
        "project_context": None,
    }


def get_state(phone: str) -> dict:
    """
    Get the state dict for a given phone.
    If it doesn't exist yet, create a new one with default values.
    """
    if phone not in _user_state:
        _user_state[phone] = _initial_state()
    else:
        # ensure backward compatibility if keys were added later
        base = _initial_state()
        base.update(_user_state[phone])
        _user_state[phone] = base

    return _user_state[phone]


def update_state_with_intent(phone: str, intent: Optional[str], intent_weight: int = 5) -> dict:
    """
    Scoring logic (unchanged).
    """
    state = get_state(phone)

    state["message_count"] += 1

    if intent and intent != state.get("last_intent"):
        state["intent_history"].append(intent)
        state["score"] += intent_weight
        state["last_intent"] = intent

    state["rank"] = _calculate_rank(state["score"])
    return state


def mark_handoff(phone: str) -> None:
    """
    Hand over to a human agent.
    """
    state = get_state(phone)
    state["handoff_done"] = True


# ===================================================
# NEW — Conversation history helper for AI memory
# ===================================================

def append_history(phone: str, sender: str, text: str) -> None:
    """
    Store limited conversation history for AI fallback.
    Only last N messages are kept to reduce memory.
    """
    state = get_state(phone)

    entry = {"from": sender, "text": text}
    state["conversation_history"].append(entry)

    # trim to last 15 messages max
    if len(state["conversation_history"]) > 15:
        state["conversation_history"] = state["conversation_history"][-15:]
    def stop_questioning(phone: str) -> None:
    """
    Use this flag when:
    - user qualified OR
    - rank becomes hot OR
    - user explicitly requests call/visit OR
    - user avoids questions multiple times OR
    - user shows irritation
    """
    state = get_state(phone)
    state["stop_questions"] = True
