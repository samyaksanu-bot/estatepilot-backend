from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import traceback

from app.whatsapp.sender import send_whatsapp_message
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

        # ✅ State
        state = get_state(from_number)

        # ✅ Prevent Meta retry duplicates
        if state.get("last_message_id") == message_id:
            return {"status": "duplicate"}

        state["last_message_id"] = message_id

        # ✅ ONE reply engine
        reply = generate_reply(
            user_id=from_number,
            user_message=user_text,
            state=state
        )

        if reply:
            send_whatsapp_message(from_number, reply)

        return {"status": "received"}

    except Exception:
        print("❌ WhatsApp webhook error")
        traceback.print_exc()
        return {"status": "error"}

