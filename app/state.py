user_state = {}

def get_state(phone: str) -> dict:
    if phone not in user_state:
        user_state[phone] = {
            "step": "intro",
            "budget": None,
            "location": None,
            "messages_count": 0,
            "intent_score": 0,
            "ready_for_visit": False,
            "handoff_done": False
        }
    return user_state[phone]
