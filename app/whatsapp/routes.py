from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("MODE:", mode)
    print("TOKEN FROM META:", token)
    print("TOKEN FROM ENV:", VERIFY_TOKEN)
    print("CHALLENGE:", challenge)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)

