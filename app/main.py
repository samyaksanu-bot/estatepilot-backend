from fastapi import FastAPI

# Core boot logic
from app.brain_loader import load_brain
from app.context import COUNTERS, SCORING

# Routers
from app.whatsapp.routes import router as whatsapp_router
from app.campaign_engine.routes import router as campaign_router


# --------------------------------------------------
# LOAD BRAIN ON STARTUP
# --------------------------------------------------
loaded_counters, loaded_scoring = load_brain()
COUNTERS.update(loaded_counters)
SCORING.update(loaded_scoring)

print("✅ Brain loaded:", list(COUNTERS.keys()))
print("✅ EstatePilot backend booting")


# ---------------------

