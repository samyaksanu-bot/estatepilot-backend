# app/state.py

# In-memory user state (OK for now)
user_state = {}

def get_state(phone: str) -> dict:
    """
    Returns or initializes state for a WhatsApp user.
    KEEP THIS STABLE. Do NOT add random keys.
    """
    if phone not in user_state:
        user_state[phone] = {
            "step": "intro",          # intro → intent → budget → location → soft_visit → handoff
            "intent": None,           # price | location | details | visit
            "budget": None,
            "location": None,
            "messages_count": 0,
            "handoff": False
        }

    return user_state[phone]
