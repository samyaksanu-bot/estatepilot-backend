from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import traceback
import os

from app.whatsapp.sender import send_whatsapp_message
from app.intent_engine import detect_intent
from app.template_engine import get_template
from app.reply_engine import fallback_reply
from app.state import (
    get_state,
    update_state_with_intent,
    mark_handoff
)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "verify_token")


# --------------------------------------------------
# META WEBHOOK VERIFICATION
# --------------------------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))

    return PlainTextResponse("Verification failed", status_code=403)


# --------------------------------------------------
# INCOMING WHATSAPP MESSAGE
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
        user_text = message.get("text", {}).get("body", "").strip().lower()
        message_id = message.get("id")

        state = get_state(from_number)

        if state.get("last_message_id") == message_id:
            return {"status": "duplicate"}

        state["last_message_id"] = message_id

        if state.get("handoff_done"):
            return {"status": "agent_handling"}

        intent = detect_intent(user_text)
        state = update_state_with_intent(from_number, intent)

        if state.get("rank") == "hot":
            send_whatsapp_message(
                from_number,
                "✅ Our advisor will call you shortly to confirm details."
            )
            mark_handoff(from_number)
            return {"status": "handoff"}

        reply = get_template(intent, state) or fallback_reply(user_text)
        send_whatsapp_message(from_number, reply)

        return {"status": "received"}

    except Exception:
        traceback.print_exc()
        return {"status": "error"}
