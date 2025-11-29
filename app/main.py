from fastapi import FastAPI
from app.brain_loader import load_brain

# ✅ Explicit WhatsApp router import
from app.whatsapp.routes import router as whatsapp_router

COUNTERS, SCORING = load_brain()
print("✅ EstatePilot brain loaded:", COUNTERS.keys())

app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

# ✅ Mount WhatsApp explicitly
app.include_router(whatsapp_router)

@app.get("/health")
def health():
    return {"status": "ok"}
