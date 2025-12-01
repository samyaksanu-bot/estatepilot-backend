from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os, json

from app.whatsapp.sender import send_whatsapp_message
from app.state import get_state
from app.reply_engine import generate_reply

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# --------------------------------------------------
# WEBHOOK VERIFY
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
# INCOMING MESSAGES
# --------------------------------------------------
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
        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        state = get_state(from_number)
        reply = generate_reply(text, state)

        if reply:
            send_whatsapp_message(from_number, reply)

    except Exception as e:
        print("❌ Error processing WhatsApp message:", str(e))

    return {"status": "received"}

