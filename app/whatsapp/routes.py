# app/whatsapp/routes.py

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import json
import os

from app.whatsapp.sender import send_whatsapp_message
from app.state import get_state
from app.reply_engine import generate_reply

router = APIRouter(prefix="/whatsapp")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))
    return PlainTextResponse("Verification failed", status_code=403)


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

        # Prevent spam after handoff
        if state.get("handoff_done"):
            return {"status": "handoff_active"}

        reply = generate_reply(text, state)

        if reply:
            send_whatsapp_message(
                to_number=from_number,
                message=reply
            )

        return {"status": "received"}

    except Exception as e:
        print("❌ WhatsApp error:", str(e))
        return {"status": "error"}
