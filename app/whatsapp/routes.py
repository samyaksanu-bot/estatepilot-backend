from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os

router = APIRouter(
    prefix="/whatsapp",   # this makes the full path /whatsapp/...
    tags=["whatsapp"],
)

# This must match the env variable we will set on Render
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    GET webhook used by Meta to VERIFY your endpoint.
    It must:
    - check hub.mode == 'subscribe'
    - check hub.verify_token == VERIFY_TOKEN
    - return hub.challenge with status 200
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        # Return the challenge as plain text
        return PlainTextResponse(content=challenge, status_code=200)

    # If token or mode is wrong, return 403
    return PlainTextResponse(content="Verification failed", status_code=403)


@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    POST webhook used when WhatsApp sends actual messages or status updates.
    For now we just log the body and return 200.
    """
    body = await request.json()
    print("INCOMING WHATSAPP WEBHOOK:", body)
    return {"status": "received"}
