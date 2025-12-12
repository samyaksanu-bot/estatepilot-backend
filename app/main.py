from fastapi import FastAPI

# Core boot logic
from app.brain_loader import load_brain
from app.context import COUNTERS, SCORING

# Routers
from app.whatsapp.routes import router as whatsapp_router
from app.campaign_engine.routes import router as campaign_router

# TEMP TEST ROUTE
from app.campaign_engine.test_route import router as test_route
app.include_router(test_route)

# --------------------------------------------------
# LOAD BRAIN ON STARTUP
# --------------------------------------------------
loaded_counters, loaded_scoring = load_brain()
COUNTERS.update(loaded_counters)
SCORING.update(loaded_scoring)

print("✅ Brain loaded:", list(COUNTERS.keys()))
print("✅ EstatePilot backend booting")


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)


# --------------------------------------------------
# REGISTER ROUTERS
# --------------------------------------------------
app.include_router(whatsapp_router)
app.include_router(campaign_router)


# --------------------------------------------------
# HEALTH CHECK (RENDER USES THIS)
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
