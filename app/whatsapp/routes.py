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

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))

    return PlainTextResponse("Verification failed", status_code=403)


# ✅ Incoming WhatsApp messages (POST)
@router.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()

    # LOG ONLY (no business logic yet)
    print("✅ Incoming WhatsApp Payload:")
    print(json.dumps(payload, indent=2))

    return {"status": "received"}
