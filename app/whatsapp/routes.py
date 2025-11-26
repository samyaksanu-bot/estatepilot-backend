from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


# ✅ Webhook verification (GET)
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# ✅ Incoming WhatsApp messages (POST)
@router.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()

    # 🚨 IMPORTANT: always log payload
    print("📩 Incoming WhatsApp Message:")
    print(json.dumps(payload, indent=2))

    return {"status": "received"}

