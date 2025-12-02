from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import traceback

from app.whatsapp.sender import send_whatsapp_message
from app.state import get_state
from app.reply_engine import generate_reply  # ✅ correct import

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# -------------------------------
# Webhook verification (GET)
# -------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# -------------------------------
# Incoming messages (POST)
# -------------------------------
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
        text = message["text"]["body"]

        # 1️⃣ Detect intent
intent = detect_intent(text)

# 2️⃣ Update intent depth
update_intent_depth(from_number, intent)

# 3️⃣ Update score + rank
state = update_lead_state(from_number, intent, text)

# 4️⃣ Get depth for reply selection
depth = get_intent_depth(from_number, intent)

# 5️⃣ Generate reply
reply = generate_reply(
    intent=intent,
    context={"price": "45 lakh"},
    depth=depth - 1
)

send_whatsapp_message(from_number, reply)

print("📊 LEAD STATUS:", state["rank"], "SCORE:", state["score"])

        # ✅ Prevent duplicate replies
        state = get_state(from_number)
        if state.get("last_message_id") == message_id:
            return {"status": "duplicate_ignored"}

        state["last_message_id"] = message_id

        # ✅ LLM / AI reply
        reply = generate_reply(
            user_id=from_number,
            user_message=text
        )

        if reply:
            send_whatsapp_message(from_number, reply)

        return {"status": "received"}

    except Exception:
        print("❌ WhatsApp webhook error")
        traceback.print_exc()
        return {"status": "error"}
