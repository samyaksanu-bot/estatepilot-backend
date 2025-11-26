from fastapi import FastAPI
from app.whatsapp.routes import router as whatsapp_router

app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "OK"}

# ✅ Explicitly mount WhatsApp router
app.include_router(whatsapp_router)
