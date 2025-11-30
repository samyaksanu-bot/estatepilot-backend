user_state = {}

def get_state(phone: str) -> dict:
    if phone not in user_state:
        user_state[phone] = {
            "summary": "",
            "messages_count": 0,
            "handoff_done": False,
            "silent": False
        }
    return user_state[phone]
