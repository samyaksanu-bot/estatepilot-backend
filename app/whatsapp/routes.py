from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

from app.whatsapp.sender import send_whatsapp_message

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# ✅ Webhook verification (GET)
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))

    return PlainTextResponse("Verification failed", status_code=403)


# ✅ Incoming WhatsApp messages (POST)
@router.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()
    print("📩 Incoming payload:")
    print(json.dumps(payload, indent=2))

    try:
       entry = payload.get("entry", [])[0]
changes = entry.get("changes", [])[0]
value = changes.get("value", {})

messages = value.get("messages", [])

# If no "messages" key → ignore (likely status update)
if not messages:
    print("⚠ No user message in this update. Skipping.")
    return {"status": "ignored"}

message = messages[0]

from_number = message.get("from")
text = message.get("text", {}).get("body")

# If it's not a text message (image, reaction, etc.)
if not text:
    print("⚠ No text body found in message.")
    return {"status": "no_text"}

        reply = f"✅ EstatePilot Working.\nYou said:\n{text}"

        send_whatsapp_message(
            to=from_number,
            text=reply
        )

    except Exception as e:
        print("❌ Error processing message:", str(e))

    return {"status": "received"}

