from fastapi import FastAPI
from app.brain_loader import load_brain
from app.context import COUNTERS, SCORING
from app.whatsapp.routes import router as whatsapp_router

# Load brain at startup
loaded_counters, loaded_scoring = load_brain()
COUNTERS.update(loaded_counters)
SCORING.update(loaded_scoring)

print("✅ Brain loaded:", COUNTERS.keys())

app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

# Register routers
app.include_router(whatsapp_router)

@app.get("/health")
def health():
    return {"status": "ok"}
