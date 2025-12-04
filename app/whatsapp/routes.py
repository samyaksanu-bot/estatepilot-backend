from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import traceback
import os

from app.whatsapp.sender import send_whatsapp_message
from app.intent_engine import detect_intent
from app.template_engine import get_template
from app.state import (
    get_state,
    update_state_with_intent,
    mark_handoff,
)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "verify_token")


# --------------------------------------------------
# META WEBHOOK VERIFICATION
# --------------------------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# --------------------------------------------------
# INCOMING WHATSAPP MESSAGE HANDLER
# --------------------------------------------------
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

        from_number = message.get("from")
        user_text = message.get("text", {}).get("body", "").strip()
        message_id = message.get("id")

        if not from_number or not user_text:
            return {"status": "ignored"}

        # Load current state
        state = get_state(from_number)

        # Dedup: ignore same message id
        if state.get("last_message_id") == message_id:
            return {"status": "duplicate_ignored"}

        state["last_message_id"] = message_id

        # If already handed off to human, do nothing
        if state.get("handoff_done"):
            return {"status": "agent_handling"}

        # Detect intent
        intent = detect_intent(user_text)

        # Update state with new intent
        state = update_state_with_intent(from_number, intent)

        # If hot lead → handoff
        explicit_handoff_keywords = ["call me", "site visit", "contact agent", "talk to person"]
        if state.get("rank") == "hot" or any(k.lower() in user_text.lower() for k in explicit_handoff_keywords):
            send_whatsapp_message(
                from_number,
                "✅ Perfect. Our advisor will call you shortly to confirm the details."
            )
            mark_handoff(from_number)
            return {"status": "handoff"}

        # Generate reply from templates
        reply_text = get_template(intent, state)

        # Simple fallback (no import from reply_engine)
        if not reply_text:
            reply_text = (
                "Thanks for reaching out.\n\n"
                "Please share:\n"
                "• Location you are interested in\n"
                "• Budget range (in lakh)\n"
                "• Plot or Flat\n\n"
                "I will guide you better after this."
            )

        # Send reply
        send_whatsapp_message(from_number, reply_text)

        return {"status": "received"}

    except Exception:
        print("❌ WhatsApp webhook error")
        traceback.print_exc()
        return {"status": "error"}

