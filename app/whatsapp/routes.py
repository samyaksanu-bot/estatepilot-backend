from fastapi import APIRouter, Request

router = APIRouter()

VERIFY_TOKEN = "estatepilot123"

@router.get("/whatsapp/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"status": "error", "message": "Verification failed"}

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    print("Incoming WhatsApp message:", data)
    return {"status": "received"}
