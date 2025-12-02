# app/brain/state_manager.py

from collections import defaultdict

# In-memory store (for now)
# Later this can be Redis / DB
USER_STATE = defaultdict(dict)


def get_user_state(user_id: str) -> dict:
    """
    Returns current state for a user
    """
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {
            "intent_depth": defaultdict(int),
            "last_intent": None,
            "score": 0,
            "rank": "COLD"
        }
    return USER_STATE[user_id]


def update_intent_depth(user_id: str, intent: str):
    state = get_user_state(user_id)
    state["intent_depth"][intent] += 1
    state["last_intent"] = intent


def get_intent_depth(user_id: str, intent: str) -> int:
    state = get_user_state(user_id)
    return state["intent_depth"].get(intent, 0)


def update_lead_state(user_id: str, intent: str, text: str):
    from app.brain.rank_engine import update_score, update_rank

    state = get_user_state(user_id)

    update_score(state, intent, text)
    update_rank(state)

    return state
