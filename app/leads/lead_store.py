import json
from datetime import datetime

def save_lead(phone: str, message: str, client_id: str):
    lead = {
        "phone": phone,
        "message": message,
        "client_id": client_id,
        "time": datetime.utcnow().isoformat()
    }

    with open("leads.json", "a") as f:
        f.write(json.dumps(lead) + "\n")
