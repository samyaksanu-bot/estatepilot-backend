from fastapi import FastAPI

from app.brain_loader import load_brain
from app.context import COUNTERS, SCORING


# ✅ Load brain first (this part is OK)
loaded_counters, loaded_scoring = load_brain()
COUNTERS.update(loaded_counters)
SCORING.update(loaded_scoring)

print("✅ Brain loaded:", list(COUNTERS.keys()))


# ✅ Create FastAPI app EARLY
app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

print("✅ EstatePilot backend booting")


# ✅ Import routers ONLY AFTER app exists
from app.whatsapp.routes import router as whatsapp_router


# ✅ Register routers
app.include_router(whatsapp_router)


# ✅ Health check
@app.get("/health")
def health():
    return {"status": "ok"}
