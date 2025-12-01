import os
import requests

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

def send_whatsapp_message(to: str, text: str):
    """
    Send a WhatsApp text message using Meta Cloud API
    """

    if not WHATSAPP_ACCESS_TOKEN:
        print("❌ WHATSAPP_ACCESS_TOKEN is missing")
        return

    if not PHONE_NUMBER_ID:
        print("❌ WHATSAPP_PHONE_NUMBER_ID is missing")
        return

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code >= 300:
            print("❌ WhatsApp send failed")
            print(response.status_code, response.text)
        else:
            print("✅ WhatsApp message sent")

    except Exception as e:
        print("❌ WhatsApp request error:", str(e))
