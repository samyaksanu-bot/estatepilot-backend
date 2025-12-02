from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import traceback

from app.whatsapp.sender import send_whatsapp_message
from app.intent_engine import detect_intent
from app.state import get_state, update_state_with_intent, mark_handoff
from app.template_engine import get_template
from app.reply_engine import ai_fallback_reply
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

        # ✅ Only text messages
        if message.get("type") != "text":
            return {"status": "ignored"}

        from_number = message.get("from")
        user_text = message.get("text", {}).get("body", "").strip().lower()
        message_id = message.get("id")

        if not from_number or not user_text:
            return {"status": "ignored"}

        # ----------------------------------------
        # STATE SAFETY
        # ----------------------------------------
        state = get_state(from_number)

        # Prevent duplicate Meta retries
        if state.get("last_message_id") == message_id:
            return {"status": "duplicate_ignored"}

        state["last_message_id"] = message_id

        # ----------------------------------------
        # STEP 1: Detect Intent
        # ----------------------------------------
        intent = detect_intent(user_text)

        # ----------------------------------------
        # STEP 2: Update score & rank
        # ----------------------------------------
        state = update_state_with_intent(from_number, intent)

        # ----------------------------------------
        # STEP 3: HUMAN HANDOFF LOGIC ✅
        # ----------------------------------------
        if (
            state["rank"] == "hot"
            or intent == "site_visit"
            or any(x in user_text for x in ["call", "visit", "agent", "site"])
        ):
            if not state.get("handoff_done"):
                send_whatsapp_message(
                    from_number,
                    "Perfect 👍 I’ll have our advisor call you shortly to confirm the details."
                )
                mark_handoff(from_number)
            return {"status": "handoff"}

        # ----------------------------------------
        # STEP 4: Template-based reply
        # ----------------------------------------
        reply_text = get_template(intent, state)

        # ----------------------------------------
        # STEP 5: AI fallback (only if template fails)
        # ----------------------------------------
        if not reply_text:
            reply_text = ai_fallback_reply(user_text)

        # ----------------------------------------
        # STEP 6: Send WhatsApp reply
        # ----------------------------------------
        if reply_text:
            send_whatsapp_message(from_number, reply_text)

        return {"status": "received"}

    except Exception:
        print("❌ WhatsApp webhook error")
        traceback.print_exc()
        return {"status": "error"}
