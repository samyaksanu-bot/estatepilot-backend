from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

from app.whatsapp.sender import send_whatsapp_message

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# -----------------------------------------------------
# 1. WHATSAPP WEBHOOK VERIFICATION (GET)
# -----------------------------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)

# -----------------------------------------------------
# 2. INCOMING WHATSAPP MESSAGES (POST)
# -----------------------------------------------------
# ✅ Incoming WhatsApp messages (POST)
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

        # ✅ Ignore delivery/read/status events
        if "messages" not in value:
            print("ℹ️ Non-message event received. Ignored.")
            return {"status": "ignored"}

        message = value["messages"][0]

        from_number = message["from"]
        text = message["text"]["body"]

        reply = f"✅ EstatePilot is live.\nYou said:\n{text}"

        send_whatsapp_message(
            to_number=from_number,
            text=reply
        )

    except Exception as e:
        print("❌ Error processing message:", str(e))

    return {"status": "received"}
