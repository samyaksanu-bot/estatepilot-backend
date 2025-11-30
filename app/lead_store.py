import datetime

LEADS = []

def save_lead(phone: str, state: dict):
    LEADS.append({
        "phone": phone,
        "summary": state.get("summary", ""),
        "handoff_time": datetime.datetime.utcnow().isoformat()
    })
