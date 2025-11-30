# app/state.py

# Per-user conversation memory (in-memory for now)
user_state = {}

def get_state(phone: str) -> dict:
    """
    Returns or initializes conversation state for a phone number.
    """

    if phone not in user_state:
        user_state[phone] = {
            "step": "intro",        # intro → intent → budget → location → visit → done
            "intent": None,         # price | location | availability | visit | general
            "budget": None,
            "location": None,
            "visit_time": None,
            "qualified": False,
            "last_bot_message": None
        }

    return user_state[phone]
