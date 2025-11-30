from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

# ✅ WhatsApp sender
from app.whatsapp.sender import send_whatsapp_message

# ✅ State manager
from app.state import get_state

# ✅ LLM reply engine
from app.reply_engine import generate_reply

from app.lead_store import save_lead

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# --------------------------------------------------
# ✅ WhatsApp Webhook Verification (GET)
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
# ✅ Incoming WhatsApp Messages (POST)
# --------------------------------------------------
@router.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()
    print("📩 Incoming payload:")
    print(json.dumps(payload, indent=2))

    try:
        entry = payload.get("entry", [])
        if not entry:
            return {"status": "ignored"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ignored"}

        value = changes[0].get("value", {})

        # Ignore delivery/read receipts
        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        # ✅ Load user state
        state = get_state(from_number)

        # ✅ Generate AI reply
        reply = generate_reply(text, state)

        # ✅ Send only if reply exists
        if reply:
            send_whatsapp_message(from_number, reply)

# ✅ HUMAN HANDOFF LOGIC (ADD HERE)
if state.get("handoff_done") and not state.get("notified"):
    save_lead(from_number, state)
    state["notified"] = True
    print("📞 Human handoff required for:", from_number)
    
    except Exception as e:
        print("❌ Error processing WhatsApp message:", str(e))

    return {"status": "received"}

