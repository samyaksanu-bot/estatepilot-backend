from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

# WhatsApp sender
from app.whatsapp.sender import send_whatsapp_message

# Conversation brain
from app.conversation_engine import next_reply
from app.state import get_state

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# -------------------------------------------------
# 1. WHATSAPP WEBHOOK VERIFICATION (GET)
# -------------------------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# -------------------------------------------------
# 2. INCOMING WHATSAPP MESSAGES (POST)
# -------------------------------------------------
@router.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()

    try:
        entry = payload.get("entry", [])
        if not entry:
            return {"status": "ignored"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ignored"}

        value = changes[0].get("value", {})

        # Ignore delivery / read / status events
        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]

        from_number = message.get("from")
        if not from_number:
            return {"status": "ignored"}

        # Only handle text messages
        text = message.get("text", {}).get("body")
        if not text:
            return {"status": "ignored"}

        # ---------------- CORE INTELLIGENCE ----------------
        state = get_state(from_number)
       from app.reply_engine import generate_reply

reply = generate_reply(text, state)

        if reply:
            send_whatsapp_message(
                to=from_number,
                message=reply
            )

    except Exception as e:
        print("❌ WhatsApp processing error:", str(e))

    return {"status": "received"}
