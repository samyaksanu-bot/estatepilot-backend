from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

from app.whatsapp.sender import send_whatsapp_message

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


# ✅ WEBHOOK VERIFICATION
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))

    return PlainTextResponse("Verification failed", status_code=403)


# ✅ INCOMING MESSAGES
@router.post("/webhook")
async def incoming_webhook(request: Request):
    payload = await request.json()

    print("📩 RAW WHATSAPP PAYLOAD")
    print(json.dumps(payload, indent=2))

    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        # ✅ SAFELY CHECK FOR MESSAGE
        if "messages" not in value:
            print("⚠️ No messages key found")
            return {"status": "ignored"}

        message = value["messages"][0]
        sender = message["from"]

        text = (
            message.get("text", {})
            .get("body", "No text message")
        )

        print(f"✅ Sender: {sender}")
        print(f"✅ Message text: {text}")

        # ✅ FORCE AUTO-REPLY (NO CONDITIONS)
        send_whatsapp_message(
            sender,
            "✅ Bot is live. We received your message."
        )

    except Exception as e:
        print("❌ ERROR:", str(e))

    return {"status": "received"}


