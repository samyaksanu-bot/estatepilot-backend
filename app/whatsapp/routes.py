from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import traceback

from app.whatsapp.sender import send_whatsapp_message
from app.intent_engine import detect_intent
from app.state import get_state
from app.reply_engine import generate_reply   # ✅ ONE reply engine only

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


# ------------------------------------------------
# Webhook verification (GET)
# ------------------------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# ------------------------------------------------
# Incoming messages (POST)
# ------------------------------------------------
@router.post("/webhook")
async def receive_message(request: Request):
    try:
        payload = await request.json()

        entry = payload.get("entry", [])
        if not entry:
            return {"status": "ignored"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ignored"}

        value = changes[0].get("value", {})
        messages = value.get("messages")
        if not messages:
            return {"status": "ignored"}

        message = messages[0]
        if message.get("type") != "text":
            return {"status": "ignored"}

        message_id = message.get("id")
        from_number = message.get("from")
        user_text = message["text"]["body"]

      # Optional: dedupe using state (Meta retry protection)
        try:
            state = get_state(from_number)
            if state.get("last_message_id") == message_id:
                return {"status": "duplicate_ignored"}
            state["last_message_id"] = message_id
        except Exception:
            # If state store fails, we still answer – don’t crash webhook
            state = {}

        # 1) Detect intent
        intent = detect_intent(user_text)

        # 2) Generate reply from template engine
        reply_text = generate_reply(intent=intent, user_text=user_text)

        # 3) Send WhatsApp message
        send_whatsapp_message(from_number, reply_text)

        return {"status": "received"}

    except Exception as e:
        print("❌ WhatsApp webhook error:", str(e))
        return {"status": "error"}
      
