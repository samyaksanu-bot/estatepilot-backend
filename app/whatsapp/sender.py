import os
import requests
import json

# ✅ Required environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")          # Permanent access token
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")        # WhatsApp phone number ID

WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(to_number: str, text: str):
    """
    Sends a WhatsApp text message using the Meta Cloud API
    """

    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        raise Exception("WHATSAPP_TOKEN or PHONE_NUMBER_ID is missing")

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(
        WHATSAPP_API_URL,
        headers=headers,
        json=payload
    )

    # ✅ Log response for debugging
    print("📤 WhatsApp API Status:", response.status_code)
    print("📤 WhatsApp API Response:", response.text)

    if response.status_code >= 400:
        raise Exception(response.text)

    return response.json()
