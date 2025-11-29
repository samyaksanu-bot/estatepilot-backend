# app/state.py

# ----------------------------
# Global brain state (shared)
# ----------------------------
COUNTERS = None
SCORING = None

# ----------------------------
# Per-user conversation state
# ----------------------------
user_state = {}

def get_state(phone: str):
    if phone not in user_state:
        user_state[phone] = {
            "last_intent": None,
            "last_question": None,
            "score": 0,
            "language": "english"
        }
    return user_state[phone]
