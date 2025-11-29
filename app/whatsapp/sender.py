import os
import requests

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

GRAPH_URL = "https://graph.facebook.com/v19.0"

def send_whatsapp_message(to: str, message: str):
    """
    Send a WhatsApp text message using Meta Cloud API
    """

    if not META_ACCESS_TOKEN or not PHONE_NUMBER_ID:
        raise Exception("WHATSAPP_TOKEN or PHONE_NUMBER_ID is missing")

    url = f"{GRAPH_URL}/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code >= 300:
        raise Exception(f"WhatsApp send failed: {response.text}")

    return response.json()
