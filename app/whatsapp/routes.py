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
        messages = value.get("messages", [])
        if not messages:
            return {"status": "ignored"}

        message = messages[0]

        # ✅ Only text messages
        if message.get("type") != "text":
            return {"status": "ignored"}

        from_number = message["from"]
        user_text = message["text"]["body"].strip()

        # ==============================
        # ✅ STEP 1: Detect intent
        # ==============================
        from app.intent_engine import detect_intent
        intent = detect_intent(user_text)

        # ==============================
        # ✅ STEP 2: Update state + score
        # ==============================
        from app.state import update_state_with_intent
        state = update_state_with_intent(from_number, intent)

        # ==============================
        # ✅ STEP 3: Template response
        # ==============================
        from app.template_engine import get_template
        reply = get_template(intent, state)

        # ==============================
        # ✅ STEP 4: AI fallback (ONLY if needed)
        # ==============================
        if not reply:
            from app.reply_engine import fallback_ai_reply
            reply = fallback_ai_reply(
                user_text=user_text,
                state=state
            )

        # ==============================
        # ✅ STEP 5: Send WhatsApp reply
        # ==============================
        from app.whatsapp.sender import send_whatsapp_message
        send_whatsapp_message(from_number, reply)

        return {"status": "received"}

    except Exception as e:
        import traceback
        print("❌ WhatsApp webhook error")
        traceback.print_exc()
        return {"status": "error"}
