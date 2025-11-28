from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os
import json

from app.client_configs.loader import load_client_config

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

# ✅ Webhook verification (Meta)
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))

    return PlainTextResponse("Verification failed", status_code=403)


# ✅ Incoming WhatsApp messages
@router.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()

    print("📩 Incoming WhatsApp payload:")
    print(json.dumps(payload, indent=2))

    # TEMP: single client (we scale later)
    client_id = "ojas_builders"
    config = load_client_config(client_id)

    # SIMPLE rule engine (no AI yet)
    greeting = config["bot_rules"]["greeting"]

    # ⛔ for now: just log response intent
    print("🤖 Bot would reply with:", greeting)

    return {"status": "received"}
