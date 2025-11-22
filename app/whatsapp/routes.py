from fastapi import APIRouter
from app.whatsapp.sender import send_whatsapp_message

router = APIRouter(prefix="/whatsapp")

@router.post("/send")
def send_msg(payload: dict):
    return send_whatsapp_message(payload["to"], payload["message"])
