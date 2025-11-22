from fastapi import APIRouter, Request
from app.leads.service import create_lead
from app.whatsapp.flow import process_message

router = APIRouter(prefix="/whatsapp")

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    # Check message exists
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
    except:
        return {"status": "ignored"}
    
    phone = message["from"]
    text = message["text"]["body"]
    
    response = process_message(phone, text)
    
    # Return empty 200 to WhatsApp
    return {"status": "received", "response": response}
