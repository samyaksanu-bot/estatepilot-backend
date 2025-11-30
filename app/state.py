# app/state.py

user_state = {}

def get_state(phone: str) -> dict:
    if phone not in user_state:
        user_state[phone] = {
            "stage": "start",        # start → discover → qualify → engage → handoff
            "budget": None,
            "location": None,
            "interest": None,
            "messages": 0,
            "visit_ready": False,
            "handoff_done": False
        }

    user_state[phone]["messages"] += 1
    return user_state[phone]
