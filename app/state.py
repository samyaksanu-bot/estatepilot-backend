# app/state.py

# Per-user conversation state
user_state = {}


def get_state(phone: str) -> dict:
    """
    Returns or initializes the state for a given phone number.
    """
    if phone not in user_state:
        user_state[phone] = {
            "step": "intro",        # intro → budget → location → visit → done
            "budget": None,
            "location": None,
            "visit_time": None,
            "qualified": False,
            "last_intent": None,
        }

    return user_state[phone]
