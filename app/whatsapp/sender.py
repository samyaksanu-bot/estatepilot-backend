print("✅ WHATSAPP_ACCESS_TOKEN exists:", bool(os.getenv("WHATSAPP_ACCESS_TOKEN")))
# app/whatsapp/sender.py

import os
import requests

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

GRAPH_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(to: str, message: str):
    """
    Canonical WhatsApp sender.
    DO NOT rename params.
    Always call with positional args.
    """

    if not WHATSAPP_ACCESS_TOKEN:
        raise ValueError("WHATSAPP_ACCESS_TOKEN is missing")

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(GRAPH_URL, json=payload, headers=headers)

    if response.status_code >= 400:
        print("❌ WhatsApp send failed:", response.text)

    return response.json()

